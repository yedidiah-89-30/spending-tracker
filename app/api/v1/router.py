from fastapi import APIRouter

from app.api.v1.endpoints import auth, dashboard, expense, income

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(dashboard.router)
api_router.include_router(income.router)
api_router.include_router(expense.router)
