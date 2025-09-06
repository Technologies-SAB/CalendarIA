from pydantic_settings import BaseSettings
import dotenv

dotenv.load_dotenv()

class Settings(BaseSettings):
    SCOPES: str
    ICLOUD_USERNAME: str
    ICLOUD_PASSWORD: str

settings = Settings()