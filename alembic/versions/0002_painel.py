"""Adiciona organização, usuários e auditoria do painel."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002_painel"
down_revision: str | None = "0001_base"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("retention_days", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "panel_users",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("oidc_subject", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("email_verified", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("oidc_subject"),
    )
    op.create_index("ix_panel_users_organization_id", "panel_users", ["organization_id"])
    op.create_index("ix_panel_users_oidc_subject", "panel_users", ["oidc_subject"])
    op.create_index("ix_panel_users_email", "panel_users", ["email"])
    op.create_table(
        "panel_audit",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("actor_user_id", sa.String(36), nullable=True),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("target_type", sa.String(80), nullable=False),
        sa.Column("target_id", sa.String(128), nullable=True),
        sa.Column("metadata_redacted", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["panel_users.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_panel_audit_actor_user_id", "panel_audit", ["actor_user_id"])
    op.create_index("ix_panel_audit_organization_id", "panel_audit", ["organization_id"])
    op.add_column("consultations", sa.Column("organization_id", sa.String(36), nullable=True))
    op.add_column("consultations", sa.Column("requested_by_user_id", sa.String(36), nullable=True))
    op.add_column("consultations", sa.Column("origin", sa.String(32), nullable=False, server_default="api"))
    op.create_foreign_key(
        "fk_consultations_organization_id", "consultations", "organizations", ["organization_id"], ["id"]
    )
    op.create_foreign_key(
        "fk_consultations_requested_by_user_id",
        "consultations",
        "panel_users",
        ["requested_by_user_id"],
        ["id"],
    )
    op.create_index("ix_consultations_organization_id", "consultations", ["organization_id"])
    op.create_index("ix_consultations_requested_by_user_id", "consultations", ["requested_by_user_id"])


def downgrade() -> None:
    op.drop_index("ix_consultations_requested_by_user_id", table_name="consultations")
    op.drop_index("ix_consultations_organization_id", table_name="consultations")
    op.drop_constraint("fk_consultations_requested_by_user_id", "consultations", type_="foreignkey")
    op.drop_constraint("fk_consultations_organization_id", "consultations", type_="foreignkey")
    op.drop_column("consultations", "origin")
    op.drop_column("consultations", "requested_by_user_id")
    op.drop_column("consultations", "organization_id")
    op.drop_table("panel_audit")
    op.drop_index("ix_panel_users_email", table_name="panel_users")
    op.drop_index("ix_panel_users_oidc_subject", table_name="panel_users")
    op.drop_index("ix_panel_users_organization_id", table_name="panel_users")
    op.drop_table("panel_users")
    op.drop_table("organizations")
