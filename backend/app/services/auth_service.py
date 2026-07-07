"""Business logic for authentication.

Routes call into this service and never touch repositories or the ORM
directly - that separation is what lets us unit test registration/login
rules without spinning up FastAPI at all (see tests/test_auth_service.py).
"""

import logging

from jose import JWTError

from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
    verify_token_hash,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair

logger = logging.getLogger("app.auth")


class AuthService:
    def __init__(self, user_repo: UserRepository, refresh_token_repo: RefreshTokenRepository):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo

    def register(self, payload: RegisterRequest) -> User:
        if self.user_repo.email_exists(payload.email):
            # Deliberately vague (no "email" vs "password" distinction is
            # relevant here, but we do confirm existence - registration is
            # not a security-sensitive oracle the way login is).
            raise ConflictError("An account with this email already exists.")

        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        return self.user_repo.add(user)

    def authenticate(self, payload: LoginRequest) -> User:
        user = self.user_repo.get_by_email(payload.email)
        # Same error for "no such user" and "wrong password" - do not leak
        # which one it was, that would let an attacker enumerate accounts.
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise UnauthorizedError("Incorrect email or password.")
        if not user.is_active:
            raise UnauthorizedError("This account has been deactivated.")
        return user

    def issue_token_pair(self, user: User) -> TokenPair:
        access_token = create_access_token(user.id)
        refresh_token, jti, expires_at = create_refresh_token(user.id)

        token_row = RefreshToken(
            user_id=user.id,
            jti=jti,
            token_hash=hash_token(refresh_token),
            expires_at=expires_at,
        )
        self.refresh_token_repo.add(token_row)

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def refresh(self, raw_refresh_token: str) -> TokenPair:
        """Validates the refresh token, revokes it, and issues a brand new
        access+refresh pair (rotation). Rotating on every use means a
        stolen-and-reused refresh token is detectable: if the legitimate
        client tries to use the same (now-revoked) token later, that's a
        signal of compromise."""
        try:
            claims = decode_token(raw_refresh_token)
        except JWTError:
            raise UnauthorizedError("Invalid or expired refresh token.")

        if claims.get("type") != "refresh":
            raise UnauthorizedError("Invalid or expired refresh token.")

        jti = claims.get("jti")
        token_row = self.refresh_token_repo.get_by_jti(jti) if jti else None
        if token_row is None or not self.refresh_token_repo.is_valid(token_row):
            raise UnauthorizedError("Invalid or expired refresh token.")
        if not verify_token_hash(raw_refresh_token, token_row.token_hash):
            raise UnauthorizedError("Invalid or expired refresh token.")

        user = self.user_repo.get(token_row.user_id)
        if user is None or not user.is_active:
            raise UnauthorizedError("Invalid or expired refresh token.")

        self.refresh_token_repo.revoke(token_row)
        return self.issue_token_pair(user)

    def logout(self, raw_refresh_token: str) -> None:
        """Revokes a single refresh token. Best-effort: an invalid/expired
        token is treated as already logged out rather than an error, so
        clients can always call logout safely."""
        try:
            claims = decode_token(raw_refresh_token)
        except JWTError:
            return
        jti = claims.get("jti")
        if not jti:
            return
        token_row = self.refresh_token_repo.get_by_jti(jti)
        if token_row and not token_row.revoked:
            self.refresh_token_repo.revoke(token_row)
