from googleapiclient.discovery import build
from google.oauth2 import service_account
from typing import Dict, List
from .CleaningRecord import CleaningRecord

def get_google_ss_cleaning_records(
        credentials: service_account.Credentials,
        ss_id: str,
        ss_sheet_name: str,
        ss_header_dict: Dict,
        listing_name: str,
        listing_type: str
    ) -> List[CleaningRecord]:

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    result = (
        sheet.values().get(spreadsheetId=ss_id,range=f"{ss_sheet_name}!A2:Z").execute()
    )

    rows = result.get("values", [])

    #sheets api by default omits trailing empty cells in each row
    #so we need to pad each row with empty values to match the header
    padded_rows = []
    for row in rows:
        while len(row) < len(ss_header_dict):
            row.append(None)
        padded_rows.append(row)

    crs = []
    for i, row in enumerate(padded_rows):
        if (
            row[ss_header_dict['listing_name']] == listing_name and
            row[ss_header_dict['listing_type']] == listing_type
        ):
            cr = CleaningRecord.from_ssrow(
                (i+1), #rows are 1 indexed
                row,
                ss_header_dict
            )
            crs.append(cr)

    return crs
