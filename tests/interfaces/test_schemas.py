from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from inaptas.interfaces.http.schemas import (
    CompanyLookupRequest,
    FiscalResponse,
    ProviderSource,
)


def test_resposta_canonica_preserva_camadas_de_confianca() -> None:
    resposta = FiscalResponse(
        cnpj="12ABC34501DE35",
        sources=[ProviderSource(provider="RECEITAWS", status="ok")],
        generated_at=datetime.now(UTC),
    )

    assert resposta.system_diagnosis.registration == "UNKNOWN"
    assert resposta.ai_interpretation is None
    assert resposta.tax.pending_obligations == []


def test_requisicao_de_consulta_rejeita_campo_extra() -> None:
    with pytest.raises(ValidationError):
        CompanyLookupRequest(cnpj="11222333000181", outro_campo="nao-permitido")
