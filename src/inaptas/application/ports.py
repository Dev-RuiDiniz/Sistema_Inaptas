from __future__ import annotations

from typing import Protocol

from inaptas.domain.models import (
    CadastroProviderResult,
    ComplianceProviderResult,
    FiscalStatusProviderResult,
    PgfnProviderResult,
)


class CadastroProvider(Protocol):
    nome: str

    async def consultar(self, cnpj: str) -> CadastroProviderResult:
        ...


class PgfnProvider(Protocol):
    nome: str

    async def consultar(self, cnpj: str) -> PgfnProviderResult:
        ...


class FiscalStatusProvider(Protocol):
    nome: str

    async def consultar(self, cnpj: str) -> FiscalStatusProviderResult:
        ...


class ComplianceProvider(Protocol):
    nome: str

    async def consultar(self, cnpj: str) -> ComplianceProviderResult:
        ...
