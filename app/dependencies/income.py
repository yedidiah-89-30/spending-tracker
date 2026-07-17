from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.income_repository import IncomeRepository
from app.services.income_service import IncomeService


def get_income_repository(db: Session = Depends(get_db)) -> IncomeRepository:
    return IncomeRepository(db)


def get_income_service(
    income_repository: IncomeRepository = Depends(get_income_repository),
) -> IncomeService:
    return IncomeService(income_repository)
