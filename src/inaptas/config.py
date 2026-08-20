from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

TOKEN_LOCAL_PADRAO = "troque-este-token-local"


class ConfiguracaoInseguraError(ValueError):
    """Indica uma configuração incompatível com ambiente de produção."""


class Settings(BaseSettings):
    app_env: str = "local"
    app_version: str = "0.1.0"
    internal_api_token: str = TOKEN_LOCAL_PADRAO
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
    rate_limit_enabled: bool = True
    internal_rate_limit: int = 60
    rate_limit_window_seconds: int = 60
    trusted_hosts: list[str] = ["localhost", "127.0.0.1"]
    openapi_enabled: bool = True
    panel_enabled: bool = False
    panel_session_ttl_seconds: int = 3_600
    panel_session_cookie_name: str = "inaptas_panel_session"
    panel_session_secure: bool = False
    panel_organization_id: str = "00000000-0000-0000-0000-000000000001"
    panel_organization_name: str = "Escritório de contabilidade"
    panel_bootstrap_admin_emails: list[str] = Field(default_factory=list)
    oidc_issuer_url: str = ""
    oidc_client_id: str = ""
    oidc_client_secret: str = ""
    oidc_redirect_uri: str = ""
    oidc_scopes: str = "openid email profile"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validar_configuracao(settings: Settings) -> None:
    if settings.app_env.lower() not in {"prod", "production"}:
        return
    if not settings.internal_api_token or settings.internal_api_token == TOKEN_LOCAL_PADRAO:
        raise ConfiguracaoInseguraError("INTERNAL_API_TOKEN deve ser definido em produção")
    if settings.openapi_enabled:
        raise ConfiguracaoInseguraError("OPENAPI_ENABLED deve ser false em produção")
    if not settings.trusted_hosts or "*" in settings.trusted_hosts:
        raise ConfiguracaoInseguraError("TRUSTED_HOSTS não pode aceitar wildcard em produção")
    if settings.panel_enabled:
        if not settings.panel_session_secure:
            raise ConfiguracaoInseguraError("PANEL_SESSION_SECURE deve ser true em producao")
        if not all(
            (
                settings.oidc_issuer_url,
                settings.oidc_client_id,
                settings.oidc_client_secret,
                settings.oidc_redirect_uri,
            )
        ):
            raise ConfiguracaoInseguraError(
                "OIDC deve estar configurado quando o painel estiver ativo"
            )
