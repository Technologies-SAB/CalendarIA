import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config import settings
from security import decrypt_data

# --- Funções de Autenticação e Callback ---

def get_google_auth_flow() -> Flow:
    """
    Cria e retorna o objeto de fluxo de autenticação do Google,
    configurado com as credenciais do ambiente.
    """
    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
            }
        },
        scopes=settings.SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )

def process_google_callback(authorization_response: str) -> dict:
    """
    Processa a URL de callback do Google, troca o código de autorização
    por tokens de acesso e refresh, e retorna as credenciais como um dicionário.
    
    :param authorization_response: A URL completa de callback recebida do Google.
    :return: Um dicionário com as credenciais prontas para serem salvas.
    """
    flow = get_google_auth_flow()
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = {
        'token': flow.credentials.token,
        'refresh_token': flow.credentials.refresh_token,
        'token_uri': flow.credentials.token_uri,
        'client_id': flow.credentials.client_id,
        'client_secret': flow.credentials.client_secret,
        'scopes': flow.credentials.scopes
    }
    return credentials

# --- Função para Criar um Cliente de Serviço Autenticado ---

def get_google_service(encrypted_credentials: str):
    """
    Recebe as credenciais criptografadas do banco de dados,
    descriptografa, cria um objeto de credenciais do Google,
    e retorna um objeto de serviço ('service') pronto para uso.

    :param encrypted_credentials: A string de credenciais criptografada vinda do DB.
    :return: Um objeto de serviço do Google Calendar API, ou None em caso de erro.
    """
    try:
        creds_json = decrypt_data(encrypted_credentials)
        creds_dict = json.loads(creds_json)
        
        credentials = Credentials.from_authorized_user_info(creds_dict, settings.SCOPES)

        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request
            credentials.refresh(Request())

        service = build("calendar", "v3", credentials=credentials)
        return service
    
    except Exception as e:
        print(f"Erro ao criar o serviço do Google: {e}")
        return None