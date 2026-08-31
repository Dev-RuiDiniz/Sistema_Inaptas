from datetime import UTC, datetime

from fakeredis.aioredis import FakeRedis
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from inaptas.config import Settings
from inaptas.domain.cnpj import CnpjInvalidoError, normalizar_cnpj
from inaptas.infrastructure.cache.redis_store import RedisStore
from inaptas.infrastructure.persistence.database import criar_fabrica_sessoes
from inaptas.interfaces.http.schemas import FiscalResponse
from inaptas.main import create_app


class ServicoFalso:
    def __init__(self) -> None:
        self.resposta = FiscalResponse(cnpj="11222333000181", generated_at=datetime.now(UTC))

    async def consultar_cadastro(self, cnpj: str) -> FiscalResponse:
        if cnpj == "invalido":
            raise CnpjInvalidoError("inválido")
        return self.resposta.model_copy(update={"cnpj": normalizar_cnpj(cnpj)})

    async def consultar_situacao_fiscal(self, cnpj: str) -> FiscalResponse:
        return self.resposta.model_copy(update={"cnpj": cnpj})

    async def consultar_pgfn(self, cnpj: str) -> FiscalResponse:
        return self.resposta.model_copy(update={"cnpj": cnpj})

    async def consultar_compliance(self, cnpj: str) -> FiscalResponse:
        return self.resposta.model_copy(update={"cnpj": cnpj})

    async def consulta_completa(self, cnpj: str) -> FiscalResponse:
        return self.resposta.model_copy(update={"cnpj": cnpj})


def _cliente() -> TestClient:
    configuracao = Settings(
        app_env="test",
        internal_api_token="token-teste",
        orchestrator_api_token="token-orquestrador",
        trusted_hosts=["testserver"],
        rate_limit_enabled=False,
    )
    app = create_app(settings=configuracao, service=ServicoFalso())
    app.state.redis_client = FakeRedis()
    app.state.redis_store = RedisStore(app.state.redis_client)
    app.state.database_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    app.state.session_factory = criar_fabrica_sessoes(app.state.database_engine)
    return TestClient(app)


def test_health_e_publico_e_retorna_correlation_id() -> None:
    resposta = _cliente().get("/health")

    assert resposta.status_code == 200
    assert resposta.headers["X-Correlation-ID"]


def test_rota_interna_rejeita_token_ausente() -> None:
    resposta = _cliente().post("/v1/company/lookup", json={"cnpj": "11222333000181"})

    assert resposta.status_code == 401
    assert resposta.json()["error"]["code"] == "unauthorized"


def test_rota_interna_rejeita_token_invalido() -> None:
    resposta = _cliente().post(
        "/v1/company/lookup",
        headers={"Authorization": "Bearer token-incorreto"},
        json={"cnpj": "11222333000181"},
    )

    assert resposta.status_code == 401
    assert resposta.json()["error"]["code"] == "unauthorized"


def test_rota_do_orquestrador_usa_token_separado() -> None:
    cliente = _cliente()

    com_token_interno = cliente.post(
        "/v1/orchestrator/company/full-check",
        headers={"Authorization": "Bearer token-teste"},
        json={"cnpj": "11222333000181"},
    )
    com_token_orquestrador = cliente.post(
        "/v1/orchestrator/company/full-check",
        headers={"Authorization": "Bearer token-orquestrador"},
        json={"cnpj": "11222333000181"},
    )

    assert com_token_interno.status_code == 401
    assert com_token_orquestrador.status_code == 200


def test_lookup_autenticado_devolve_resposta_canonica() -> None:
    resposta = _cliente().post(
        "/v1/company/lookup",
        headers={"Authorization": "Bearer token-teste", "X-Correlation-ID": "correlacao-teste"},
        json={"cnpj": "11.222.333/0001-81"},
    )

    assert resposta.status_code == 200
    assert resposta.headers["X-Correlation-ID"] == "correlacao-teste"
    assert resposta.json()["cnpj"] == "11222333000181"


def test_rota_de_compliance_exige_autenticacao_e_devolve_contrato() -> None:
    resposta = _cliente().post(
        "/v1/company/compliance",
        headers={"Authorization": "Bearer token-teste"},
        json={"cnpj": "11222333000181"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["compliance"]["records"] == []


def test_lookup_autenticado_aceita_cnpj_alfanumerico() -> None:
    resposta = _cliente().post(
        "/v1/company/lookup",
        headers={"Authorization": "Bearer token-teste"},
        json={"cnpj": "12abc34501de35"},
    )

    assert resposta.status_code == 200
    assert resposta.json()["cnpj"] == "12ABC34501DE35"


def test_cnpj_invalido_retorna_erro_estavel() -> None:
    resposta = _cliente().post(
        "/v1/company/lookup",
        headers={"Authorization": "Bearer token-teste"},
        json={"cnpj": "invalido"},
    )

    assert resposta.status_code == 422
    assert resposta.json()["error"]["code"] == "invalid_cnpj"


def test_rate_limit_bloqueia_excesso_de_consultas() -> None:
    configuracao = Settings(
        app_env="test",
        internal_api_token="token-teste",
        trusted_hosts=["testserver"],
        internal_rate_limit=1,
        rate_limit_window_seconds=60,
    )
    app = create_app(settings=configuracao, service=ServicoFalso())
    app.state.redis_store = RedisStore(FakeRedis())
    cliente = TestClient(app)
    cabecalho = {"Authorization": "Bearer token-teste"}

    primeira = cliente.post(
        "/v1/company/lookup", headers=cabecalho, json={"cnpj": "11222333000181"}
    )
    segunda = cliente.post(
        "/v1/company/lookup", headers=cabecalho, json={"cnpj": "11222333000181"}
    )

    assert primeira.status_code == 200
    assert segunda.status_code == 429
    assert segunda.json()["error"]["code"] == "rate_limit_exceeded"
