from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class RecentTransactionRead(BaseModel):
    """Shape for one row in the dashboard's 'recent transactions' widget.

    Populated from a merge of Income (Sprint 3) and Expense (Sprint 4)
    entries, newest first. Deliberately generic (`type` is "income" |
    "expense") rather than reusing IncomeRead/ExpenseRead directly, since
    this feed mixes both.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    category: str
    amount: Decimal
    description: str | None
    date: date


class MonthlyIncomePoint(BaseModel):
    """One point on the frontend's IncomeChart trend line.

    `amount` is deliberately a plain `float`, not `Decimal` (unlike every
    other money field on this API, which serializes as a string to avoid
    float precision loss - see total_income/total_expenses/etc. below).
    This field exists specifically to be plotted by a charting library,
    which wants a JSON number, not a string it would have to parse; a
    fraction-of-a-cent of float imprecision on a chart axis is immaterial,
    unlike on a balance the user might reconcile against a bank statement.
    `month` is formatted "Mon YYYY" (e.g. "Jul 2026") - human-readable and
    unambiguous across year boundaries, ready to use directly as a chart
    axis label with no further formatting needed on the frontend.
    """

    month: str
    amount: float


class DashboardSummary(BaseModel):
    """Top-level payload for GET /api/v1/dashboard/summary.

    total_income/total_expenses/net_profit_loss reflect real Income and
    Expense data as of Sprint 4. total_savings stays 0 until Savings Goals
    (Sprint 6) lands - see DashboardService and `pending_features` below.
    currency is read from the authenticated user's profile so the
    frontend never has to guess a display currency.
    """

    month: int = Field(ge=1, le=12)
    year: int
    currency: str

    total_income: Decimal
    total_expenses: Decimal
    net_profit_loss: Decimal
    total_savings: Decimal

    recent_transactions: list[RecentTransactionRead]

    # Trailing 6-month income trend, oldest first, ending at `month`/`year` -
    # feeds the frontend's IncomeChart component directly.
    income_data: list[MonthlyIncomePoint]

    # Lets the frontend show "coming soon" states for widgets whose data
    # source isn't wired up yet, instead of silently displaying zero as if
    # it were a real, meaningful total.
    pending_features: list[str]
