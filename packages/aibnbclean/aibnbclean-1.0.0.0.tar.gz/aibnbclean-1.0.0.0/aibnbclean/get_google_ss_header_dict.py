from googleapiclient.discovery import build
from google.oauth2 import service_account

def get_google_ss_header_dict(
        credentials: service_account.Credentials,
        ss_id: str,
        ss_name: str
    ):

    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()

    result = (
        sheet.values()
        .get(spreadsheetId=ss_id, range=f"{ss_name}!A1:Z1").execute()
    )

    values = result.get("values", [])

    header_dict = {}

    for i, v in enumerate(values[0]):
        header_dict[v] = i

    return header_dict
