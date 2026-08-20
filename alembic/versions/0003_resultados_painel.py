"""Adiciona o contrato normalizado persistido para o painel."""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003_resultados_painel"
down_revision: str | None = "0002_painel"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "consultation_results",
        sa.Column("consultation_id", sa.String(36), nullable=False),
        sa.Column("organization_id", sa.String(36), nullable=False),
        sa.Column("normalized_response", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["consultation_id"], ["consultations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("consultation_id"),
    )
    op.create_index(
        "ix_consultation_results_organization_id", "consultation_results", ["organization_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_consultation_results_organization_id", table_name="consultation_results")
    op.drop_table("consultation_results")
