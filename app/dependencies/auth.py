from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService

# tokenUrl is only used to populate the Swagger "Authorize" button - actual
# token issuance happens at /api/v1/auth/login, not at this path.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login", auto_error=False)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_refresh_token_repository(db: Session = Depends(get_db)) -> RefreshTokenRepository:
    return RefreshTokenRepository(db)


def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository),
    refresh_token_repo: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> AuthService:
    return AuthService(user_repo, refresh_token_repo)


def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    """Resolves the bearer access token on every protected request into a
    User row. Raises 401 for anything wrong with the token; deliberately
    does not distinguish "expired" from "malformed" from "wrong type" in
    the response body, to avoid giving an attacker a debugging oracle."""
    credentials_error = UnauthorizedError("Could not validate credentials.")
    if token is None:
        raise credentials_error

    try:
        claims = decode_token(token)
    except JWTError:
        raise credentials_error

    if claims.get("type") != "access":
        raise credentials_error

    user_id_raw = claims.get("sub")
    if user_id_raw is None:
        raise credentials_error

    try:
        user_id = int(user_id_raw)
    except (TypeError, ValueError):
        raise credentials_error

    user = user_repo.get(user_id)
    if user is None or not user.is_active:
        raise credentials_error

    return user


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    """Separate seam from get_current_user so future checks (e.g. email
    verified, subscription active) can be added here without touching every
    route that just needs "is this a valid, active user"."""
    return user
