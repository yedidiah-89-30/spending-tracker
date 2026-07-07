import enum
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum as SAEnum, ForeignKey, Numeric, String, Date, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class IncomeCategory(str, enum.Enum):
    SALARY = "salary"
    BUSINESS = "business"
    FREELANCE = "freelance"
    OTHER = "other"


class Income(Base):
    __tablename__ = "income"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)

    category: Mapped[IncomeCategory] = mapped_column(
        SAEnum(IncomeCategory, name="income_category", native_enum=False, length=20),
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
