from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: Session):
        super().__init__(db, RefreshToken)

    def get_by_jti(self, jti: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.jti == jti)
        return self.db.execute(stmt).scalar_one_or_none()

    def revoke(self, token: RefreshToken) -> None:
        token.revoked = True
        self.db.commit()

    def revoke_all_for_user(self, user_id: int) -> None:
        """Used on logout-everywhere or password-reset flows."""
        self.db.execute(
            update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
        )
        self.db.commit()

    def is_valid(self, token: RefreshToken) -> bool:
        if token.revoked:
            return False
        expires_at = token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at > datetime.now(timezone.utc)
