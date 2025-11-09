from typing import Dict

from google.oauth2 import service_account


def get_google_ss_credentials(svc_account: Dict) -> service_account.Credentials:

    return service_account.Credentials.from_service_account_info(
        svc_account,
        scopes=['https://www.googleapis.com/auth/spreadsheets']
    )
