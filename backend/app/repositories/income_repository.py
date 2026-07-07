from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.income import Income, IncomeCategory
from app.repositories.base import BaseRepository
from app.schemas.common import SortOrder

_SORTABLE_COLUMNS = {
    "date": Income.date,
    "amount": Income.amount,
    "category": Income.category,
    "created_at": Income.created_at,
}


class IncomeRepository(BaseRepository[Income]):
    def __init__(self, db: Session):
        super().__init__(db, Income)

    def get_for_user(self, income_id: int, user_id: int) -> Income | None:
        stmt = select(Income).where(Income.id == income_id, Income.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_for_user(
        self,
        user_id: int,
        *,
        page: int,
        page_size: int,
        category: IncomeCategory | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        min_amount: Decimal | None = None,
        max_amount: Decimal | None = None,
        search: str | None = None,
        sort_by: str = "date",
        sort_order: SortOrder = SortOrder.DESC,
    ) -> tuple[list[Income], int]:
        stmt = select(Income).where(Income.user_id == user_id)

        if category is not None:
            stmt = stmt.where(Income.category == category)
        if start_date is not None:
            stmt = stmt.where(Income.date >= start_date)
        if end_date is not None:
            stmt = stmt.where(Income.date <= end_date)
        if min_amount is not None:
            stmt = stmt.where(Income.amount >= min_amount)
        if max_amount is not None:
            stmt = stmt.where(Income.amount <= max_amount)
        if search:
            stmt = stmt.where(Income.description.ilike(f"%{search}%"))

        total = self.db.execute(
            select(func.count()).select_from(stmt.subquery())
        ).scalar_one()

        sort_column = _SORTABLE_COLUMNS.get(sort_by, Income.date)
        stmt = stmt.order_by(sort_column.desc() if sort_order == SortOrder.DESC else sort_column.asc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)

        items = list(self.db.execute(stmt).scalars().all())
        return items, total

    def sum_for_month(self, user_id: int, year: int, month: int) -> Decimal:
        stmt = select(func.coalesce(func.sum(Income.amount), 0)).where(
            Income.user_id == user_id,
            func.extract("year", Income.date) == year,
            func.extract("month", Income.date) == month,
        )
        return self.db.execute(stmt).scalar_one()

    def list_recent(self, user_id: int, limit: int = 5) -> list[Income]:
        stmt = (
            select(Income)
            .where(Income.user_id == user_id)
            .order_by(Income.date.desc(), Income.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def update(self, income: Income, **fields) -> Income:
        for key, value in fields.items():
            setattr(income, key, value)
        self.db.commit()
        self.db.refresh(income)
        return income
