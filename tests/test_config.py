import pytest

from inaptas.config import (
    ConfiguracaoInseguraError,
    Settings,
    validar_configuracao,
)


def test_configuracao_local_com_defaults_e_permitida() -> None:
    validar_configuracao(Settings(app_env="local"))


def test_producao_rejeita_token_interno_padrao() -> None:
    settings = Settings(
        app_env="production",
        openapi_enabled=False,
        trusted_hosts=["api.exemplo.com"],
    )

    with pytest.raises(ConfiguracaoInseguraError, match="INTERNAL_API_TOKEN"):
        validar_configuracao(settings)


def test_producao_rejeita_openapi_habilitado() -> None:
    settings = Settings(
        app_env="production",
        internal_api_token="token-producao-seguro",
        orchestrator_api_token="token-orquestrador-seguro",
        n8n_internal_webhook_url="https://n8n.exemplo/webhook/inaptas",
        n8n_internal_webhook_token="token-n8n-seguro",
        n8n_encryption_key="chave-n8n-segura",
        trusted_hosts=["api.exemplo.com"],
    )

    with pytest.raises(ConfiguracaoInseguraError, match="OPENAPI_ENABLED"):
        validar_configuracao(settings)


def test_producao_rejeita_trusted_host_wildcard() -> None:
    settings = Settings(
        app_env="production",
        internal_api_token="token-producao-seguro",
        orchestrator_api_token="token-orquestrador-seguro",
        n8n_internal_webhook_url="https://n8n.exemplo/webhook/inaptas",
        n8n_internal_webhook_token="token-n8n-seguro",
        n8n_encryption_key="chave-n8n-segura",
        openapi_enabled=False,
        trusted_hosts=["*"],
    )

    with pytest.raises(ConfiguracaoInseguraError, match="TRUSTED_HOSTS"):
        validar_configuracao(settings)


def test_producao_segura_e_aceita() -> None:
    settings = Settings(
        app_env="production",
        internal_api_token="token-producao-seguro",
        orchestrator_api_token="token-orquestrador-seguro",
        n8n_internal_webhook_url="https://n8n.exemplo/webhook/inaptas",
        n8n_internal_webhook_token="token-n8n-seguro",
        n8n_encryption_key="chave-n8n-segura",
        openapi_enabled=False,
        trusted_hosts=["api.exemplo.com"],
    )

    validar_configuracao(settings)
