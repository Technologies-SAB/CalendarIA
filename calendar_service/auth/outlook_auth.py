from O365 import Account
from config import settings

SCOPES = ['Calendars.ReadWrite']

temp_auth_flow_storage = {}

def get_outlook_account_object():
    credentials = (settings.OUTLOOK_CLIENT_ID, settings.OUTLOOK_CLIENT_SECRET)
    if not all(credentials):
        raise ValueError("Credenciais do Outlook não definidas no ambiente.")
    return Account(credentials)

def get_outlook_auth_url_and_flow(chat_id: str) -> str:
    account = get_outlook_account_object()
    
    flow = account.con.msal_client.initiate_auth_code_flow(
        scopes=SCOPES,
        redirect_uri=settings.OUTLOOK_REDIRECT_URI,
        prompt='consent'
    )

    temp_auth_flow_storage[chat_id] = flow
    
    return flow['auth_uri']