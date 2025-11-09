from googleapiclient.discovery import build
from google.oauth2 import service_account


def add_google_ss_rows(
        credentials: service_account.Credentials,
        ss_id: str,
        ss_sheet_name: str,
        values: list
    ):

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    body = {
        'values': values
    }

    # when the valueInputOption is set to USER_ENTERED the values are parsed
    # as if they were manually typed in and get converted to the correct type

    _ = sheet.values().append(
        spreadsheetId=ss_id,
        range=f"{ss_sheet_name}!A2:Z",
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
