"""Business logic for the Expense feature.

Mirrors app/services/income_service.py's ownership/validation pattern
exactly (same conventions, same reasoning) - see that file's docstring
for the rationale on 404-not-403 and exclude_unset PATCH semantics.
"""

from datetime import date
from decimal import Decimal

from app.core.exceptions import NotFoundError
from app.models.expense import Expense, ExpenseCategory
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.common import PaginatedResponse, SortOrder
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate


class ExpenseService:
    def __init__(self, expense_repository: ExpenseRepository):
        self.expense_repository = expense_repository

    def create(self, user_id: int, payload: ExpenseCreate) -> Expense:
        expense = Expense(
            user_id=user_id,
            category=payload.category,
            amount=payload.amount,
            description=payload.description,
            date=payload.date,
        )
        return self.expense_repository.add(expense)

    def get(self, user_id: int, expense_id: int) -> Expense:
        expense = self.expense_repository.get_for_user(expense_id, user_id)
        if expense is None:
            # 404, not 403: never confirm to a caller whether an id exists
            # for a user other than themselves.
            raise NotFoundError("Expense entry not found.")
        return expense

    def list_for_user(
        self,
        user_id: int,
        *,
        page: int,
        page_size: int,
        category: ExpenseCategory | None,
        start_date: date | None,
        end_date: date | None,
        min_amount: Decimal | None,
        max_amount: Decimal | None,
        search: str | None,
        sort_by: str,
        sort_order: SortOrder,
    ) -> PaginatedResponse[ExpenseRead]:
        items, total = self.expense_repository.list_for_user(
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
            items=[ExpenseRead.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def update(self, user_id: int, expense_id: int, payload: ExpenseUpdate) -> Expense:
        expense = self.get(user_id, expense_id)
        updates = payload.model_dump(exclude_unset=True)
        return self.expense_repository.update(expense, **updates)

    def delete(self, user_id: int, expense_id: int) -> None:
        expense = self.get(user_id, expense_id)
        self.expense_repository.delete(expense)

    def total_for_month(self, user_id: int, year: int, month: int) -> Decimal:
        return self.expense_repository.sum_for_month(user_id, year, month)

    def category_breakdown_for_month(self, user_id: int, year: int, month: int) -> dict[str, Decimal]:
        return self.expense_repository.sum_by_category_for_month(user_id, year, month)

    def recent(self, user_id: int, limit: int = 5) -> list[Expense]:
        return self.expense_repository.list_recent(user_id, limit=limit)
