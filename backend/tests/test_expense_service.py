from datetime import date
from decimal import Decimal

import pytest

from app.core.exceptions import NotFoundError
from app.models.expense import ExpenseCategory
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.common import SortOrder
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services.expense_service import ExpenseService


@pytest.fixture()
def expense_service(db_session):
    return ExpenseService(ExpenseRepository(db_session))


def make_payload(**overrides):
    defaults = dict(
        category=ExpenseCategory.FOOD,
        amount=Decimal("50.00"),
        description="Groceries",
        date=date(2026, 7, 1),
    )
    defaults.update(overrides)
    return ExpenseCreate(**defaults)


def list_kwargs(**overrides):
    defaults = dict(
        page=1,
        page_size=20,
        category=None,
        start_date=None,
        end_date=None,
        min_amount=None,
        max_amount=None,
        search=None,
        sort_by="date",
        sort_order=SortOrder.DESC,
    )
    defaults.update(overrides)
    return defaults


class TestCreate:
    def test_create_persists_and_returns_expense(self, expense_service):
        expense = expense_service.create(user_id=1, payload=make_payload())

        assert expense.id is not None
        assert expense.amount == Decimal("50.00")
        assert expense.category == ExpenseCategory.FOOD


class TestGet:
    def test_get_returns_owned_expense(self, expense_service):
        created = expense_service.create(user_id=1, payload=make_payload())

        fetched = expense_service.get(user_id=1, expense_id=created.id)

        assert fetched.id == created.id

    def test_get_raises_not_found_for_another_users_expense(self, expense_service):
        created = expense_service.create(user_id=1, payload=make_payload())

        with pytest.raises(NotFoundError):
            expense_service.get(user_id=2, expense_id=created.id)

    def test_get_raises_not_found_for_missing_id(self, expense_service):
        with pytest.raises(NotFoundError):
            expense_service.get(user_id=1, expense_id=999)


class TestUpdate:
    def test_update_changes_only_provided_fields(self, expense_service):
        created = expense_service.create(user_id=1, payload=make_payload(description="original"))

        updated = expense_service.update(
            user_id=1, expense_id=created.id, payload=ExpenseUpdate(amount=Decimal("75.00"))
        )

        assert updated.amount == Decimal("75.00")
        assert updated.description == "original"  # untouched

    def test_update_can_clear_description(self, expense_service):
        created = expense_service.create(user_id=1, payload=make_payload(description="original"))

        updated = expense_service.update(
            user_id=1, expense_id=created.id, payload=ExpenseUpdate(description=None)
        )

        # description was explicitly sent as null, so it must be cleared -
        # not left untouched the way an omitted field would be.
        assert updated.description is None

    def test_update_raises_not_found_for_another_users_expense(self, expense_service):
        created = expense_service.create(user_id=1, payload=make_payload())

        with pytest.raises(NotFoundError):
            expense_service.update(
                user_id=2, expense_id=created.id, payload=ExpenseUpdate(amount=Decimal("1"))
            )

    def test_update_rejects_non_positive_amount(self):
        with pytest.raises(Exception):
            ExpenseUpdate(amount=Decimal("0"))


class TestDelete:
    def test_delete_removes_expense(self, expense_service):
        created = expense_service.create(user_id=1, payload=make_payload())

        expense_service.delete(user_id=1, expense_id=created.id)

        with pytest.raises(NotFoundError):
            expense_service.get(user_id=1, expense_id=created.id)

    def test_delete_raises_not_found_for_another_users_expense(self, expense_service):
        created = expense_service.create(user_id=1, payload=make_payload())

        with pytest.raises(NotFoundError):
            expense_service.delete(user_id=2, expense_id=created.id)


