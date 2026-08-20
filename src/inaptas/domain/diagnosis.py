from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from inaptas.domain.models import CadastroProviderResult, PgfnProviderResult, ProviderStatus


@dataclass(frozen=True)
class SystemDiagnosis:
    registration: str = "UNKNOWN"
    pgfn: str = "UNKNOWN_SOURCE_UNAVAILABLE"


def _diagnosticar_cadastro(resultado: CadastroProviderResult | None) -> str:
    if resultado is None or resultado.status is not ProviderStatus.OK:
        return "UNKNOWN"

    situacao: Any = resultado.source_data.get("registration_status")
    if situacao is None:
        situacao = resultado.source_data.get("situacao_cadastral")
    if not isinstance(situacao, str) or not situacao.strip():
        return "UNKNOWN"
    if situacao.strip().upper() in {"ATIVA", "ACTIVE"}:
        return "ACTIVE"
    return "INACTIVE"


def _diagnosticar_pgfn(resultado: PgfnProviderResult | None) -> str:
    if resultado is None or resultado.status is not ProviderStatus.OK:
        return "UNKNOWN_SOURCE_UNAVAILABLE"

    has_active_debt = resultado.source_data.get("has_active_debt")
    if has_active_debt is False:
        return "NO_ACTIVE_DEBT_RETURNED_BY_SOURCE"
    if has_active_debt is True:
        return "ACTIVE_DEBT_RETURNED_BY_SOURCE"
    return "UNKNOWN"


def construir_diagnostico(
    cadastro: CadastroProviderResult | None,
    pgfn: PgfnProviderResult | None,
) -> SystemDiagnosis:
    return SystemDiagnosis(
        registration=_diagnosticar_cadastro(cadastro),
        pgfn=_diagnosticar_pgfn(pgfn),
    )
