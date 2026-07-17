from datetime import date
from decimal import Decimal

import pytest

from app.core.exceptions import NotFoundError
from app.models.income import IncomeCategory
from app.repositories.income_repository import IncomeRepository
from app.schemas.common import SortOrder
from app.schemas.income import IncomeCreate, IncomeUpdate
from app.services.income_service import IncomeService


@pytest.fixture()
def income_service(db_session):
    return IncomeService(IncomeRepository(db_session))


def make_payload(**overrides):
    defaults = dict(
        category=IncomeCategory.SALARY,
        amount=Decimal("1000.00"),
        description="July salary",
        date=date(2026, 7, 1),
    )
    defaults.update(overrides)
    return IncomeCreate(**defaults)


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
    def test_create_persists_and_returns_income(self, income_service):
        income = income_service.create(user_id=1, payload=make_payload())

        assert income.id is not None
        assert income.amount == Decimal("1000.00")
        assert income.category == IncomeCategory.SALARY

    def test_create_stores_the_category_as_its_lowercase_value_not_its_enum_name(
        self, income_service, db_session
    ):
        """Regression test: SQLAlchemy's Enum type binds a Python enum
        column using the member NAME ("SALARY") by default, not its value
        ("salary"), unless values_callable is set on the column (see
        app/models/income.py). That mismatch against the DB's
        ck_income_category_valid CHECK constraint (which only allows the
        lowercase values) caused every income creation to fail against
        real Postgres, even though this exact flow passed against SQLite
        here - because the CHECK constraint used to exist only in the
        Alembic migration, not on the ORM model, so SQLite never enforced
        it. Both gaps are now closed: the model carries the same
        CheckConstraint (see Income.__table_args__), and this test reads
        the raw column value back to confirm it's the lowercase slug."""
        from sqlalchemy import text

        income_service.create(user_id=1, payload=make_payload())

        raw_value = db_session.execute(text("SELECT category FROM income")).scalar_one()

        assert raw_value == "salary"
        assert raw_value != "SALARY"


class TestGet:
    def test_get_returns_owned_income(self, income_service):
        created = income_service.create(user_id=1, payload=make_payload())

        fetched = income_service.get(user_id=1, income_id=created.id)

        assert fetched.id == created.id

    def test_get_raises_not_found_for_another_users_income(self, income_service):
        created = income_service.create(user_id=1, payload=make_payload())

        with pytest.raises(NotFoundError):
            income_service.get(user_id=2, income_id=created.id)

    def test_get_raises_not_found_for_missing_id(self, income_service):
        with pytest.raises(NotFoundError):
            income_service.get(user_id=1, income_id=999)


class TestUpdate:
    def test_update_changes_only_provided_fields(self, income_service):
        created = income_service.create(user_id=1, payload=make_payload(description="original"))

        updated = income_service.update(
            user_id=1, income_id=created.id, payload=IncomeUpdate(amount=Decimal("2000.00"))
        )

        assert updated.amount == Decimal("2000.00")
        assert updated.description == "original"  # untouched

    def test_update_can_clear_description(self, income_service):
        created = income_service.create(user_id=1, payload=make_payload(description="original"))

        updated = income_service.update(
            user_id=1, income_id=created.id, payload=IncomeUpdate(description=None)
        )

        # description was explicitly sent as null, so it must be cleared -
        # not left untouched the way an omitted field would be.
        assert updated.description is None

    def test_update_raises_not_found_for_another_users_income(self, income_service):
        created = income_service.create(user_id=1, payload=make_payload())

        with pytest.raises(NotFoundError):
            income_service.update(
                user_id=2, income_id=created.id, payload=IncomeUpdate(amount=Decimal("1"))
            )


class TestDelete:
    def test_delete_removes_income(self, income_service):
        created = income_service.create(user_id=1, payload=make_payload())

        income_service.delete(user_id=1, income_id=created.id)

        with pytest.raises(NotFoundError):
            income_service.get(user_id=1, income_id=created.id)

    def test_delete_raises_not_found_for_another_users_income(self, income_service):
        created = income_service.create(user_id=1, payload=make_payload())

        with pytest.raises(NotFoundError):
            income_service.delete(user_id=2, income_id=created.id)


class TestList:
    def test_list_is_scoped_to_user(self, income_service):
        income_service.create(user_id=1, payload=make_payload())
        income_service.create(user_id=2, payload=make_payload())

        result = income_service.list_for_user(user_id=1, **list_kwargs())

        assert result.total == 1

    def test_list_filters_by_category(self, income_service):
        income_service.create(user_id=1, payload=make_payload(category=IncomeCategory.SALARY))
        income_service.create(user_id=1, payload=make_payload(category=IncomeCategory.FREELANCE))

        result = income_service.list_for_user(user_id=1, **list_kwargs(category=IncomeCategory.FREELANCE))

        assert result.total == 1
        assert result.items[0].category == IncomeCategory.FREELANCE

    def test_list_filters_by_amount_range(self, income_service):
        income_service.create(user_id=1, payload=make_payload(amount=Decimal("50.00")))
        income_service.create(user_id=1, payload=make_payload(amount=Decimal("500.00")))

        result = income_service.list_for_user(user_id=1, **list_kwargs(min_amount=Decimal("100")))

        assert result.total == 1
        assert result.items[0].amount == Decimal("500.00")

    def test_list_searches_description(self, income_service):
        income_service.create(user_id=1, payload=make_payload(description="freelance web project"))
        income_service.create(user_id=1, payload=make_payload(description="monthly paycheck"))

        result = income_service.list_for_user(user_id=1, **list_kwargs(search="paycheck"))

        assert result.total == 1
        assert "paycheck" in result.items[0].description

    def test_list_paginates(self, income_service):
        for i in range(5):
            income_service.create(user_id=1, payload=make_payload(date=date(2026, 7, i + 1)))

        page_1 = income_service.list_for_user(user_id=1, **list_kwargs(page=1, page_size=2))

        assert page_1.total == 5
        assert page_1.total_pages == 3
        assert len(page_1.items) == 2

    def test_list_sorts_by_amount_ascending(self, income_service):
        income_service.create(user_id=1, payload=make_payload(amount=Decimal("300.00")))
        income_service.create(user_id=1, payload=make_payload(amount=Decimal("100.00")))
        income_service.create(user_id=1, payload=make_payload(amount=Decimal("200.00")))

        result = income_service.list_for_user(
            user_id=1, **list_kwargs(sort_by="amount", sort_order=SortOrder.ASC)
        )

        assert [item.amount for item in result.items] == [
            Decimal("100.00"),
            Decimal("200.00"),
            Decimal("300.00"),
        ]
