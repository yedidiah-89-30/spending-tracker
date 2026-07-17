from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.expense import ExpenseCategory


class ExpenseBase(BaseModel):
    category: ExpenseCategory
    amount: Decimal = Field(gt=0, description="Must be greater than zero.")
    description: str | None = Field(default=None, max_length=500)
    date: date_type


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    """All fields optional - PATCH-style partial update."""

    category: ExpenseCategory | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    description: str | None = Field(default=None, max_length=500)
    date: date_type | None = None


class ExpenseRead(ExpenseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
