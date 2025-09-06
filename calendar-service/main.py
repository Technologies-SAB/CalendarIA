from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google.google_calendar import agendar_google
from apple.apple_calendar import agendar_apple

app = FastAPI(
    title="API CalendarIA",
    description="Microserviço de integração de Calendários Apple e Google."
)

class Evento(BaseModel):
    data: str
    hora: str
    title: str
    description: str

@app.post("/agendar")
async def agendar_evento(evento: Evento):
    resultado_google = agendar_google(evento.data, evento.hora, evento.title, evento.description)
    resultado_apple = agendar_apple(evento.data, evento.hora, evento.title, evento.description)

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