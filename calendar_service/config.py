from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str
    ENCRYPTION_KEY: str
    
    # Google
    SCOPES: list[str] = ["https://www.googleapis.com/auth/calendar"]
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    # Outlook
    OUTLOOK_CLIENT_ID: str
    OUTLOOK_CLIENT_SECRET: str
    OUTLOOK_REDIRECT_URI: str

    # iCloud
    ICLOUD_USERNAME: Optional[str] = None
    ICLOUD_PASSWORD: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()