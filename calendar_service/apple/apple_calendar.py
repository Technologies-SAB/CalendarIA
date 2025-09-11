import os
import datetime
import logging
import uuid
import pytz

from caldav import DAVClient, Principal, Calendar
from icalendar import Calendar as iCalendar, Event as iEvent

from config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

ICLOUD_SERVERS = [
    "https://caldav.icloud.com",
    "https://p01-caldav.icloud.com",
    "https://p02-caldav.icloud.com",
    "https://p03-caldav.icloud.com",
    "https://p04-caldav.icloud.com",
    "https://p06-caldav.icloud.com",
]

# def get_icloud_api():

#     print(f"--- DEBUG: Tentando login com Usuário: '{settings.ICLOUD_USERNAME}'")
#     print(f"--- DEBUG: Tentando login com Senha: '{settings.ICLOUD_PASSWORD}'")

#     try:
#         api = PyiCloudService(settings.ICLOUD_USERNAME, settings.ICLOUD_PASSWORD)

#         if api.requires_2fa:
#             logging.error("A conta do iCLoud requer autenticação de dois fatores. Use uma senha especifica de aplicativo")
#             return None
        
#         return api
#     except PyiCloudFailedLoginException:
#         logging.error("Falha ao realizar login no iCloud. Verifique o usuário e a senha especifica de aplicativo.")
#         return None
#     except Exception as e:
#         logging.error(f"Um erro inesperado ocorreu ao se conectar ao iCloud: {e}")
#         return None
    
def agendar_apple(data_str: str, hora_str: str, title: str, description: str):
    client = None
    
    for server_url in ICLOUD_SERVERS:
        try:
            client = DAVClient(url=server_url, username=settings.ICLOUD_USERNAME, password=settings.ICLOUD_PASSWORD)
            logging.info(f"Conectado com sucesso ao servidor CalDAV: {server_url}")
            break
        except Exception:
            logging.warning(f"Falha ao conectar em {server_url}. Tentando o próximo...")
            continue
    
    if not client:
        return {"status": "error", "message": "Falha ao conectar em todos os servidores CalDAV conhecidos. Verifique as credenciais."}
    
    try:
        principal: Principal = client.principal()
        
        calendars: list[Calendar] = principal.calendars()

        if not calendars:
            return {"status": "error", "message": "Nenhum calendário encontrado na conta do iCloud."}
        
        target_calendar_name = "Pessoal"
        calendar = None

        for cal in calendars:
            if cal.name.lower() == target_calendar_name.lower():
                calendar = cal
                logging.info(f"Calendário alvo '{target_calendar_name}' encontrado!")
                break
        
        if not calendar:
            calendar = calendars[0]
            logging.warning(f"Calendário '{target_calendar_name}' não encontrado. Usando o calendário padrão: '{calendar.name}'")

        cal = iCalendar()
        cal.add('prodid', '-//CalendarIA Bot//')
        cal.add('version', '2.0')

        fuso_horario = pytz.timezone("America/Sao_Paulo")
        dia, mes, ano = map(int, data_str.split('/'))
        hora, minuto = map(int, hora_str.split(':'))
        start_time = fuso_horario.localize(datetime.datetime(ano, mes, dia, hora, minuto))
        end_time = start_time + datetime.timedelta(hours=2)
        
        event = iEvent()
        event.add('summary', title)
        event.add('description', description)
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        event.add('dtstamp', datetime.datetime.utcnow()) 
        event.add('uid', str(uuid.uuid4()))

        cal.add_component(event)
        
        event_salvo = calendar.save_event(cal.to_ical())
        logging.info(f"Evento '{title}' agendado com sucesso no iCloud via CalDAV.")

        return {
            "status": "success",
            "message": f"Evento agendado no calendário '{calendar.name}' do iCloud."
        }
        
    except Exception as e:
        logging.error(f"Erro ao agendar evento no iCloud via CalDAV: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
    
def listar_eventos_apple():

    client = None
    for server_url in ICLOUD_SERVERS:
        try:
            client = DAVClient(url=server_url, username=settings.ICLOUD_USERNAME, password=settings.ICLOUD_PASSWORD)
            break
        except Exception:
            continue
    if not client: return []

    try:
        principal: Principal = client.principal()
        
        calendars: list[Calendar] = principal.calendars()

        if not calendars:
            return {"status": "error", "message": "Nenhum calendário encontrado na conta do iCloud."}
        
        target_calendar_name = "Pessoal"
        calendar = None

        for cal in calendars:
            if cal.name.lower() == target_calendar_name.lower():
                calendar = cal
                logging.info(f"Calendário alvo '{target_calendar_name}' encontrado!")
                break
        
        if not calendar:
            calendar = calendars[0]
            logging.warning(f"Calendário '{target_calendar_name}' não encontrado. Usando o calendário padrão: '{calendar.name}'")

        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=7)

        events_fetched = calendar.date_search(start=start_date, end=end_date, expand=True)
        
        lista_formatada = []
        for event in events_fetched:
            event_data = event.vobject_instance.vevent
            titulo = event_data.summary.value
            inicio = event_data.dtstart.value
            uid = event_data.uid.value
            lista_formatada.append({
                "id": uid,
                "inicio": inicio.isoformat(), 
                "titulo": titulo,
                "origem": "iCloud"
            })
        return lista_formatada
    except Exception as e:
        logging.error(f"Erro ao listar eventos do iCloud: {e}")
        return []
    
