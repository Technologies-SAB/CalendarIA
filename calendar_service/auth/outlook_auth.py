from O365 import Account
from config import settings

SCOPES = ['Calendars.ReadWrite']

# Armazenamento temporário para o fluxo de autenticação
# Chave: chat_id do usuário, Valor: o dicionário de fluxo da msal
temp_auth_flow_storage = {}

def get_outlook_account_object():
    """Cria o objeto de conta da O365."""
    credentials = (settings.OUTLOOK_CLIENT_ID, settings.OUTLOOK_CLIENT_SECRET)
    if not all(credentials):
        raise ValueError("Credenciais do Outlook não definidas no ambiente.")
    return Account(credentials)

def get_outlook_auth_url_and_flow(chat_id: str) -> str:
    """
    Gera a URL de autorização e armazena o fluxo de autenticação
    associado ao chat_id para ser usado no callback.
    """
    account = get_outlook_account_object()
    
    # A biblioteca MSAL inicia um fluxo e o retorna como um dicionário
    flow = account.con.msal_client.initiate_auth_code_flow(
        scopes=SCOPES,
        redirect_uri=settings.OUTLOOK_REDIRECT_URI
    )

    # Armazenamos o fluxo inteiro, associado ao chat_id
    temp_auth_flow_storage[chat_id] = flow
    
    # A URL de autorização está dentro do dicionário do fluxo
    return flow['auth_uri']