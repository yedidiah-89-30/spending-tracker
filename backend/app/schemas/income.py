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
