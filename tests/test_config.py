import pytest

from inaptas.config import (
    ConfiguracaoInseguraError,
    Settings,
    validar_configuracao,
)


def test_configuracao_local_com_defaults_e_permitida() -> None:
    validar_configuracao(Settings(app_env="local"))


def test_configuracao_portal_transparencia_valida_limites() -> None:
    validar_configuracao(
        Settings(
            compliance_provider="portal_transparencia",
            portal_transparencia_api_token="token-sintetico",
        )
    )


@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("portal_transparencia_timeout_seconds", 0, "TIMEOUT_SECONDS"),
        ("portal_transparencia_max_retries", -1, "MAX_RETRIES"),
        ("portal_transparencia_max_pages", 0, "MAX_PAGES"),
    ],
)
def test_configuracao_portal_transparencia_rejeita_limites_invalidos(
    campo: str, valor: int, mensagem: str
) -> None:
    with pytest.raises(ConfiguracaoInseguraError, match=mensagem):
        validar_configuracao(Settings(**{campo: valor}))


@pytest.mark.parametrize(
    ("campo", "valor", "mensagem"),
    [
        ("serpro_divida_ativa_timeout_seconds", 0, "TIMEOUT_SECONDS"),
        ("serpro_divida_ativa_max_retries", -1, "MAX_RETRIES"),
    ],
)
def test_configuracao_serpro_rejeita_limites_invalidos(
    campo: str, valor: int, mensagem: str
) -> None:
    with pytest.raises(ConfiguracaoInseguraError, match=mensagem):
        validar_configuracao(Settings(**{campo: valor}))


def test_producao_rejeita_url_serpro_sem_https() -> None:
    settings = Settings(
        app_env="production",
        pgfn_provider="serpro_trial",
        serpro_divida_ativa_trial_token="token-sintetico",
        serpro_divida_ativa_base_url="http://serpro.test",
        internal_api_token="token-producao-seguro",
        orchestrator_api_token="token-orquestrador-seguro",
        n8n_internal_webhook_url="https://n8n.exemplo/webhook/inaptas",
        n8n_internal_webhook_token="token-n8n-seguro",
        n8n_encryption_key="chave-n8n-segura",
        openapi_enabled=False,
        trusted_hosts=["api.exemplo.com"],
    )

    with pytest.raises(ConfiguracaoInseguraError, match="SERPRO_DIVIDA_ATIVA_BASE_URL"):
        validar_configuracao(settings)


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
