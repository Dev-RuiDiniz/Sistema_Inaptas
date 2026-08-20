"""Cria tabelas de consultas e auditoria."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001_base"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "consultations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("correlation_id", sa.String(length=128), nullable=False),
        sa.Column("cnpj", sa.String(length=14), nullable=False),
        sa.Column("source", sa.String(length=64), nullable=True),
        sa.Column("request_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("response_hash", sa.String(length=128), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("whatsapp_contact_hash", sa.String(length=128), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_consultations_correlation_id", "consultations", ["correlation_id"])
    op.create_index("ix_consultations_cnpj", "consultations", ["cnpj"])
    op.create_table(
        "api_audit",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("consultation_id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("endpoint_alias", sa.String(length=128), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["consultation_id"], ["consultations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_api_audit_consultation_id", "api_audit", ["consultation_id"])
    op.create_table(
        "provider_config",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("timeout", sa.Integer(), nullable=False),
        sa.Column("max_retries", sa.Integer(), nullable=False),
        sa.Column("cache_ttl", sa.Integer(), nullable=False),
        sa.Column("config_note", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider"),
    )


def downgrade() -> None:
    op.drop_table("provider_config")
    op.drop_index("ix_api_audit_consultation_id", table_name="api_audit")
    op.drop_table("api_audit")
    op.drop_index("ix_consultations_cnpj", table_name="consultations")
    op.drop_index("ix_consultations_correlation_id", table_name="consultations")
    op.drop_table("consultations")
