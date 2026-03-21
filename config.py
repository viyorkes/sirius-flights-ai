from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str

    # RapidAPI
    rapidapi_key: str
    rapidapi_host: str = "flights-sky.p.rapidapi.com"
    rapidapi_base_url: str = "https://flights-sky.p.rapidapi.com"

    # Claude
    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096

    # App
    app_name: str = "Sirius Flights AI"
    app_version: str = "1.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()