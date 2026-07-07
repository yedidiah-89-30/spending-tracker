"""Business logic for the Income feature.

Every method takes user_id explicitly and every query is scoped to it -
there is no path by which one user can read/modify another user's income
rows, and a mismatched id is reported as NotFoundError (not Forbidden) so
we never confirm to an attacker that a given id exists at all.
"""

from datetime import date
from decimal import Decimal

from app.core.exceptions import NotFoundError
from app.models.income import Income, IncomeCategory
from app.repositories.income_repository import IncomeRepository
from app.schemas.common import PaginatedResponse, SortOrder
from app.schemas.income import IncomeCreate, IncomeRead, IncomeUpdate


class IncomeService:
    def __init__(self, income_repository: IncomeRepository):
        self.income_repository = income_repository

    def create(self, user_id: int, payload: IncomeCreate) -> Income:
        income = Income(
            user_id=user_id,
            category=payload.category,
            amount=payload.amount,
            description=payload.description,
            date=payload.date,
        )
        return self.income_repository.add(income)

    def get(self, user_id: int, income_id: int) -> Income:
        income = self.income_repository.get_for_user(income_id, user_id)
        if income is None:
            raise NotFoundError("Income entry not found.")
        return income

    def list_for_user(
        self,
        user_id: int,
        *,
        page: int,
        page_size: int,
        category: IncomeCategory | None,
        start_date: date | None,
        end_date: date | None,
        min_amount: Decimal | None,
        max_amount: Decimal | None,
        search: str | None,
        sort_by: str,
        sort_order: SortOrder,
    ) -> PaginatedResponse[IncomeRead]:
        items, total = self.income_repository.list_for_user(
            user_id,
            page=page,
            page_size=page_size,
            category=category,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        return PaginatedResponse.build(
            items=[IncomeRead.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update(self, user_id: int, income_id: int, payload: IncomeUpdate) -> Income:
        income = self.get(user_id, income_id)
        updates = payload.model_dump(exclude_unset=True)
        return self.income_repository.update(income, **updates)

    def delete(self, user_id: int, income_id: int) -> None:
        income = self.get(user_id, income_id)
        self.income_repository.delete(income)

    def total_for_month(self, user_id: int, year: int, month: int) -> Decimal:
        return self.income_repository.sum_for_month(user_id, year, month)

    def recent(self, user_id: int, limit: int = 5) -> list[Income]:
        return self.income_repository.list_recent(user_id, limit=limit)