class TestList:
    def test_list_is_scoped_to_user(self, expense_service):
        expense_service.create(user_id=1, payload=make_payload())
        expense_service.create(user_id=2, payload=make_payload())

        result = expense_service.list_for_user(user_id=1, **list_kwargs())

        assert result.total == 1

    def test_list_filters_by_category(self, expense_service):
        expense_service.create(user_id=1, payload=make_payload(category=ExpenseCategory.FOOD))
        expense_service.create(user_id=1, payload=make_payload(category=ExpenseCategory.RENT))

        result = expense_service.list_for_user(user_id=1, **list_kwargs(category=ExpenseCategory.RENT))

        assert result.total == 1
        assert result.items[0].category == ExpenseCategory.RENT

    def test_list_filters_by_date_range(self, expense_service):
        expense_service.create(user_id=1, payload=make_payload(date=date(2026, 6, 15)))
        expense_service.create(user_id=1, payload=make_payload(date=date(2026, 7, 15)))

        result = expense_service.list_for_user(
            user_id=1, **list_kwargs(start_date=date(2026, 7, 1), end_date=date(2026, 7, 31))
        )

        assert result.total == 1
        assert result.items[0].date == date(2026, 7, 15)

    def test_list_filters_by_amount_range(self, expense_service):
        expense_service.create(user_id=1, payload=make_payload(amount=Decimal("10.00")))
        expense_service.create(user_id=1, payload=make_payload(amount=Decimal("100.00")))

        result = expense_service.list_for_user(user_id=1, **list_kwargs(min_amount=Decimal("50")))

        assert result.total == 1
        assert result.items[0].amount == Decimal("100.00")

    def test_list_searches_description(self, expense_service):
        expense_service.create(user_id=1, payload=make_payload(description="weekend groceries"))
        expense_service.create(user_id=1, payload=make_payload(description="electricity bill"))

        result = expense_service.list_for_user(user_id=1, **list_kwargs(search="electricity"))

        assert result.total == 1
        assert "electricity" in result.items[0].description

    def test_list_paginates(self, expense_service):
        for i in range(5):
            expense_service.create(user_id=1, payload=make_payload(date=date(2026, 7, i + 1)))

        page_1 = expense_service.list_for_user(user_id=1, **list_kwargs(page=1, page_size=2))

        assert page_1.total == 5
        assert page_1.total_pages == 3
        assert len(page_1.items) == 2

    def test_list_sorts_by_amount_ascending(self, expense_service):
        expense_service.create(user_id=1, payload=make_payload(amount=Decimal("30.00")))
        expense_service.create(user_id=1, payload=make_payload(amount=Decimal("10.00")))
        expense_service.create(user_id=1, payload=make_payload(amount=Decimal("20.00")))

        result = expense_service.list_for_user(
            user_id=1, **list_kwargs(sort_by="amount", sort_order=SortOrder.ASC)
        )

        assert [item.amount for item in result.items] == [
            Decimal("10.00"),
            Decimal("20.00"),
            Decimal("30.00"),
        ]


class TestReporting:
    def test_total_for_month_sums_only_that_month(self, expense_service):
        expense_service.create(user_id=1, payload=make_payload(amount=Decimal("40.00"), date=date(2026, 7, 5)))
        expense_service.create(user_id=1, payload=make_payload(amount=Decimal("999.00"), date=date(2026, 6, 5)))

        total = expense_service.total_for_month(user_id=1, year=2026, month=7)

        assert total == Decimal("40.00")

    def test_category_breakdown_for_month(self, expense_service):
        expense_service.create(
            user_id=1, payload=make_payload(category=ExpenseCategory.FOOD, amount=Decimal("40.00"), date=date(2026, 7, 5))
        )
        expense_service.create(
            user_id=1, payload=make_payload(category=ExpenseCategory.RENT, amount=Decimal("800.00"), date=date(2026, 7, 6))
        )

        breakdown = expense_service.category_breakdown_for_month(user_id=1, year=2026, month=7)

        assert breakdown["food"] == Decimal("40.00")
        assert breakdown["rent"] == Decimal("800.00")
