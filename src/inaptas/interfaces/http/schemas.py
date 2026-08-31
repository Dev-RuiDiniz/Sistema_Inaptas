from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from inaptas.domain.models import ProviderStatus


class ModeloBase(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CompanyLookupRequest(ModeloBase):
    cnpj: str


class CompanyData(ModeloBase):
    legal_name: str | None = None
    opening_date: str | None = None
    registration_status: str | None = None
    registration_status_date: str | None = None
    registration_status_reason: str | None = None


class TaxPeriod(ModeloBase):
    included_at: str | None = None
    excluded_at: str | None = None
    source: str | None = None
    reference_date: str | None = None


class TaxData(ModeloBase):
    simple_national: bool | None = None
    simei: bool | None = None
    declared_tax_regime: str | None = None
    pending_obligations: list[str] = Field(default_factory=list)
    simple_national_history: list[TaxPeriod] = Field(default_factory=list)
    simei_history: list[TaxPeriod] = Field(default_factory=list)


class PgfnData(ModeloBase):
    has_active_debt: bool | None = None
    debts: list[dict[str, Any]] = Field(default_factory=list)


class SanctionRecord(ModeloBase):
    dataset: str
    id: int
    reference_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    publication_date: str | None = None
    sanction_type: str | None = None
    sanctioned_name: str | None = None
    sanctioned_document: str | None = None
    authority_name: str | None = None
    authority_uf: str | None = None
    process_number: str | None = None
    publication_url: str | None = None
    fine_amount: str | None = None
    reason: str | None = None


class ComplianceData(ModeloBase):
    sanctions_found: bool | None = None
    records: list[SanctionRecord] = Field(default_factory=list)


class ProviderSource(ModeloBase):
    provider: str
    status: ProviderStatus
    error_code: str | None = None
    latency_ms: int | None = None


class SystemDiagnosisModel(ModeloBase):
    registration: str = "UNKNOWN"
    pgfn: str = "UNKNOWN_SOURCE_UNAVAILABLE"


class FiscalResponse(ModeloBase):
    cnpj: str
    company: CompanyData = Field(default_factory=CompanyData)
    tax: TaxData = Field(default_factory=TaxData)
    pgfn: PgfnData = Field(default_factory=PgfnData)
    compliance: ComplianceData = Field(default_factory=ComplianceData)
    sources: list[ProviderSource] = Field(default_factory=list)
    system_diagnosis: SystemDiagnosisModel = Field(default_factory=SystemDiagnosisModel)
    ai_interpretation: str | None = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ErrorDetails(ModeloBase):
    code: str
    message: str
    correlation_id: str


class ErrorResponse(ModeloBase):
    error: ErrorDetails
