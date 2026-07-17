from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.expense_repository import ExpenseRepository
from app.services.expense_service import ExpenseService


def get_expense_repository(db: Session = Depends(get_db)) -> ExpenseRepository:
    return ExpenseRepository(db)


def get_expense_service(
    expense_repository: ExpenseRepository = Depends(get_expense_repository),
) -> ExpenseService:
    return ExpenseService(expense_repository)
