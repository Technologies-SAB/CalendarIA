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
            cred_path = os.path.join(os.path.dirname(__file__), "..", "client_secret.json")
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, settings.SCOPES)
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
    service = get_calendar_service()

    if not service:
        return {"status": "error", "message": "Falha ao conectar com o Google Calendar."}
    
    try:
        dia, mes, ano = map(int, data_str.split('/'))
        hora, minuto = map(int, hora_str.split(':'))

        start_time = datetime.datetime(ano, mes, dia, hora, minuto)

        end_time = start_time + datetime.timedelta(hours=2) # Padrão de 2 horas o evento.

        event = {
            "summary": title,
            "description": description + "\n Evento agendado via CalendarIA",
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "America/Sao_Paulo",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "America/Sao_Paulo",
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
    
def listar_eventos_google():
    service = get_calendar_service()
    if not service:
        return []
    
    try:
        now = datetime.datetime.utcnow().isoformat() + "Z"
        future = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + "Z"
        
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                timeMax=future,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        lista_formatada = []
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            lista_formatada.append({
                "id": event["id"],
                "inicio": start, 
                "titulo": event["summary"],
                "origem": "Google"
            })
        return lista_formatada
    except Exception as e:
        logging.error(f"Erro ao listar eventos do Google: {e}")
        return []
    
def apagar_evento_google(event_id: str):

    service = get_calendar_service()

    if not service:
        return {"status": "error", "message": "Falha na conexão com o Google."}

    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        logging.info(f"Evento com ID '{event_id}' apagado do Google Calendar.")
        return {"status": "success", "message": "Evento apagado do Google Calendar."}
    
    except HttpError as e:
        if e.resp.status in [404, 410]:
            logging.warning(f"Tentativa de apagar evento já removido ou não encontrado no Google (ID: {event_id}). Status: {e.resp.status}")
            return {"status": "not_found", "message": "Este evento não foi encontrado no Google Calendar (pode já ter sido apagado)."}
        
        logging.error(f"Erro HTTP ao apagar evento do Google: {e}")
        return {"status": "error", "message": "Ocorreu um erro de comunicação com a API do Google."}
    
    except Exception as e:
        logging.error(f"Erro inesperado ao apagar evento do Google: {e}")
        return {"status": "error", "message": "Ocorreu um erro inesperado no servidor."}
    
def apagar_evento_google_por_busca(titulo: str, inicio_iso: str):

    service = get_calendar_service()

    if not service: return {"status": "error", "message": "Falha na conexão com o Google."}

    try:
        time_min_dt = datetime.datetime.fromisoformat(inicio_iso.replace("Z", "+00:00"))
        time_min = time_min_dt.isoformat() + "Z"
        time_max = (time_min_dt + datetime.timedelta(seconds=2)).isoformat() + "Z"
        
        events_result = service.events().list(
            calendarId='primary', q=titulo, timeMin=time_min, timeMax=time_max, maxResults=1, singleEvents=True
        ).execute()
        eventos = events_result.get('items', [])
        
        if not eventos:
            return {"status": "not_found", "message": "Evento correspondente não encontrado."}
        
        event_id = eventos[0]['id']
        service.events().delete(calendarId='primary', eventId=event_id).execute()

        logging.info(f"Evento correspondente '{titulo}' apagado do Google Calendar.")

        return {"status": "success", "message": "Evento correspondente apagado com sucesso."}

    except Exception as e:

        return {"status": "error", "message": f"Erro ao tentar apagar evento correspondente: {e}"}
    
    
# if __name__ == "__main__":
#     logging.info("Iniciando o processo de autenticação para gerar o token.json...")
#     get_calendar_service()
#     logging.info("Autenticação concluída. O arquivo token.json foi criado/atualizado.")