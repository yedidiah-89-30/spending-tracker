import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, Enum as SAEnum, ForeignKey, Numeric, String, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IncomeCategory(str, enum.Enum):
    SALARY = "salary"
    BUSINESS = "business"
    FREELANCE = "freelance"
    OTHER = "other"


class Income(Base):
    __tablename__ = "income"
    __table_args__ = (
        # These mirror the CheckConstraints in
        # alembic/versions/0002_create_income_table.py exactly. They were
        # previously declared only in the migration, not here - which meant
        # the SQLite test database (built via Base.metadata.create_all(),
        # not Alembic) never enforced them, and is why the enum-casing bug
        # (values bound as "SALARY" instead of "salary") shipped without a
        # failing test. Keeping both in sync matters; if this constraint
        # ever changes, update both places.
        CheckConstraint("amount > 0", name="ck_income_amount_positive"),
        CheckConstraint(
            "category IN ('salary', 'business', 'freelance', 'other')",
            name="ck_income_category_valid",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    category: Mapped[IncomeCategory] = mapped_column(
        SAEnum(
            IncomeCategory,
            name="income_category",
            native_enum=False,
            length=20,
            # By default SQLAlchemy binds/reads a Python enum column using the
            # member NAME ("SALARY"), not its value ("salary"). That mismatch
            # against the ck_income_category_valid CHECK constraint (which
            # only allows the lowercase values) is what caused the
            # CheckViolation - values_callable makes it use .value instead.
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    # Numeric (not Float) to avoid floating-point rounding errors on money.
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=12, scale=2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user = relationship("User", back_populates="incomes")
