from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from inaptas.interfaces.http.schemas import (
    CompanyLookupRequest,
    FiscalResponse,
    ProviderSource,
    TaxPeriod,
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


def test_contrato_reserva_historico_de_enquadramento() -> None:
    periodo = TaxPeriod(
        included_at="2020-01-01",
        excluded_at=None,
        source="FONTE_OFICIAL",
        reference_date="2020-01-01",
    )
    resposta = FiscalResponse(cnpj="11222333000181", tax={"simple_national_history": [periodo]})

    assert resposta.tax.simple_national_history[0].source == "FONTE_OFICIAL"
    assert resposta.tax.simei_history == []
