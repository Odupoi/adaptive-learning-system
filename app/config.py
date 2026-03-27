from pydantic_settings import BaseSettings
from functools import lru_cache
import os

# Read from environment variable or fallback to SQLite for local dev
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///adaptive_learning.db"
)

class Settings(BaseSettings):
    # Database
    database_url: str

    # Groq AI
    groq_api_key: str
    groq_model: str = "openai/gpt-oss-120b"

    # Application Settings
    app_name: str = "Adaptive Learning System"
    debug: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()