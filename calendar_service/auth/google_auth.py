import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from config import settings
from security import decrypt_data
import models
import crud   
from sqlalchemy.orm import Session 

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


def get_google_service(account_from_db: models.ConnectedAccount, db: Session):

    try:
        creds_json = decrypt_data(account_from_db.encrypted_credentials)
        creds_dict = json.loads(creds_json)
        
        credentials = Credentials.from_authorized_user_info(creds_dict, settings.SCOPES)

        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request
            print("Token do Google expirado, tentando renovar...")
            credentials.refresh(Request())

            new_creds_to_save = {
                'token': credentials.token,
                'refresh_token': credentials.refresh_token,
                'token_uri': credentials.token_uri,
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'scopes': credentials.scopes
            }

            crud.update_account_credentials(db, account=account_from_db, new_credentials=new_creds_to_save)
            print("Token do Google renovado e salvo no banco de dados.")

        service = build("calendar", "v3", credentials=credentials)
        return service
    
    except Exception as e:
        print(f"Erro ao criar o serviço do Google: {e}")
        return None