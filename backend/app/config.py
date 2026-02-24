from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    MONGODB_URI: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "lead_intelligence"
    CLEARBIT_API_KEY: str | None = None
    PROXYCURL_API_KEY: str | None = None
    FRONTEND_URLS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.FRONTEND_URLS.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
 
