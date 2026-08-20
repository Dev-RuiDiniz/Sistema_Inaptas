from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def agora_utc() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    pass


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
