import requests
from config import settings
import msal
import json

DOTNET_API_SCOPES = [f"api://{settings.OUTLOOK_CLIENT_ID}/.default"]

def get_dotnet_api_token():
    msal_client = msal.ConfidentialClientApplication(
        client_id=settings.OUTLOOK_CLIENT_ID,
        client_credential=settings.OUTLOOK_CLIENT_SECRET,
        authority="https://login.microsoftonline.com/common"
    )
    
    result = msal_client.acquire_token_for_client(scopes=DOTNET_API_SCOPES)
    if "error" in result:
        raise Exception(f"Falha ao obter token para a API .NET: {result.get('error_description')}")
    
    return result['access_token']

def agendar_outlook(account_from_db: models.ConnectedAccount, db: Session, data_str: str, hora_str: str, titulo: str, description: str):
    try:
        access_token = get_dotnet_api_token()
        
        payload = {
            "chatId": account_from_db.owner.chat_id,
            "titulo": titulo,
            "description": description,
            "data": data_str,
            "hora": hora_str
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "http://calendar-api-dotnet:8080/Calendar/agendar",
            headers=headers,
            json=payload
        )
        
        response.raise_for_status()
        
        return response.json()

    except Exception as e:
        logging.error(f"ERRO AO CHAMAR API .NET: {e}", exc_info=True)
        return {"status": "error", "message": f"Erro de comunicação com o serviço do Outlook: {e}"}