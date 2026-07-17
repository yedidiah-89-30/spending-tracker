from datetime import date
from decimal import Decimal

import pytest

from app.models.expense import Expense, ExpenseCategory
from app.models.income import Income, IncomeCategory
from app.models.user import User
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.income_repository import IncomeRepository
from app.services.dashboard_service import DashboardService


@pytest.fixture()
def user(db_session):
    user = User(email="ada@example.com", full_name="Ada", hashed_password="x", currency="₦")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def dashboard_service(db_session):
    return DashboardService(IncomeRepository(db_session), ExpenseRepository(db_session))


class TestDashboardService:
    def test_summary_reflects_requested_period_and_user_currency(self, dashboard_service, user):
        summary = dashboard_service.get_summary(user, month=3, year=2026)

        assert summary.month == 3
        assert summary.year == 2026
        assert summary.currency == "₦"

    def test_summary_is_zeroed_when_user_has_no_data_yet(self, dashboard_service, user):
        summary = dashboard_service.get_summary(user, month=1, year=2026)

        assert summary.total_income == Decimal("0")
        assert summary.total_expenses == Decimal("0")
        assert summary.net_profit_loss == Decimal("0")
        assert summary.total_savings == Decimal("0")
        assert summary.recent_transactions == []
        assert set(summary.pending_features) == {"savings_goals", "subscriptions"}
        assert "income" not in summary.pending_features
        assert "expenses" not in summary.pending_features

    def test_summary_reflects_real_income_for_the_requested_month(self, db_session, dashboard_service, user):
        db_session.add(
            Income(
                user_id=user.id,
                category=IncomeCategory.SALARY,
                amount=Decimal("1500.00"),
                description="July salary",
                date=date(2026, 7, 5),
            )
        )
        # A different month - must NOT count toward the July total, but
        # DOES still show up in recent_transactions (that feed is
        # deliberately not scoped to the requested month - see
        # DashboardService.get_summary's docstring).
        db_session.add(
            Income(
                user_id=user.id,
                category=IncomeCategory.FREELANCE,
                amount=Decimal("200.00"),
                description="June gig",
                date=date(2026, 6, 20),
            )
        )
        db_session.commit()

        summary = dashboard_service.get_summary(user, month=7, year=2026)

        assert summary.total_income == Decimal("1500.00")
        assert summary.net_profit_loss == Decimal("1500.00")
        assert len(summary.recent_transactions) == 2
        assert summary.recent_transactions[0].category == "salary"  # most recent first

    def test_summary_reflects_real_expenses_and_net_profit_loss(self, db_session, dashboard_service, user):
        db_session.add(
            Income(
                user_id=user.id,
                category=IncomeCategory.SALARY,
                amount=Decimal("2000.00"),
                description="July salary",
                date=date(2026, 7, 1),
            )
        )
        db_session.add(
            Expense(
                user_id=user.id,
                category=ExpenseCategory.RENT,
                amount=Decimal("800.00"),
                description="July rent",
                date=date(2026, 7, 2),
            )
        )
        db_session.commit()

        summary = dashboard_service.get_summary(user, month=7, year=2026)

        assert summary.total_income == Decimal("2000.00")
        assert summary.total_expenses == Decimal("800.00")
        assert summary.net_profit_loss == Decimal("1200.00")

    def test_recent_transactions_merge_income_and_expenses_newest_first(self, db_session, dashboard_service, user):
        db_session.add(
            Income(
                user_id=user.id,
                category=IncomeCategory.SALARY,
                amount=Decimal("2000.00"),
                description="July salary",
                date=date(2026, 7, 1),
            )
        )
        db_session.add(
            Expense(
                user_id=user.id,
                category=ExpenseCategory.FOOD,
                amount=Decimal("45.00"),
                description="Groceries",
                date=date(2026, 7, 6),
            )
        )
        db_session.commit()

        summary = dashboard_service.get_summary(user, month=7, year=2026)

        assert [t.type for t in summary.recent_transactions] == ["expense", "income"]

    def test_net_profit_loss_can_be_negative(self, db_session, dashboard_service, user):
        db_session.add(
            Income(
                user_id=user.id,
                category=IncomeCategory.FREELANCE,
                amount=Decimal("100.00"),
                description="Small gig",
                date=date(2026, 7, 1),
            )
        )
        db_session.add(
            Expense(
                user_id=user.id,
                category=ExpenseCategory.SHOPPING,
                amount=Decimal("300.00"),
                description="New shoes",
                date=date(2026, 7, 3),
            )
        )
        db_session.commit()

        summary = dashboard_service.get_summary(user, month=7, year=2026)

        assert summary.net_profit_loss == Decimal("-200.00")
