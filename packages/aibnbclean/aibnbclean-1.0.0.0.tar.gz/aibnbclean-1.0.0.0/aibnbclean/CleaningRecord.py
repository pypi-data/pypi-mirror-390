import re
import hashlib
from unicodedata import normalize
from io import StringIO
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from .GoogleAiResponse import GoogleAiResponse
from google import genai
from twilio.rest import Client


class CleaningRecord:
    def __init__(
        self,
        id: str,
        reservation_url: Optional[str],
        message_url: Optional[str],
        message_text: Optional[str],
        listing_name: str,
        listing_type: str,
        spreadsheet_index: Optional[int],
        guest_name: Optional[str],
        check_in_date: Optional[datetime],
        cleaning_date: datetime,  # aka check_out_date
        guests_qty: Optional[int],
        beds_qty: Optional[int],
        pnp_beds_qty: Optional[int],
        cleaning_fee: Optional[int],
        laundry: Optional[str],
        car_make: Optional[str],
        car_model: Optional[str],
        car_color: Optional[str],
        car_license_number: Optional[str],
        car_license_state: Optional[str],
        phone_last_4_digits: Optional[str],
        next_id: Optional[str],
        next_check_in_date: Optional[datetime],
        next_cleaning_date: Optional[datetime],
        next_guest_name: Optional[str],
        next_guests_qty: Optional[int],
        next_beds_qty: Optional[int],
        next_pnp_beds_qty: Optional[int],
        next_car_make: Optional[str],
        next_car_model: Optional[str],
        next_car_color: Optional[str],
        next_car_license_number: Optional[str],
        next_car_license_state: Optional[str],
        next_phone_last_4_digits: Optional[str]
    ):
        self.id = id
        self.reservation_url = reservation_url
        self.message_url = message_url
        self.message_text = message_text
        self.listing_name = listing_name
        self.listing_type = listing_type
        self.spreadsheet_index = spreadsheet_index
        self.guest_name = guest_name
        self.check_in_date = check_in_date
        self.cleaning_date = cleaning_date
        self.guests_qty = guests_qty
        self.beds_qty = beds_qty
        self.pnp_beds_qty = pnp_beds_qty
        self.cleaning_fee = cleaning_fee
        self.laundry = laundry
        self.car_make = car_make
        self.car_model = car_model
        self.car_color = car_color
        self.car_license_number = car_license_number
        self.car_license_state = car_license_state
        self.phone_last_4_digits = phone_last_4_digits
        self.next_id = next_id
        self.next_check_in_date = next_check_in_date
        self.next_cleaning_date = next_cleaning_date
        self.next_guest_name = next_guest_name
        self.next_guests_qty = next_guests_qty
        self.next_beds_qty = next_beds_qty
        self.next_pnp_beds_qty = next_pnp_beds_qty
        self.next_car_make = next_car_make
        self.next_car_model = next_car_model
        self.next_car_color = next_car_color
        self.next_car_license_number = next_car_license_number
        self.next_car_license_state = next_car_license_state
        self.next_phone_last_4_digits = next_phone_last_4_digits

    @classmethod
    def from_ssrow(cls, index, row, header_dict) -> 'CleaningRecord':

        cleaning_date = row[header_dict['cleaning_date']]
        if isinstance(cleaning_date, str):
            cleaning_date = datetime.strptime(
                row[header_dict['cleaning_date']], '%m/%d/%Y'
            )
        elif isinstance(cleaning_date, date):
            cleaning_date = datetime.combine(
                cleaning_date,
                datetime.min.time()
            )

        next_check_in_date = row[header_dict['next_check_in_date']]
        if isinstance(next_check_in_date, str):
            next_check_in_date = datetime.strptime(
                row[header_dict['next_check_in_date']], '%m/%d/%Y'
            )
        elif isinstance(next_check_in_date, date):
            next_check_in_date = datetime.combine(
                next_check_in_date,
                datetime.min.time()
            )

        return cls(
            id=row[header_dict['id']],
            reservation_url=None,
            message_url=None,
            message_text=None,
            listing_name=row[header_dict['listing_name']],
            listing_type=row[header_dict['listing_type']],
            spreadsheet_index=index,
            guest_name=None,
            check_in_date=None,
            cleaning_date=cleaning_date,
            guests_qty=None,
            beds_qty=None,
            pnp_beds_qty=None,
            cleaning_fee=row[header_dict['cleaning_fee']],
            laundry=row[header_dict['laundry']],
            car_make=None,
            car_model=None,
            car_color=None,
            car_license_number=None,
            car_license_state=None,
            phone_last_4_digits=None,
            next_id=None,
            next_check_in_date=next_check_in_date,
            next_cleaning_date=None,
            next_guest_name=None,
            next_guests_qty=row[header_dict['next_guests_qty']],
            next_beds_qty=row[header_dict['next_beds_qty']],
            next_pnp_beds_qty=row[header_dict['next_pnp_beds_qty']],
            next_car_make=row[header_dict['next_car_make']],
            next_car_model=row[header_dict['next_car_model']],
            next_car_color=row[header_dict['next_car_color']],
            next_car_license_number=row[header_dict['next_car_license_number']],
            next_car_license_state=row[header_dict['next_car_license_state']],
            next_phone_last_4_digits=row[header_dict['next_phone_last_4_digits']]
        )

    def to_ssrow(self, header_dict) -> List[str]:
        """
        method to convert CleaningRecord object to a list of strings
        in the order of the spreadsheet header row
        """
        sorted_headers = sorted(header_dict, key=header_dict.get)

        output = []

        for header in sorted_headers:
            value = getattr(self, header)
            if isinstance(value, date):
                output.append(value.strftime("%m/%d/%Y"))
            elif isinstance(value, str):
                # prefix single quote so we make sure spreadsheet interprets it as a string
                output.append(f"'{value}")
            else:
                output.append(value)

        return output

    @classmethod
    def from_gcal_ab_reservation(
        cls,
        gc_event,
        listing_name: str,
        listing_type: str,
        default_cleaning_fee: int,
        laundry: str
    ) -> 'CleaningRecord':

        split_desc = gc_event['DESCRIPTION'].split('\n')

        check_in_date = gc_event.DTSTART
        if isinstance(check_in_date, date):
            check_in_date = datetime.combine(
                check_in_date,
                datetime.min.time()
            )

        cleaning_date = gc_event.DTEND
        if isinstance(cleaning_date, date):
            cleaning_date = datetime.combine(
                cleaning_date,
                datetime.min.time()
            )

        return cls(
            id=split_desc[0].split('/')[-1].strip(),
            reservation_url=split_desc[0].split(
                'Reservation URL: ')[1].strip(),
            message_url=None,
            message_text=None,
            listing_name=listing_name,
            listing_type=listing_type,
            spreadsheet_index=None,
            guest_name=None,
            check_in_date=check_in_date,
            cleaning_date=cleaning_date,
            guests_qty=None,
            beds_qty=None,
            pnp_beds_qty=None,
            cleaning_fee=default_cleaning_fee,
            laundry=laundry,
            car_make=None,
            car_model=None,
            car_color=None,
            car_license_number=None,
            car_license_state=None,
            phone_last_4_digits=split_desc[1].split(': ')[-1].strip(),
            next_id=None,
            next_check_in_date=None,
            next_cleaning_date=None,
            next_guest_name=None,
            next_guests_qty=None,
            next_beds_qty=None,
            next_pnp_beds_qty=None,
            next_car_make=None,
            next_car_model=None,
            next_car_color=None,
            next_car_license_number=None,
            next_car_license_state=None,
            next_phone_last_4_digits=None
        )

    @classmethod
    def from_gcal_home_cleaning(
        cls,
        gc_event,
        listing_name: str,
        listing_type: str,
        default_cleaning_fee: int,
        laundry: str
    ) -> 'CleaningRecord':

        # generate a 10 character code for the id so it's similar to
        # the airbnb reservation id
        id_p0 = gc_event['UID'].split('@')[0].strip()
        id_p1 = gc_event.DTSTART.strftime("%m/%d/%Y")
        id_p2 = gc_event.DTEND.strftime("%m/%d/%Y")
        id_str = id_p0 + id_p1 + id_p2

        cleaning_date = gc_event.DTEND
        if isinstance(cleaning_date, date):
            cleaning_date = datetime.combine(
                cleaning_date,
                datetime.min.time()
            )

        return cls(
            id=hashlib.md5(id_str.encode('utf-8')).hexdigest()[0:9].upper(),
            reservation_url=None,
            message_url=None,
            message_text=None,
            listing_name=listing_name,
            listing_type=listing_type,
            spreadsheet_index=None,
            guest_name=None,
            check_in_date=None,
            cleaning_date=cleaning_date,
            guests_qty=None,
            beds_qty=None,
            pnp_beds_qty=None,
            cleaning_fee=default_cleaning_fee,
            laundry=laundry,
            car_make=None,
            car_model=None,
            car_color=None,
            car_license_number=None,
            car_license_state=None,
            phone_last_4_digits=None,
            next_id=None,
            next_check_in_date=None,
            next_cleaning_date=None,
            next_guest_name=None,
            next_guests_qty=None,
            next_beds_qty=None,
            next_pnp_beds_qty=None,
            next_car_make=None,
            next_car_model=None,
            next_car_color=None,
            next_car_license_number=None,
            next_car_license_state=None,
            next_phone_last_4_digits=None
        )

    def update_with_next_cr(self, next_cr: 'CleaningRecord'):
        self.next_id = next_cr.id
        self.next_check_in_date = next_cr.check_in_date
        self.next_cleaning_date = next_cr.cleaning_date
        self.next_guest_name = next_cr.guest_name
        self.next_guests_qty = next_cr.guests_qty
        self.next_beds_qty = next_cr.beds_qty
        self.next_pnp_beds_qty = next_cr.pnp_beds_qty
        self.next_car_make = next_cr.car_make
        self.next_car_model = next_cr.car_model
        self.next_car_color = next_cr.car_color
        self.next_car_license_number = next_cr.car_license_number
        self.next_car_license_state = next_cr.car_license_state
        self.next_phone_last_4_digits = next_cr.phone_last_4_digits

    def _set_message_url(self, driver: webdriver.Chrome):
        if self.reservation_url is None:
            raise ValueError("reservation_url is required")

        if driver.current_url != self.reservation_url:
            driver.get(self.reservation_url)

        pattern = r"/hosting/p/inbox/folder/all/thread/\d+"
        match = re.search(pattern, driver.page_source)
        if match:
            self.message_url = "https://www.airbnb.com" + match.group(0)

    def _set_guest_name(self, driver: webdriver.Chrome):
        if self.reservation_url is None:
            raise ValueError("reservation_url is required")

        if driver.current_url != self.reservation_url:
            driver.get(self.reservation_url)

        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    '[data-testid="hrd-sbui-header-section"]'
                )
            )
        )
        header_section_txt = section.text.split('\n')
        self.guest_name = header_section_txt[1]

    def _set_guests_qty(self, driver: webdriver.Chrome):
        if self.reservation_url is None:
            raise ValueError("reservation_url is required")

        if driver.current_url != self.reservation_url:
            driver.get(self.reservation_url)

        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    '[data-testid="hrd-sbui-header-section"]'
                )
            )
        )

        header_section_txt = section.text.split('\n')

        for txt in header_section_txt:
            match = re.search(r"(\d+)\s+guests?", txt)
            if match:
                self.guests_qty = int(match.group(1))
                break

    def _set_cleaning_fee(self, driver: webdriver.Chrome):
        if self.reservation_url is None:
            raise ValueError("reservation_url is required")

        if driver.current_url != self.reservation_url:
            driver.get(self.reservation_url)

        section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    '[data-testid="hrd-sbui-payment-details-section"]'
                )
            )
        )

        section_txt = section.text.split('\n')

        for i in range(len(section_txt)):
            match = re.search("Cleaning", section_txt[i])
            if match:
                cln_fee_str = section_txt[i + 1].replace('$', '').split('.')[0]
                self.cleaning_fee = int(cln_fee_str)
                break

    def _set_message_text(self, driver: webdriver.Chrome):
        if self.message_url is None:
            return

        if driver.current_url != self.message_url:
            driver.get(self.message_url)

        buffer = StringIO()

        try:
            driver.get(self.message_url)

            message_list = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        '[data-testid="message-list"]'
                    )
                )
            )

            # only get the direct child div elements (not nested ones)
            direct_children = message_list.find_elements(
                By.XPATH,
                "./div"
            )

            for child in direct_children:
                child_text = child.text.strip()
                buffer.write(child_text)

            tmp = buffer.getvalue()
            tmp = normalize("NFKD", tmp)
            tmp = re.sub(r"\d{2}:\d{2}\n", " ", tmp)
            tmp = tmp.replace('\n', ' ')

            self.message_text = tmp

        finally:
            if buffer:
                buffer.close()

    def update_with_selenium(self, driver: webdriver.Chrome):
        try:
            self._set_message_url(driver)
            self._set_guest_name(driver)
            self._set_guests_qty(driver)
            self._set_cleaning_fee(driver)
            self._set_message_text(driver)
        except Exception as e:
            raise Exception(f"update_properties_with_selenium: {e}")

    def update_with_google_ai(self, api_key: str, guests: Dict, beds: Dict, pnp_beds: Dict):
        """
        example code
        https://ai.google.dev/gemini-api/docs/structured-output?lang=python
        """
        try:
            if self.message_text is None:
                raise Exception("message_text is required")

            client = genai.Client(api_key=api_key)

            contents = f"""
                Read the MessageText and return the following

                guests_qty
                    return an int to indicate the number of guests

                    minimum/default is {guests['min']} and
                    maximum is {guests['max']}

                    the booking indicates {self.guests_qty} guest(s) but this
                    might be inaccurate and there are actually more guests

                beds_qty
                    return an int to indicate the number of beds required

                    minimum/default is {beds['min']} and
                    maximum is {beds['max']}

                    conditions for 1 bed
                        1 guest or
                        2 guests that are partners

                    conditions for 2 beds
                        guest specifies they would like an extra bed or
                        3 or more guests or
                        2 guests that are not partners

                pnp_beds_qty
                    return an int to indicate the number of pack and play beds required

                    pack and play beds are for infants

                    minimum/default is {pnp_beds['min']} and
                    maximum is {pnp_beds['max']}

                    conditions for 1
                        guest specifies they would like it set up for them

                car_make
                    return the make of the car as a string,
                    examples: Subaru, Mitsubishi, Honda, Jeep, Chevrolet
                    return empty string if it cannot be found

                car_model
                    return the model of the car as a string
                    examples: Impreza, Civic, Cherokee, Bolt
                    return empty string if it cannot be found

                car_color
                    return the color of the car as a string
                    examples: blue, black, red, purple, silver
                    return empty string if it cannot be found

                car_license_number
                    return the license plate number as a string
                    return empty string if it cannot be found

                car_license_state
                    return as the 2 letter abbreviation for the state as a string
                    examples: MA, FL, VA, CA
                    return empty string if it cannot be found

                Message_Text
                {self.message_text}
            """

            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=contents,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': GoogleAiResponse,
                }
            )

            if type(response.parsed) is not GoogleAiResponse:
                raise Exception("did not return GoogleAiResponse schema")

            google_ai_response: GoogleAiResponse = response.parsed

            self.guests_qty = google_ai_response.guests_qty
            self.beds_qty = google_ai_response.beds_qty
            self.pnp_beds_qty = google_ai_response.pnp_beds_qty
            self.car_make = google_ai_response.car_make
            self.car_model = google_ai_response.car_model
            self.car_color = google_ai_response.car_color
            self.car_license_number = google_ai_response.car_license_number
            self.car_license_state = google_ai_response.car_license_state

        except Exception as e:
            raise Exception(f"update_properties_with_google_ai: {e}")

    def check_in_is_today(self) -> bool:
        # check_in_date should be datetime.datetime
        # today_datetime should be datetime.datetime
        today_datetime = datetime.combine(
            datetime.now().date(),
            datetime.min.time()
        )

        if (
            self.check_in_date is not None and
            self.check_in_date == today_datetime
        ):
            return True

        return False

    def cleaning_is_tomorrow(self) -> bool:
        # cleaning_date should be datetime.datetime
        # tomorrow_datetime should be datetime.datetime
        tomorrow_datetime = datetime.combine(
            (datetime.now() + timedelta(days=1)).date(),
            datetime.min.time()
        )

        if self.cleaning_date == tomorrow_datetime:
            return True

        return False

    def cleaning_is_within(self, days: int) -> bool:
        # make sure today has same timezone as self.cleaning_date for comparison
        if hasattr(self.cleaning_date, 'tzinfo') and self.cleaning_date.tzinfo is not None:
            today = datetime.now(self.cleaning_date.tzinfo)
        else:
            today = datetime.now()

        within = today + timedelta(days=days)

        if self.cleaning_date >= today and self.cleaning_date <= within:
            return True

        return False

    def send_date_added_sms(
        self,
        tw_client: Client,
        tw_from_number: str,
        tw_to_number: str,
        spreadsheet_bitly_url: str,
    ):
        cleaning_date = self.cleaning_date.strftime("%m/%d/%Y")

        text_body = f"""
Notification for {self.listing_name}
Cleaning Date added: {cleaning_date}
Cleaning Schedule (New Version): {spreadsheet_bitly_url}
Cleaning Schedule (Old Version): https://bit.ly/4428USu
"""
        tw_client.messages.create(
            to=tw_to_number,
            from_=tw_from_number,
            body=text_body
        )

    def send_date_removed_sms(
        self,
        tw_client: Client,
        tw_from_number: str,
        tw_to_number: str,
        spreadsheet_bitly_url: str
    ):
        cleaning_date = self.cleaning_date.strftime("%m/%d/%Y")
        text_body = f"""
Notification for {self.listing_name}
Cleaning Date removed: {cleaning_date}
Cleaning Schedule (New Version): {spreadsheet_bitly_url}
Cleaning Schedule (Old Version): https://bit.ly/4428USu
"""
        tw_client.messages.create(
            to=tw_to_number,
            from_=tw_from_number,
            body=text_body
        )

    def send_cleaning_reminder_sms(
        self,
        tw_client: Client,
        tw_from_number: str,
        tw_to_number: str,
        spreadsheet_bitly_url: str,
        checklist_bitly_url: str
    ):

        cleaning_date = self.cleaning_date.strftime("%m/%d/%Y")

        if self.listing_type == 'airbnb':
            # next_check_in_date
            if self.next_check_in_date is not None:
                next_check_in_date = self.next_check_in_date.strftime(
                    "%m/%d/%Y"
                )
            else:
                next_check_in_date = 'na'

            # guests_qty
            if self.next_guests_qty:
                next_guests_qty = str(self.next_guests_qty)
            else:
                next_guests_qty = 'na'

            # beds_qty
            if self.next_beds_qty:
                next_beds_qty = str(self.next_beds_qty)
            else:
                next_beds_qty = 'na'

            # send twilio text sms with cleaning info
            text_body = f"""
Notification for {self.listing_name}
Cleaning Date: {cleaning_date}
Check In Date: {next_check_in_date}
Guests: {next_guests_qty}, Beds: {next_beds_qty}
Cleaning Checklist: {checklist_bitly_url}
Cleaning Schedule (New Version): {spreadsheet_bitly_url}
Cleaning Schedule (Old Version): https://bit.ly/4428USu
"""

            tw_client.messages.create(
                to=tw_to_number,
                from_=tw_from_number,
                body=text_body
            )

        elif self.listing_type == "home":
            text_body = f"""
Notification for {self.listing_name}
Cleaning Date: {cleaning_date}
Cleaning Schedule (New Version): {spreadsheet_bitly_url}
Cleaning Schedule (Old Version): https://bit.ly/4428USu
"""

            tw_client.messages.create(
                to=tw_to_number,
                from_=tw_from_number,
                body=text_body
            )

    def new_pay_reminder_task(self, td_api, td_project_id):
        if self.cleaning_fee:
            cleaning_fee = str(self.cleaning_fee)
        else:
            cleaning_fee = 'na'

        td_api.add_task(
            project_id=td_project_id,
            content=f"pay cleaners {cleaning_fee} for {self.listing_name}",
            due_string="tomorrow 9am"
        )

    def new_check_airbnb_task(self, td_api, td_project_id):
        if self.listing_type != 'airbnb':
            return

        td_api.add_task(
            project_id=td_project_id,
            content=f"check airbnb {self.listing_name}",
            due_string="tomorrow 9am"
        )

    def new_airbnb_parking_pass_task(self, td_api, td_project_id):
        if self.listing_type != 'airbnb':
            return

        if self.check_in_date:
            check_in_date = self.check_in_date.strftime("%m/%d/%Y")
        else:
            check_in_date = 'na'

        if self.cleaning_date:
            cleaning_date = self.cleaning_date.strftime("%m/%d/%Y")
        else:
            cleaning_date = 'na'

        guest_name = getattr(self, "guest_name", 'na')

        car_make = getattr(self, "car_make", 'na')

        car_model = getattr(self, "car_model", 'na')

        car_color = getattr(self, "car_color", 'na')

        car_license_number = getattr(
            self, "car_license_number", 'na'
        )

        car_license_state = getattr(
            self, "car_license_state", 'na')

        td_api.add_task(
            project_id=td_project_id,
            content=f"""
Parking Info for {guest_name}
Car Make: {car_make}
Car Model: {car_model}
Car Color: {car_color}
Car License Number: {car_license_number}
Car License State: {car_license_state}
Parking Duration: {check_in_date} to {cleaning_date}
""",
            due_string="today 2pm"
        )
