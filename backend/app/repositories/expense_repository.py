from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.expense import Expense, ExpenseCategory
from app.repositories.base import BaseRepository
from app.schemas.common import SortOrder

_SORTABLE_COLUMNS = {
    "date": Expense.date,
    "amount": Expense.amount,
    "category": Expense.category,
    "created_at": Expense.created_at,
}


class ExpenseRepository(BaseRepository[Expense]):
    def __init__(self, db: Session):
        super().__init__(db, Expense)

    def get_for_user(self, expense_id: int, user_id: int) -> Expense | None:
        stmt = select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_user(
        self,
        user_id: int,
        *,
        page: int,
        page_size: int,
        category: ExpenseCategory | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        search: str | None = None,
        sort_by: str = "date",
        sort_order: SortOrder = SortOrder.DESC,
    ) -> tuple[list[Expense], int]:
        stmt = select(Expense).where(Expense.user_id == user_id)

        if category is not None:
            stmt = stmt.where(Expense.category == category)
        if start_date is not None:
            stmt = stmt.where(Expense.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Expense.date <= end_date)
        if min_amount is not None:
            stmt = stmt.where(Expense.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(Expense.amount <= max_amount)
        if search:
            stmt = stmt.where(Expense.description.ilike(f"%{search}%"))

        total = self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar_one()

        sort_column = _SORTABLE_COLUMNS.get(sort_by, Expense.date)
        stmt = stmt.order_by(sort_column.desc() if sort_order == SortOrder.DESC else sort_column.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def sum_for_month(self, user_id: int, year: int, month: int) -> Decimal:
        stmt = select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.user_id == user_id,
            func.extract("year", Expense.date) == year,
            func.extract("month", Expense.date) == month,
        )
        return self.db.execute(stmt).scalar_one()

    def sum_by_category_for_month(self, user_id: int, year: int, month: int) -> dict[str, Decimal]:
        """Category -> total for the month. Built now so Reports/Budgets
        (later sprints) can reuse it instead of re-deriving the same
        aggregation - see README's "Future Improvements" note."""
        stmt = (
            select(Expense.category, func.coalesce(func.sum(Expense.amount), 0))
            .where(
                Expense.user_id == user_id,
                func.extract("year", Expense.date) == year,
                func.extract("month", Expense.date) == month,
            )
            .group_by(Expense.category)
        )
        return {category.value: total for category, total in self.db.execute(stmt).all()}

    def list_recent(self, user_id: int, limit: int = 5) -> list[Expense]:
        stmt = (
            select(Expense)
            .where(Expense.user_id == user_id)
            .order_by(Expense.date.desc(), Expense.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def update(self, expense: Expense, **fields) -> Expense:
        for key, value in fields.items():
            setattr(expense, key, value)
        self.db.commit()
        self.db.refresh(expense)
        return expense
