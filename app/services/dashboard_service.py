"""Business logic for the Dashboard feature.

The Dashboard doesn't own any data itself - it aggregates across Income,
Expenses, Savings Goals, and Subscriptions.

Sprint 4 update: Expenses is now wired in (total_expenses, real
net_profit_loss, and expense rows merged into recent_transactions).
Savings Goals and Subscriptions still don't exist (Sprints 6, 7), so those
stay at 0/empty for now.

Each future sprint should:
  1. Inject that sprint's repository into DashboardService.__init__.
  2. Replace the corresponding hardcoded value below with a real query.
  3. Remove that feature's name from `_PENDING_FEATURES`.
No endpoint or schema change is required when that happens - the contract
has been stable since Sprint 2.
"""

from decimal import Decimal

from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.income_repository import IncomeRepository
from app.schemas.dashboard import DashboardSummary, RecentTransactionRead

_PENDING_FEATURES = ["savings_goals", "subscriptions"]

_RECENT_TRANSACTIONS_LIMIT = 5


class DashboardService:
    def __init__(self, income_repository: IncomeRepository, expense_repository: ExpenseRepository):
        self.income_repository = income_repository
        self.expense_repository = expense_repository

    def get_summary(self, user: User, month: int, year: int) -> DashboardSummary:
        """`month`/`year` scope the totals (total_income, total_expenses,
        net_profit_loss). `recent_transactions` deliberately does NOT scope
        to that period - it's a "latest activity" feed across every
        transaction type, so it always shows the user's most recent entries
        regardless of which month they're currently viewing totals for.
        This matches how most finance dashboards behave: you can look at
        July's totals while still seeing that you logged something
        yesterday.
        """
        total_income = Decimal(self.income_repository.sum_for_month(user.id, year, month))
        total_expenses = Decimal(self.expense_repository.sum_for_month(user.id, year, month))

        recent_income = self.income_repository.list_recent(user.id, limit=_RECENT_TRANSACTIONS_LIMIT)
        recent_expenses = self.expense_repository.list_recent(user.id, limit=_RECENT_TRANSACTIONS_LIMIT)

        recent_transactions = [
            RecentTransactionRead(
                id=row.id,
                type="income",
                category=row.category.value,
                amount=row.amount,
                description=row.description,
                date=row.date,
            )
            for row in recent_income
        ] + [
            RecentTransactionRead(
                id=row.id,
                type="expense",
                category=row.category.value,
                amount=row.amount,
                description=row.description,
                date=row.date,
            )
            for row in recent_expenses
        ]
        # Merge income + expense into one newest-first feed, capped at the
        # limit - not a flat concatenation of two separately-capped lists.
        recent_transactions.sort(key=lambda t: t.date, reverse=True)
        recent_transactions = recent_transactions[:_RECENT_TRANSACTIONS_LIMIT]

        return DashboardSummary(
            month=month,
            year=year,
            currency=user.currency,
            total_income=total_income,
            total_expenses=total_expenses,
            net_profit_loss=total_income - total_expenses,
            total_savings=Decimal("0.00"),
            recent_transactions=recent_transactions,
            pending_features=list(_PENDING_FEATURES),
        )

