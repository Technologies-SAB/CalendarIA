from cryptography.fernet import Fernet
from itsdangerous import URLSafeTimedSerializer
import os
from config import settings


ENCRYPTION_KEY = settings.ENCRYPTION_KEY


import logging
logging.info("Chave de criptografia carregada com sucesso.")

if not ENCRYPTION_KEY:
    raise ValueError("A ENCRYPTION_KEY não foi definida no ambiente. O serviço não pode iniciar de forma segura.")

fernet = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    if not isinstance(data, str):
        raise TypeError("Apenas dados do tipo string podem ser criptografados.")
    
    encrypted_bytes = fernet.encrypt(data.encode())
    return encrypted_bytes.decode()

def decrypt_data(encrypted_data: str) -> str:
    if not isinstance(encrypted_data, str):
        raise TypeError("Apenas dados do tipo string podem ser descriptografados.")
        
    decrypted_bytes = fernet.decrypt(encrypted_data.encode())
    return decrypted_bytes.decode()

session_serializer = URLSafeTimedSerializer(settings.ENCRYPTION_KEY, salt='outlook-auth-state')

def generate_session_state(data: dict) -> str:
    """Cria um token de estado seguro contendo dados (ex: chat_id)."""
    return session_serializer.dumps(data)

def verify_session_state(state_token: str, max_age_seconds: int = 3600) -> dict | None:
    """Verifica um token de estado, garantindo que não expirou e não foi adulterado."""
    try:
        return session_serializer.loads(state_token, max_age=max_age_seconds)
    except Exception:
        return None