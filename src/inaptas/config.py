from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "local"
    app_version: str = "0.1.0"
    internal_api_token: str = "troque-este-token-local"
    database_url: str = "postgresql+asyncpg://inaptas:inaptas@localhost:5432/inaptas"
    redis_url: str = "redis://localhost:6379/0"
    receitaws_base_url: str = "https://www.receitaws.com.br"
    receitaws_timeout_seconds: float = 5.0
    whatsapp_verify_token: str = ""
    whatsapp_app_secret: str = ""
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""
    whatsapp_api_base_url: str = "https://graph.facebook.com"
    whatsapp_timeout_seconds: float = 10.0
    dify_base_url: str = ""
    dify_api_key: str = ""
    dify_timeout_seconds: float = 10.0
    trusted_hosts: list[str] = ["localhost", "127.0.0.1"]
    openapi_enabled: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
