import os
import datetime
import logging

from pyicloud import PyiCloudService
from pyicloud.exceptions import PyiCloudFailedLoginException
from config import settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_icloud_api():

    try:
        api = PyiCloudService(settings.ICLOUD_USERNAME, settings.ICLOUD_PASSWORD)

        if api.requires_2fa:
            logging.error("A conta do iCLoud requer autenticação de dois fatores. Use uma senha especifica de aplicativo")
            return None
        
        return api
    except PyiCloudFailedLoginException:
        logging.error("Falha ao realizar login no iCloud. Verifique o usuário e a senha especifica de aplicativo.")
        return None
    except Exception as e:
        logging.error(f"Um erro inesperado ocorreu ao se conectar ao iCloud: {e}")
        return None
    
def agendar_apple(data_str: str, hora_str: str, title: str, description: str):
    api = get_icloud_api()

    if not api:
        return{"status": "error", "message": "Não foi possível se conectar ao iCloud."}
    
    try:
        dia, mes, ano = map(int, data_str.split('/'))
        hora, minuto = map(int, hora_str.split(':'))

        start_time = datetime.datetime(ano, mes, dia, hora, minuto)

        end_time = start_time + datetime.timedelta(hours=2) # Padrão de 2 horas o evento.

        nome_calendario_pricipal = 'Pessoal'

        calendar = None

        for cal in api.calendar.get_calendars.values():
            if cal.name.lower() == nome_calendario_pricipal.lower():
                calendar = cal
                break

        if not calendar:
            if api.calendar.get_calendars():
                calendar = list(api.calendar.get_calendars())[0]
                logging.warning(f"Calendiario '{nome_calendario_pricipal}' não encontrado. Usando '{calendar.name}' como padrão.")

            else:
                raise ValueError("Nenhum calendário encontrado na conta do iCloud.")
            
        calendar.new_event(
            title=title,
            description=description,
            start=start_time,
            end=end_time
        )

        logging.info(f"Evento '{title}' agendado com sucesso no iCloud.")
        return {
            "status": "success",
            "message": f"Evento agendado no calendário '{calendar.name}' do iCloud."
        }
    
    except Exception as e:
        logging.error(f"Erro ao criar evento: {e}")
        return {"status": "error", "message": str(e)}
    