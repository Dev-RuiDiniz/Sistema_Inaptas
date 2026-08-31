from datetime import UTC, datetime

from inaptas.domain.models import ProviderStatus
from inaptas.infrastructure.persistence.models import Consultation
from inaptas.interfaces.http.schemas import (
    ComplianceData,
    FiscalResponse,
    ProviderSource,
    SanctionRecord,
)
from inaptas.interfaces.panel.relatorios import gerar_csv, gerar_pdf


def _dados() -> tuple[Consultation, FiscalResponse]:
    consulta = Consultation(
        id="consulta",
        correlation_id="correlacao",
        cnpj="11222333000181",
        request_type="full-check",
        status="completed",
        requested_at=datetime.now(UTC),
    )
    resposta = FiscalResponse(
        cnpj="11222333000181",
        company={"legal_name": "Empresa Teste", "registration_status": "ATIVA"},
        sources=[ProviderSource(provider="receitaws", status=ProviderStatus.UNAVAILABLE)],
    )
    return consulta, resposta


def test_csv_e_utf8_com_bom_e_preserva_indisponibilidade() -> None:
    consulta, resposta = _dados()
    arquivo = gerar_csv(consulta, resposta)
    assert arquivo.startswith(b"\xef\xbb\xbf")
    assert "unavailable" in arquivo.decode("utf-8-sig")
    assert b"token" not in arquivo.lower()


def test_pdf_e_gerado_sem_segredos() -> None:
    consulta, resposta = _dados()
    arquivo = gerar_pdf(consulta, resposta)
    assert arquivo.startswith(b"%PDF")
    assert b"segredo" not in arquivo.lower()


def test_relatorios_incluem_resumo_e_registro_normalizado() -> None:
    consulta, resposta = _dados()
    resposta.compliance = ComplianceData(
        sanctions_found=True,
        records=[
            SanctionRecord(
                dataset="CEIS",
                id=7,
                sanction_type="Impedimento",
                authority_name="Órgão Teste",
                process_number="PROC-7",
                publication_url="https://exemplo.test/7",
            )
        ],
    )

    arquivo = gerar_csv(consulta, resposta).decode("utf-8-sig")

    assert "registros encontrados" in arquivo
    assert "Registro 1 — Dataset" in arquivo
    assert "CEIS" in arquivo
    assert "PROC-7" in arquivo
    assert "https://exemplo.test/7" in arquivo
