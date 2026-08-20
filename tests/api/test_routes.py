from datetime import UTC, datetime

from fastapi.testclient import TestClient

from inaptas.config import Settings
from inaptas.domain.cnpj import CnpjInvalidoError, normalizar_cnpj
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

    async def consulta_completa(self, cnpj: str) -> FiscalResponse:
        return self.resposta.model_copy(update={"cnpj": cnpj})


def _cliente() -> TestClient:
    configuracao = Settings(
        app_env="test",
        internal_api_token="token-teste",
        trusted_hosts=["testserver"],
    )
    return TestClient(create_app(settings=configuracao, service=ServicoFalso()))


def test_health_e_publico_e_retorna_correlation_id() -> None:
    resposta = _cliente().get("/health")

    assert resposta.status_code == 200
    assert resposta.headers["X-Correlation-ID"]


def test_rota_interna_rejeita_token_ausente() -> None:
    resposta = _cliente().post("/v1/company/lookup", json={"cnpj": "11222333000181"})

    assert resposta.status_code == 401
    assert resposta.json()["error"]["code"] == "unauthorized"


def test_lookup_autenticado_devolve_resposta_canonica() -> None:
    resposta = _cliente().post(
        "/v1/company/lookup",
        headers={"Authorization": "Bearer token-teste", "X-Correlation-ID": "correlacao-teste"},
        json={"cnpj": "11.222.333/0001-81"},
    )

    assert resposta.status_code == 200
    assert resposta.headers["X-Correlation-ID"] == "correlacao-teste"
    assert resposta.json()["cnpj"] == "11222333000181"


def test_cnpj_invalido_retorna_erro_estavel() -> None:
    resposta = _cliente().post(
        "/v1/company/lookup",
        headers={"Authorization": "Bearer token-teste"},
        json={"cnpj": "invalido"},
    )

    assert resposta.status_code == 422
    assert resposta.json()["error"]["code"] == "invalid_cnpj"
