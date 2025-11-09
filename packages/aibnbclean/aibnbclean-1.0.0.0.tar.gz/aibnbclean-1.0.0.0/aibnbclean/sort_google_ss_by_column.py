from googleapiclient.discovery import build
from google.oauth2 import service_account


def sort_google_ss_by_column(
        credentials: service_account.Credentials,
        ss_id: str,
        ss_sheet_id: int,
        sort_column: int
    ):

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    requests = []

    request = {
        'sortRange': {
            'range': {
                'sheetId': ss_sheet_id,
                'startRowIndex': 1
            },
            'sortSpecs': [
                {
                    'dimensionIndex': sort_column,
                    'sortOrder': 'ASCENDING'
                }
            ]
        }
    }

    requests.append(request)

    _ = sheet.batchUpdate(
        spreadsheetId=ss_id,
        body={'requests': requests}
    ).execute()
