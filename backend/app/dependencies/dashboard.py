from fastapi import Depends

from app.dependencies.expense import get_expense_repository
from app.dependencies.income import get_income_repository
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.income_repository import IncomeRepository
from app.services.dashboard_service import DashboardService


def get_dashboard_service(
    income_repository: IncomeRepository = Depends(get_income_repository),
    expense_repository: ExpenseRepository = Depends(get_expense_repository),
) -> DashboardService:
    return DashboardService(income_repository, expense_repository)
