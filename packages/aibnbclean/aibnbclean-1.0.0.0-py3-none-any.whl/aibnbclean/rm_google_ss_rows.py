from typing import List
from google.oauth2 import service_account
from googleapiclient.discovery import build
from .add_google_ss_rows import add_google_ss_rows

def rm_google_ss_rows(
        credentials: service_account.Credentials,
        ss_id: str,
        ss_sheet_name: str,
        ss_sheet_id: int,
        indexes: List[int]
    ):

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    #api will not let you delete all non-frozen rows,
    #so we append an empty row if necessary and then delete
    result = (
        sheet.values().get(spreadsheetId=ss_id,range=f"{ss_sheet_name}!A2:Z").execute()
    )
    existing_rows = result.get("values", [])

    if len(existing_rows) == len(indexes):
        add_google_ss_rows(
            credentials = credentials,
            ss_id = ss_id,
            ss_sheet_name = ss_sheet_name,
            values = [['']]
        )

    # delete starting from the bottom of the spreadsheet
    # so we ensure the startIndex/endIndex is valid
    indexes.reverse()

    requests = []

    for index in indexes:
        request = {
            'deleteDimension': {
                'range': {
                    'sheetId': ss_sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': index,
                    'endIndex': index + 1  # Exclusive end index
                }
            }
        }
        requests.append(request)

    _ = sheet.batchUpdate(
        spreadsheetId=ss_id,
        body={'requests': requests}
    ).execute()
