from typing import Dict
from .CleaningRecord import CleaningRecord
from .get_webdriver import get_webdriver
from .login_airbnb import login_airbnb
from .get_google_ss_credentials import get_google_ss_credentials
from .get_google_ss_header_dict import get_google_ss_header_dict
from .get_google_ss_cleaning_records import get_google_ss_cleaning_records
from .get_gcal_entries import get_gcal_entries
from .rm_google_ss_rows import rm_google_ss_rows
from .add_google_ss_rows import add_google_ss_rows
from .sort_google_ss_by_column import sort_google_ss_by_column
from .get_twilio_client import get_twilio_client
from .get_todoist_api import get_todoist_api
from .get_todoist_project_id import get_todoist_project_id


def process_ab_listing(browser_dir: str, listing: Dict, secrets: Dict):

    driver = None

    try:
        # start notice
        print(f"starting listing {listing['name']}")

        # get previous crs from google spreadsheet
        google_cred = get_google_ss_credentials(secrets['google_sa'])

        google_ss_header_dict = get_google_ss_header_dict(
            credentials=google_cred,
            ss_id=listing['spreadsheet_id'],
            ss_name=listing['spreadsheet_sheet_name']
        )

        prev_crs = get_google_ss_cleaning_records(
            credentials=google_cred,
            ss_id=listing['spreadsheet_id'],
            ss_sheet_name=listing['spreadsheet_sheet_name'],
            ss_header_dict=google_ss_header_dict,
            listing_name=listing['name'],
            listing_type=listing['type']
        )

        # get new crs from google calendar
        # update each cr with info from airbnb and google ai
        # add +1 to the qty_to_process specified in listings.json
        # so we can update each cr with info from the next cr
        gcal_entries = get_gcal_entries(
            listing['url'],
            listing['type'],
            listing['qty_to_process'] + 1
        )

        driver = get_webdriver(browser_dir)

        abuser, abpass = secrets['airbnb_userpass'].split(':')
        login_airbnb(driver, abuser, abpass)

        new_crs = []
        for i in range(len(gcal_entries)):
            cr = CleaningRecord.from_gcal_ab_reservation(
                gcal_entries[i],
                listing['name'],
                listing['type'],
                listing['default_cleaning_fee'],
                listing['laundry']
            )

            cr.update_with_selenium(driver)

            cr.update_with_google_ai(
                secrets['gemini_api_key'],
                listing['guests'],
                listing['beds'],
                listing['pnp_beds']
            )

            new_crs.append(cr)

        for i in range(len(new_crs) - 1):
            next_cr = new_crs[i + 1]
            new_crs[i].update_with_next_cr(next_cr)

        _ = new_crs.pop()

        # delete prev_crs from ss
        prev_crs_indexes = []
        for cr in prev_crs:
            prev_crs_indexes.append(cr.spreadsheet_index)

        if len(prev_crs_indexes) > 0:
            rm_google_ss_rows(
                credentials=google_cred,
                ss_id=listing['spreadsheet_id'],
                ss_sheet_name=listing['spreadsheet_sheet_name'],
                ss_sheet_id=listing['spreadsheet_sheet_id'],
                indexes=prev_crs_indexes
            )

        # add new_crs to ss
        ssrows = []
        for cr in new_crs:
            ssrow = cr.to_ssrow(google_ss_header_dict)
            ssrows.append(ssrow)

        if len(ssrows) > 0:
            add_google_ss_rows(
                credentials=google_cred,
                ss_id=listing['spreadsheet_id'],
                ss_sheet_name=listing['spreadsheet_sheet_name'],
                values=ssrows
            )

        # sort spreadsheet
        sort_google_ss_by_column(
            credentials=google_cred,
            ss_id=listing['spreadsheet_id'],
            ss_sheet_id=listing['spreadsheet_sheet_id'],
            sort_column=google_ss_header_dict['cleaning_date']
        )

        # load twilio/todoist
        # twilio is used for sms reminders that are sent to the cleaner
        # todoist is used for tasks for the property manager
        tw_client = get_twilio_client(secrets['twilio']['client'])
        td_api = get_todoist_api(secrets['todoist_api_key'])
        td_pid = get_todoist_project_id(
            project_name=listing['todoist_project_name'],
            api=td_api
        )

        # send sms reminders/todoist tasks for each cr with cleaning date tomorrow
        for cr in new_crs:
            if cr.cleaning_is_tomorrow():
                cr.send_cleaning_reminder_sms(
                    tw_client=tw_client,
                    tw_from_number=secrets['twilio']['from_number'],
                    tw_to_number=secrets['twilio']['to_number'],
                    spreadsheet_bitly_url=listing['spreadsheet_bitly_url'],
                    checklist_bitly_url=listing['checklist_bitly_url']
                )
                cr.new_pay_reminder_task(
                    td_api=td_api,
                    td_project_id=td_pid
                )
                cr.new_check_airbnb_task(
                    td_api=td_api,
                    td_project_id=td_pid
                )

            if cr.check_in_is_today():
                cr.new_airbnb_parking_pass_task(
                    td_api=td_api,
                    td_project_id=td_pid
                )

        # alert on records added
        prev_crs_ids = [prev_cr.id for prev_cr in prev_crs]
        for cr in new_crs:
            if (
                cr.id not in prev_crs_ids and
                cr.cleaning_is_within(days=listing['days_addrm_notice'])
            ):
                cr.send_date_added_sms(
                    tw_client=tw_client,
                    tw_from_number=secrets['twilio']['from_number'],
                    tw_to_number=secrets['twilio']['to_number'],
                    spreadsheet_bitly_url=listing['spreadsheet_bitly_url']
                )

        # alert on records removed
        new_crs_ids = [new_cr.id for new_cr in new_crs]
        for cr in prev_crs:
            if (
                cr.id not in new_crs_ids and
                cr.cleaning_is_within(days=listing['days_addrm_notice'])
            ):
                cr.send_date_removed_sms(
                    tw_client=tw_client,
                    tw_from_number=secrets['twilio']['from_number'],
                    tw_to_number=secrets['twilio']['to_number'],
                    spreadsheet_bitly_url=listing['spreadsheet_bitly_url']
                )

        # completion notice
        print(f"completed listing {listing['name']}")

    except Exception as e:
        print(f"error processing listing {listing['name']}: {e}")

    finally:
        if driver:
            driver.quit()
