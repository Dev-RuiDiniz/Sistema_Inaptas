from __future__ import annotations

from inaptas.domain.models import (
    FiscalStatusProviderResult,
    PgfnProviderResult,
    ProviderStatus,
)


class DisabledPgfnProvider:
    nome = "SERPRO_PGFN"

    async def consultar(self, cnpj: str) -> PgfnProviderResult:
        return PgfnProviderResult(
            provider=self.nome,
            status=ProviderStatus.DISABLED,
            source_data={},
            error_code="provider_disabled",
        )


class DisabledFiscalStatusProvider:
    nome = "INTEGRA_SITFIS"

    async def consultar(self, cnpj: str) -> FiscalStatusProviderResult:
        return FiscalStatusProviderResult(
            provider=self.nome,
            status=ProviderStatus.DISABLED,
            source_data={},
            error_code="provider_disabled",
        )
