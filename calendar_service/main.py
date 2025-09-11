from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from datetime import datetime
from google.google_calendar import (
    agendar_google, 
    listar_eventos_google, 
    apagar_evento_google, 
    apagar_evento_google_por_busca
)
from apple.apple_calendar import (
    agendar_apple, 
    listar_eventos_apple, 
    apagar_evento_apple, 
    apagar_evento_apple_por_busca
)

app = FastAPI(
    title="API CalendarIA",
    description="Microserviço de integração de Calendários Apple e Google."
)

class EventoAgendar(BaseModel):
    date: str
    hour: str
    title: str
    description: str

class EventoApagar(BaseModel):
    id: str
    origem: str
    titulo: str
    inicio: str

@app.post("/agendar")
async def agendar_evento(evento: EventoAgendar):
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

@app.delete("/apagar")
async def apagar_evento(evento: EventoApagar):
    resultado_google = {}
    resultado_apple = {}

    if evento.origem == "Google":
        resultado_google = apagar_evento_google(evento.id)
        resultado_apple = apagar_evento_apple_por_busca(evento.titulo, evento.inicio)
    
    elif evento.origem == "iCloud":
        resultado_apple = apagar_evento_apple(evento.id)
        resultado_google = apagar_evento_google_por_busca(evento.titulo, evento.inicio)

    return {"google": resultado_google, "apple": resultado_apple}