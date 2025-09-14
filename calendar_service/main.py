from dotenv import load_dotenv
load_dotenv()

from datetime import datetime
from fastapi import FastAPI, Depends, Request, HTTPException, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import os

import crud, models, security
from config import settings
from database import engine, get_db
from security import generate_session_state, verify_session_state
from google.google_calendar import agendar_google, listar_eventos_google, apagar_evento_google, apagar_evento_google_por_busca
from apple.apple_calendar import agendar_apple, listar_eventos_apple, apagar_evento_apple, apagar_evento_apple_por_busca
from auth.outlook_auth import get_outlook_auth_url_and_flow, get_outlook_account_object, temp_auth_flow_storage
from providers.outlook_provider import agendar_outlook

models.Base.metadata.create_all(bind=engine)
app = FastAPI(title="API CalendarIA")

SESSION_COOKIE_NAME = "calendaria_auth_session"

class EventoAgendarMulti(BaseModel):
    chat_id: str
    date: str
    hour: str
    title: str
    description: str

def set_cookie_env(response: Response, key: str, value: str):
    is_local = settings.OUTLOOK_REDIRECT_URI.startswith("http://localhost") or settings.OUTLOOK_REDIRECT_URI.startswith("http://127.0.0.1")
    response.set_cookie(
        key=key,
        value=value,
        httponly=True,
        samesite="none" if not is_local else "lax",
        secure=not is_local
    )

@app.post("/agendar")
def agendar_evento_multi(evento: EventoAgendarMulti, db: Session = Depends(get_db)):

    user = crud.get_user_by_chat_id(db, chat_id=evento.chat_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado. Conecte um calendário com !conectar.")
    
    accounts = crud.get_user_accounts(db, user)
    if not accounts:
        raise HTTPException(status_code=400, detail="Nenhuma conta de calendário conectada. Use !conectar.")
        
    resultados = []
    
    for account in accounts:
        if account.provider_name == "google":
            resultado = agendar_google(
                encrypted_credentials=account.encrypted_credentials,
                data_str=evento.date, hora_str=evento.hoor,
                titulo=evento.title, description=evento.description
            )
            resultados.append({"provider": "google", **resultado})

        elif account.provider_name == "outlook":
            resultado = agendar_outlook(
                db_account=account,
                data_str=evento.date, hora_str=evento.hour,
                titulo=evento.title, description=evento.description
            )
            resultados.append({"provider": "outlook", **resultado})
        
    return {"resultados": resultados}

class EventoApagar(BaseModel):
    id: str
    origem: str
    titulo: str
    inicio: str

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


# -----------------Rotas de Autenticação com o Outlook---------------------------------------------------------

@app.get("/outlook/start-auth")
def outlook_start_auth(chat_id: str):
    if not chat_id:
        raise HTTPException(status_code=400, detail="chat_id é obrigatório.")
    
    session_token = generate_session_state({"chat_id": chat_id})
    microsoft_auth_url = get_outlook_auth_url_and_flow(chat_id)

    content = f"""
    <html>
      <head>
        <meta http-equiv="refresh" content="0;url={microsoft_auth_url}">
      </head>
      <body>
        <p>Redirecionando para o login da Microsoft...</p>
      </body>
    </html>
    """
    response = HTMLResponse(content=content)
    set_cookie_env(response, SESSION_COOKIE_NAME, session_token)
    return response


@app.get("/auth/outlook/callback")
def auth_outlook_callback(request: Request, db: Session = Depends(get_db)):
    print("🔎 Query Params:", dict(request.query_params))
    print("🔎 Cookies recebidos no callback:", request.cookies)

    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if not session_token:
        raise HTTPException(status_code=400, detail="Sessão de autenticação não encontrada.")
    session_data = verify_session_state(session_token)
    if not session_data or "chat_id" not in session_data:
        raise HTTPException(status_code=400, detail="Sessão inválida ou expirada.")
    chat_id = session_data["chat_id"]

    auth_flow = temp_auth_flow_storage.pop(chat_id, None)
    if not auth_flow:
        raise HTTPException(status_code=400, detail="Fluxo de autenticação não encontrado ou expirado.")
    
    account = get_outlook_account_object()
    result = account.con.msal_client.acquire_token_by_auth_code_flow(
        auth_flow, dict(request.query_params)
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=f"Erro da Microsoft: {result.get('error_description')}")
    
    account.con.token_backend.token = result

    if "refresh_token" not in result:
        raise HTTPException(status_code=400, detail="A Microsoft não retornou refresh_token. Verifique se usou 'offline_access' no escopo.")
    
    id_token_claims = result.get('id_token_claims', {})
    username = id_token_claims.get('preferred_username')

    credentials_to_save = {
        'client_id': settings.OUTLOOK_CLIENT_ID,
        'client_secret': settings.OUTLOOK_CLIENT_SECRET,
        'token': account.con.token_backend.token,
        'username': username
    }

    user = crud.get_user_by_chat_id(db, chat_id=chat_id)
    if not user:
        user = crud.create_user(db, chat_id=chat_id)
    
    crud.create_or_update_account(db, user=user, provider="outlook", credentials=credentials_to_save)
    
    final_response = RedirectResponse("https://www.google.com/search?q=Conectado+com+sucesso+ao+Outlook!")
    final_response.delete_cookie(SESSION_COOKIE_NAME, domain="localhost")
    return final_response

    state_from_microsoft = request.query_params.get("state")

    if state_from_microsoft not in temp_state_storage:
        raise HTTPException(status_code=400, detail="Parâmetro 'state' inválido ou expirado.")
    
    chat_id = temp_state_storage.pop(state_from_microsoft) # Recupera e remove o state

    chat_id, original_state = state_from_microsoft.split("::")

    flow = get_google_auth_flow()
    flow.fetch_token(authorization_response=str(request.url))
    credentials = {
        'token': flow.credentials.token,
        'refresh_token': flow.credentials.refresh_token,
        'token_uri': flow.credentials.token_uri,
        'client_id': flow.credentials.client_id,
        'client_secret': flow.credentials.client_secret,
        'scopes': flow.credentials.scopes
    }

    user = crud.get_user_by_chat_id(db, chat_id=chat_id)
    if not user:
        user = crud.create_user(db, chat_id=chat_id)
    
    crud.create_or_update_account(db, user=user, provider="google", credentials=credentials)
    
    return RedirectResponse("https://www.google.com/search?q=Conectado+com+sucesso!")