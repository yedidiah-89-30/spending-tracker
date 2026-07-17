import enum
from datetime import date as date_, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, Numeric, String, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ExpenseCategory(str, enum.Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    RENT = "rent"
    UTILITIES = "utilities"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    OTHERS = "others"


class Expense(Base):
    __tablename__ = "expenses"
    __table_args__ = (
        # Mirrors alembic/versions/0003_create_expenses_table.py exactly -
        # see the comment on Income.__table_args__ in app/models/income.py
        # for why this needs to live here too, not just in the migration.
        CheckConstraint("amount > 0", name="ck_expenses_amount_positive"),
        CheckConstraint(
            "category IN ('food', 'transport', 'rent', 'utilities', 'shopping', 'entertainment', 'others')",
            name="ck_expenses_category_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    category: Mapped[ExpenseCategory] = mapped_column(
        SAEnum(
            ExpenseCategory,
            name="expense_category",
            native_enum=False,
            length=20,
            # Same fix as Income (see app/models/income.py) - without
            # values_callable, SQLAlchemy binds the enum member NAME
            # ("FOOD") instead of its value ("food"), which violates
            # ck_expenses_category_valid.
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    # Numeric (not Float) to avoid floating-point rounding errors on money -
    # same convention as Income (see app/models/income.py).
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date: Mapped[date_] = mapped_column(Date, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="expenses")
