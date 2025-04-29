import secrets
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str 
    ALLOWED_ORIGINS: str
    DEBUG: bool = True
    CORS_ALLOW_CREDENTIALS: bool = True
    AZURE_STORAGE_CONNECTION_STRING: str
    FMP_APIKEY: str
    REFRESH_SECRET_KEY: str
    
    @property
    def cors_origins(self) -> list:
        return self.ALLOWED_ORIGINS.split(",")

    class Config:
        env_file = ".env"

settings = Settings()
    