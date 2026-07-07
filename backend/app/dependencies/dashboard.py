from fastapi import Depends

from app.dependencies.income import get_income_repository
from app.repositories.income_repository import IncomeRepository
from app.services.dashboard_service import DashboardService


def get_dashboard_service(
    income_repository: IncomeRepository = Depends(get_income_repository),
) -> DashboardService:
    return DashboardService(income_repository)
