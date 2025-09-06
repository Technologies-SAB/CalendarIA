import datetime
import os.path
import logging

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_calendar_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", settings.SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", settings.SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        
    
    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        logging.error(f"Ocorreu um erro ao construir o serviço: {error}")
        return None
    
def agendar_google(data_str: str, hora_str: str, title: str, description: str):
    service = get_calendar_service

    if not service:
        return {"status": "error", "message": "Falha ao conectar com o Google Calendar."}
    
    try:
        dia, mes, ano = map(int, data_str.split('/'))
        hora, minuto = map(int, hora_str(':'))

        start_time = datetime.datetime(ano, mes, dia, hora, minuto)

        end_time = start_time + datetime.timedelta(hours=2) # Padrão de 2 horas o evento.

        event = {
            "summary": title,
            "description": description + "\n Evento agendado via CalendarIA",
            "start": {
                "dateTime": start_time.isoformat(),
                "timezone": "America/Sao_Paulo",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timezone": "America/Sao_Paulo",
            },
        }

        event = service.events().insert(calendarId="primary", body=event).execute()
        logging.info(f"Evento criado com sucesso: {event.get('htmlLink')}")

        return {
            "status": "success",
            "message": "Evento agendado no Google Calendar.",
            "link": event.get('htmlLink')
        }
    
    except Exception as e:
        logging.error(f"Erro ao criar evento: {e}")
        return {"status": "error", "message": str(e)}
    
# if __name__ == "__main__":
#     logging.info("Iniciando o processo de autenticação para gerar o token.json...")
#     get_calendar_service()
#     logging.info("Autenticação concluída. O arquivo token.json foi criado/atualizado.")