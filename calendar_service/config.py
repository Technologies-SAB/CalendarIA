from pydantic_settings import BaseSettings
import dotenv

dotenv.load_dotenv()

class Settings(BaseSettings):
    SCOPES: list[str] = ["https://www.googleapis.com/auth/calendar"]
    ICLOUD_USERNAME: str
    ICLOUD_PASSWORD: str

settings = Settings()