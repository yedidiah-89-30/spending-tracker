"""Low-level security primitives: password hashing and JWT encode/decode.

Deliberately framework-agnostic (no FastAPI imports) so it can be unit
tested in isolation and reused by any service that needs it.
"""

import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import jwt
from passlib.context import CryptContext

from app.config.settings import get_settings

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TokenType = Literal["access", "refresh"]


def hash_password(plain_password: str) -> str:
    """Hash a plaintext password with bcrypt. Never log or persist the
    plaintext value anywhere in the call chain."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_token(token: str) -> str:
    """Refresh tokens are bearer secrets just like passwords, so they're
    stored hashed - a stolen DB dump alone can't be replayed as a valid
    refresh token."""
    return pwd_context.hash(token)


def verify_token_hash(token: str, token_hash: str) -> bool:
    return pwd_context.verify(token, token_hash)


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    jti = secrets.token_hex(16)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": expires_at,
        "jti": jti,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return token, jti, expires_at


def create_access_token(user_id: int) -> str:
    token, _jti, _exp = _create_token(
        subject=str(user_id),
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return token


def create_refresh_token(user_id: int) -> tuple[str, str, datetime]:
    """Returns (raw_token, jti, expires_at). The raw token goes to the
    client; the service layer persists only jti + a hash of the token."""
    return _create_token(
        subject=str(user_id),
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """Raises jose.JWTError (or a subclass) on invalid/expired tokens.
    Callers translate that into a 401 - this module stays HTTP-agnostic."""
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
