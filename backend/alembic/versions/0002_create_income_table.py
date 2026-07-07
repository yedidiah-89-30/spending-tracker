"""create income table

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-07

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "income",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.CheckConstraint("amount > 0", name="ck_income_amount_positive"),
        sa.CheckConstraint(
            "category IN ('salary', 'business', 'freelance', 'other')",
            name="ck_income_category_valid",
        ),
    )
    op.create_index("ix_income_user_id", "income", ["user_id"])
    op.create_index("ix_income_date", "income", ["date"])


def downgrade() -> None:
    op.drop_index("ix_income_date", table_name="income")
    op.drop_index("ix_income_user_id", table_name="income")
    op.drop_table("income")