def apagar_evento_apple(event_id: str):

    client = None

    for server_url in ICLOUD_SERVERS:
        try:
            client = DAVClient(url=server_url, username=settings.ICLOUD_USERNAME, password=settings.ICLOUD_PASSWORD)
            break
        except Exception: continue
        
    if not client: return {"status": "error", "message": "Falha na conexão com o iCloud."}

    try:
        principal: Principal = client.principal()
        
        calendars: list[Calendar] = principal.calendars()

        if not calendars:
            return {"status": "error", "message": "Nenhum calendário encontrado na conta do iCloud."}
        
        target_calendar_name = "Pessoal"
        calendar = None

        for cal in calendars:
            if cal.name.lower() == target_calendar_name.lower():
                calendar = cal
                logging.info(f"Calendário alvo '{target_calendar_name}' encontrado!")
                break
        
        if not calendar:
            calendar = calendars[0]
            logging.warning(f"Calendário '{target_calendar_name}' não encontrado. Usando o calendário padrão: '{calendar.name}'")
            
        start_date = datetime.datetime.now()
        end_date = start_date + datetime.timedelta(days=365)

        events_fetched = calendar.date_search(start=start_date, end=end_date, expand=True)

        for event in events_fetched:
            if event.vobject_instance.vevent.uid.value == event_id:
                event_title = event.vobject_instance.vevent.summary.value
                event.delete()
                logging.info(f"Evento '{event_title}' (ID: {event_id}) apagado do iCloud.")
                return {"status": "success", "message": "Evento apagado do iCloud."}
        
        logging.warning(f"Tentativa de apagar evento não encontrado no iCloud (ID: {event_id}).")
        return {"status": "not_found", "message": "Evento não encontrado no iCloud."}
    except Exception as e:
        logging.error(f"Erro ao apagar evento do iCloud: {e}")
        return {"status": "error", "message": str(e)}
    
def apagar_evento_apple_por_busca(titulo: str, inicio_iso: str):
    client = None

    for server_url in ICLOUD_SERVERS:
        try:
            client = DAVClient(url=server_url, username=settings.ICLOUD_USERNAME, password=settings.ICLOUD_PASSWORD)
            break
        except Exception: continue
        
    if not client: return {"status": "error", "message": "Falha na conexão com o iCloud."}

    try:
        principal: Principal = client.principal()
        
        calendars: list[Calendar] = principal.calendars()

        if not calendars:
            return {"status": "error", "message": "Nenhum calendário encontrado na conta do iCloud."}
        
        target_calendar_name = "Pessoal"
        calendar = None

        for cal in calendars:
            if cal.name.lower() == target_calendar_name.lower():
                calendar = cal
                logging.info(f"Calendário alvo '{target_calendar_name}' encontrado!")
                break
        
        if not calendar:
            calendar = calendars[0]
            logging.warning(f"Calendário '{target_calendar_name}' não encontrado. Usando o calendário padrão: '{calendar.name}'")

        start_date = datetime.datetime.fromisoformat(inicio_iso.replace("Z", "+00:00"))
        end_date = start_date + datetime.timedelta(minutes=1)
        events_fetched = calendar.date_search(start=start_date, end=end_date, expand=True)

        for event in events_fetched:
            if event.vobject_instance and event.vobject_instance.vevent.summary.value.lower() == titulo.lower():
                event.delete()
                logging.info(f"Evento correspondente '{titulo}' apagado do iCloud.")
                return {"status": "success", "message": "Evento correspondente apagado com sucesso."}
        return {"status": "not_found", "message": "Evento correspondente não encontrado."}
    except Exception as e:
        return {"status": "error", "message": f"Erro ao tentar apagar evento correspondente: {e}"}