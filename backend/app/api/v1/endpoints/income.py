"""Income endpoints.

Standard CRUD + list with pagination/filtering/sorting. Every route
requires authentication and every query is scoped to the current user -
see IncomeService/IncomeRepository for the ownership guarantees.
"""

from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.auth import get_current_active_user
from app.dependencies.income import get_income_service
from app.models.income import IncomeCategory
from app.models.user import User
from app.schemas.common import PaginatedResponse, SortOrder
from app.schemas.income import IncomeCreate, IncomeRead, IncomeUpdate
from app.services.income_service import IncomeService

router = APIRouter(prefix="/income", tags=["Income"])


@router.post(
    "",
    response_model=IncomeRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log a new income entry",
    description="`amount` must be greater than zero. `category` is one of: salary, business, freelance, other.",
)
def create_income(
    payload: IncomeCreate,
    current_user: User = Depends(get_current_active_user),
    income_service: IncomeService = Depends(get_income_service),
) -> IncomeRead:
    income = income_service.create(current_user.id, payload)
    return IncomeRead.model_validate(income)


@router.get(
    "",
    response_model=PaginatedResponse[IncomeRead],
    summary="List income entries with pagination, filtering, and sorting",
    description=(
        "Filters: `category`, `start_date`/`end_date` (inclusive), "
        "`min_amount`/`max_amount`, `search` (matches description). "
        "Sort with `sort_by` (date | amount | category | created_at) and "
        "`sort_order` (asc | desc)."
    ),
)
def list_income(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: IncomeCategory | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    min_amount: Decimal | None = Query(default=None, ge=0),
    max_amount: Decimal | None = Query(default=None, ge=0),
    search: str | None = Query(default=None, max_length=500),
    sort_by: str = Query(default="date", pattern="^(date|amount|category|created_at)$"),
    sort_order: SortOrder = Query(default=SortOrder.DESC),
    current_user: User = Depends(get_current_active_user),
    income_service: IncomeService = Depends(get_income_service),
) -> PaginatedResponse[IncomeRead]:
    return income_service.list_for_user(
        current_user.id,
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


@router.get(
    "/{income_id}",
    response_model=IncomeRead,
    summary="Get a single income entry",
)
def get_income(
    income_id: int,
    current_user: User = Depends(get_current_active_user),
    income_service: IncomeService = Depends(get_income_service),
) -> IncomeRead:
    income = income_service.get(current_user.id, income_id)
    return IncomeRead.model_validate(income)


@router.patch(
    "/{income_id}",
    response_model=IncomeRead,
    summary="Update an income entry",
    description="Partial update - only send the fields you want to change.",
)
def update_income(
    income_id: int,
    payload: IncomeUpdate,
    current_user: User = Depends(get_current_active_user),
    income_service: IncomeService = Depends(get_income_service),
) -> IncomeRead:
    income = income_service.update(current_user.id, income_id, payload)
    return IncomeRead.model_validate(income)


@router.delete(
    "/{income_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an income entry",
)
def delete_income(
    income_id: int,
    current_user: User = Depends(get_current_active_user),
    income_service: IncomeService = Depends(get_income_service),
) -> None:
    income_service.delete(current_user.id, income_id)
