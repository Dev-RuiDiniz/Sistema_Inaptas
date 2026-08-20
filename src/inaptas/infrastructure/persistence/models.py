from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import JSON


def agora_utc() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    status: Mapped[str] = mapped_column(String(32), default="active")
    retention_days: Mapped[int] = mapped_column(Integer, default=90)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)


class PanelUser(Base):
    __tablename__ = "panel_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    oidc_subject: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), index=True)
    name: Mapped[str] = mapped_column(String(160))
    role: Mapped[str] = mapped_column(String(32), default="operator")
    status: Mapped[str] = mapped_column(String(32), default="active")
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)


class PanelAudit(Base):
    __tablename__ = "panel_audit"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    actor_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("panel_users.id"), nullable=True, index=True
    )
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    action: Mapped[str] = mapped_column(String(80))
    target_type: Mapped[str] = mapped_column(String(80))
    target_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    metadata_redacted: Mapped[dict[str, object]] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    correlation_id: Mapped[str] = mapped_column(String(128), index=True)
    cnpj: Mapped[str] = mapped_column(String(14), index=True)
    source: Mapped[str | None] = mapped_column(String(64), nullable=True)
    request_type: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="started")
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    response_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    whatsapp_contact_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    organization_id: Mapped[str | None] = mapped_column(
        ForeignKey("organizations.id"), nullable=True, index=True
    )
    requested_by_user_id: Mapped[str | None] = mapped_column(
        ForeignKey("panel_users.id"), nullable=True, index=True
    )
    origin: Mapped[str] = mapped_column(String(32), default="api")


class ConsultationResult(Base):
    __tablename__ = "consultation_results"

    consultation_id: Mapped[str] = mapped_column(
        ForeignKey("consultations.id", ondelete="CASCADE"), primary_key=True
    )
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), index=True)
    normalized_response: Mapped[dict[str, object]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)


class ApiAudit(Base):
    __tablename__ = "api_audit"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    consultation_id: Mapped[str] = mapped_column(ForeignKey("consultations.id"), index=True)
    provider: Mapped[str] = mapped_column(String(64))
    endpoint_alias: Mapped[str] = mapped_column(String(128))
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=agora_utc)


class ProviderConfig(Base):
    __tablename__ = "provider_config"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    provider: Mapped[str] = mapped_column(String(64), unique=True)
    enabled: Mapped[bool] = mapped_column(default=False)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    timeout: Mapped[int] = mapped_column(Integer, default=5)
    max_retries: Mapped[int] = mapped_column(Integer, default=0)
    cache_ttl: Mapped[int] = mapped_column(Integer, default=0)
    config_note: Mapped[str | None] = mapped_column(Text, nullable=True)
