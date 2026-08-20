from inaptas.domain.diagnosis import construir_diagnostico
from inaptas.domain.models import CadastroProviderResult, PgfnProviderResult, ProviderStatus


def test_diagnostica_empresa_ativa_com_evidencia_da_fonte() -> None:
    cadastro = CadastroProviderResult(
        provider="RECEITAWS",
        status=ProviderStatus.OK,
        source_data={"registration_status": "ATIVA"},
    )

    diagnostico = construir_diagnostico(cadastro, None)

    assert diagnostico.registration == "ACTIVE"


def test_falha_de_cadastro_nao_vira_empresa_inativa() -> None:
    cadastro = CadastroProviderResult(
        provider="RECEITAWS",
        status=ProviderStatus.UNAVAILABLE,
        source_data={},
        error_code="timeout",
    )

    diagnostico = construir_diagnostico(cadastro, None)

    assert diagnostico.registration == "UNKNOWN"


def test_pgfn_sem_divida_so_e_afirmada_com_retorno_ok() -> None:
    pgfn = PgfnProviderResult(
        provider="SERPRO_PGFN",
        status=ProviderStatus.OK,
        source_data={"has_active_debt": False},
    )

    diagnostico = construir_diagnostico(None, pgfn)

    assert diagnostico.pgfn == "NO_ACTIVE_DEBT_RETURNED_BY_SOURCE"


def test_pgfn_indisponivel_nao_vira_sem_divida() -> None:
    pgfn = PgfnProviderResult(
        provider="SERPRO_PGFN",
        status=ProviderStatus.UNAVAILABLE,
        source_data={},
    )

    diagnostico = construir_diagnostico(None, pgfn)

    assert diagnostico.pgfn == "UNKNOWN_SOURCE_UNAVAILABLE"
