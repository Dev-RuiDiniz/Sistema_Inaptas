from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ProviderStatus(StrEnum):
    OK = "ok"
    DISABLED = "disabled"
    UNAVAILABLE = "unavailable"
    INVALID = "invalid"
    ERROR = "error"


@dataclass(frozen=True)
class ProviderResult:
    provider: str
    status: ProviderStatus
    source_data: dict[str, Any]
    error_code: str | None = None
    latency_ms: int | None = None


@dataclass(frozen=True)
class CadastroProviderResult(ProviderResult):
    pass


@dataclass(frozen=True)
class PgfnProviderResult(ProviderResult):
    pass


@dataclass(frozen=True)
class FiscalStatusProviderResult(ProviderResult):
    pass


@dataclass(frozen=True)
class ComplianceProviderResult(ProviderResult):
    pass
