from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrationResult:
    status: str
    error_code: str | None = None
