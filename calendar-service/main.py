from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from google.google_calendar import agendar_google

app = FastAPI(
    title="API CalendarIA",
    description="Microserviço de integração de Calendários Appel e Google."
)

class Evento(BaseModel):
    data: str
    hora: str
    title: str
    description: str

@app.post("/agendar")
async def agendar_evento(evento: Evento):
    resultado_google = agendar_google(evento.data, evento.hora, evento.title, evento.description)

    if resultado_google["status"] == "error":
        raise HTTPException(status_code=500, detail=f"Erro no Google Calendar: {resultado_google['message']}")
    
    return {
        "status": "sucesso",
        "google": resultado_google,
        
    }