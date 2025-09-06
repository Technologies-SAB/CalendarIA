from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from datetime import datetime
from google.google_calendar import agendar_google, listar_eventos_google
from apple.apple_calendar import agendar_apple, listar_eventos_apple

app = FastAPI(
    title="API CalendarIA",
    description="Microserviço de integração de Calendários Apple e Google."
)

class Evento(BaseModel):
    date: str
    hour: str
    title: str
    description: str

@app.post("/agendar")
async def agendar_evento(evento: Evento):
    resultado_google = agendar_google(evento.date, evento.hour, evento.title, evento.description)
    resultado_apple = agendar_apple(evento.date, evento.hour, evento.title, evento.description)

    if resultado_google["status"] == "error" and resultado_apple["status"] == "error":
        raise HTTPException(
            status_code=500,
            detail={
                "google_error": resultado_google.get('message'),
                "apple_error": resultado_apple.get('message')
            }
        )
    
    return {
        "status": "sucesso",
        "google": resultado_google,
        "apple": resultado_apple
    }

@app.get("/proximos")
async def listar_proximos_eventos():
    eventos_google = listar_eventos_google()
    eventos_apple = listar_eventos_apple()
    
    todos_eventos = eventos_google + eventos_apple

    eventos_unicos = []
    vistos = set()
    for evento in todos_eventos:
        chave = (evento['inicio'], evento['titulo'])
        if chave not in vistos:
            eventos_unicos.append(evento)
            vistos.add(chave)

    eventos_unicos.sort(key=lambda x: datetime.fromisoformat(x['inicio'].replace("Z", "+00:00")))
    
    return eventos_unicos