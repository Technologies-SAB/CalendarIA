import msal
from config import settings

DOTNET_API_SCOPES = [f"api://{settings.OUTLOOK_CLIENT_ID}/.default"]

def get_dotnet_api_token() -> str:
    authority = f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}"
    
    msal_client = msal.ConfidentialClientApplication(
        client_id=settings.OUTLOOK_CLIENT_ID,
        client_credential=settings.OUTLOOK_CLIENT_SECRET,
        authority=authority
    )
    
    result = msal_client.acquire_token_for_client(scopes=DOTNET_API_SCOPES)
    
    if "access_token" not in result:
        error_details = result.get('error_description', 'Nenhum detalhe de erro retornado.')
        raise Exception(f"Não foi possível autenticar o serviço Python com a API .NET: {error_details}")
    
    return result['access_token']