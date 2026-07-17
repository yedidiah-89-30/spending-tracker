"""Dashboard endpoint.

Single summary endpoint for now. As Income/Expenses/Budgets/Savings/
Subscriptions land in later sprints, this stays the one place the
frontend calls for the landing-page overview - only DashboardService's
internals change.
"""

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.dependencies.auth import get_current_active_user
from app.dependencies.dashboard import get_dashboard_service
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummary,
    summary="Get the dashboard overview for a given month",
    description=(
        "Returns total income, total expenses, net profit/loss, total "
        "savings, and recent transactions for the given month/year "
        "(defaults to the current month). Requires a valid access token.\n\n"
        "**Note:** income, expenses, savings, and subscriptions data "
        "sources are not wired up yet (see `pending_features` in the "
        "response) - those fields will start reflecting real data as "
        "later sprints land, without any change to this endpoint's shape."
    ),
)
def get_dashboard_summary(
    month: int = Query(default_factory=lambda: date.today().month, ge=1, le=12, description="1-12"),
    year: int = Query(default_factory=lambda: date.today().year, ge=2000, le=2100),
    current_user: User = Depends(get_current_active_user),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
) -> DashboardSummary:
    return dashboard_service.get_summary(current_user, month=month, year=year)
