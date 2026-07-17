from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.income import IncomeCategory


class IncomeBase(BaseModel):
    category: IncomeCategory
    amount: Decimal = Field(gt=0, description="Must be greater than zero.")
    description: str | None = Field(default=None, max_length=500)
    date: date_type


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    """All fields optional - PATCH-style partial update."""

    category: IncomeCategory | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=500)
    date: date_type | None = None


class IncomeRead(IncomeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class IncomeStats(BaseModel):
    """Response for GET /api/v1/income/stats.

    `monthly_income`/`yearly_income` are scoped to the requested
    month/year (default: current month/year). `total_income` is
    all-time, across every income entry the user has ever logged.
    `growth_percentage` compares the requested month's total against the
    prior month's total; it's `None` when the prior month had no income
    to compare against (division by zero is meaningless, not zero).
    """

    month: int
    year: int
    total_income: Decimal
    monthly_income: Decimal
    yearly_income: Decimal
    growth_percentage: Decimal | None
