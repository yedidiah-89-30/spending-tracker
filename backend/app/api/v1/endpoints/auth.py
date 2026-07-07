"""Authentication endpoints.

Business logic lives entirely in AuthService - these routes only: validate
input (via Pydantic), apply rate limiting, call the service, and shape the
HTTP response. See app/services/auth_service.py for the actual rules.
"""

from fastapi import APIRouter, Depends, Request, status

from app.dependencies.auth import get_auth_service, get_current_active_user
from app.models.user import User
from app.schemas.auth import AuthResponse, LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenPair
from app.schemas.user import UserRead
from app.services.auth_service import AuthService
from app.utils.rate_limit import check_rate_limit

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new account",
    description=(
        "Creates a new user account and immediately logs them in, returning "
        "an access token, a refresh token, and the created user profile. "
        "Emails are case-insensitively unique; passwords must be at least "
        "8 characters and contain at least one letter and one digit."
    ),
)
def register(
    payload: RegisterRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    check_rate_limit(f"register:{request.client.host}", max_requests=10, window_seconds=60)
    user = auth_service.register(payload)
    tokens = auth_service.issue_token_pair(user)
    return AuthResponse(**tokens.model_dump(), user=UserRead.model_validate(user))


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in with email and password",
    description=(
        "Exchanges valid credentials for a new access token + refresh token "
        "pair. Rate-limited per client IP to slow down brute-force attempts."
    ),
)
def login(
    payload: LoginRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthResponse:
    check_rate_limit(f"login:{request.client.host}", max_requests=10, window_seconds=60)
    user = auth_service.authenticate(payload)
    tokens = auth_service.issue_token_pair(user)
    return AuthResponse(**tokens.model_dump(), user=UserRead.model_validate(user))


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Exchange a refresh token for a new token pair",
    description=(
        "Validates the given refresh token and, if valid and not already "
        "used/revoked, rotates it: the old refresh token is revoked and a "
        "brand new access + refresh token pair is returned. Reusing an "
        "already-rotated refresh token is treated as invalid."
    ),
)
def refresh(
    payload: RefreshRequest,
    request: Request,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPair:
    check_rate_limit(f"refresh:{request.client.host}", max_requests=30, window_seconds=60)
    return auth_service.refresh(payload.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a refresh token",
    description=(
        "Revokes the given refresh token so it can no longer be used to "
        "obtain new access tokens. Idempotent: calling it with an already "
        "invalid token still returns 204."
    ),
)
def logout(
    payload: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    auth_service.logout(payload.refresh_token)


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the currently authenticated user's profile",
    description="Requires a valid access token in the Authorization: Bearer header.",
)
def read_current_user(current_user: User = Depends(get_current_active_user)) -> UserRead:
    return UserRead.model_validate(current_user)
