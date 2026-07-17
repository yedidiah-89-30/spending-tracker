import pytest

from app.core.exceptions import ConflictError, UnauthorizedError
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import AuthService


@pytest.fixture()
def auth_service(db_session):
    return AuthService(UserRepository(db_session), RefreshTokenRepository(db_session))


class TestRegister:
    def test_register_creates_user_with_hashed_password(self, auth_service):
        user = auth_service.register(
            RegisterRequest(email="Ada@Example.com", full_name="Ada Lovelace", password="Sup3rSecret")
        )

        assert user.id is not None
        assert user.email == "ada@example.com"  # normalized to lowercase
        assert user.hashed_password != "Sup3rSecret"

    def test_register_rejects_duplicate_email(self, auth_service):
        auth_service.register(
            RegisterRequest(email="ada@example.com", full_name="Ada", password="Sup3rSecret")
        )

        with pytest.raises(ConflictError):
            auth_service.register(
                RegisterRequest(email="ADA@example.com", full_name="Ada Again", password="An0therPass")
            )


class TestAuthenticate:
    def test_authenticate_succeeds_with_correct_credentials(self, auth_service):
        auth_service.register(
            RegisterRequest(email="ada@example.com", full_name="Ada", password="Sup3rSecret")
        )

        user = auth_service.authenticate(LoginRequest(email="ada@example.com", password="Sup3rSecret"))

        assert user.email == "ada@example.com"

    def test_authenticate_fails_with_wrong_password(self, auth_service):
        auth_service.register(
            RegisterRequest(email="ada@example.com", full_name="Ada", password="Sup3rSecret")
        )

        with pytest.raises(UnauthorizedError):
            auth_service.authenticate(LoginRequest(email="ada@example.com", password="WrongPass1"))

    def test_authenticate_fails_for_unknown_email(self, auth_service):
        with pytest.raises(UnauthorizedError):
            auth_service.authenticate(LoginRequest(email="ghost@example.com", password="Whatever1"))


class TestTokenLifecycle:
    def test_refresh_rotates_token_and_invalidates_old_one(self, auth_service):
        user = auth_service.register(
            RegisterRequest(email="ada@example.com", full_name="Ada", password="Sup3rSecret")
        )
        first_pair = auth_service.issue_token_pair(user)

        second_pair = auth_service.refresh(first_pair.refresh_token)

        assert second_pair.refresh_token != first_pair.refresh_token
        with pytest.raises(UnauthorizedError):
            auth_service.refresh(first_pair.refresh_token)  # reuse of rotated token must fail

    def test_logout_revokes_refresh_token(self, auth_service):
        user = auth_service.register(
            RegisterRequest(email="ada@example.com", full_name="Ada", password="Sup3rSecret")
        )
        pair = auth_service.issue_token_pair(user)

        auth_service.logout(pair.refresh_token)

        with pytest.raises(UnauthorizedError):
            auth_service.refresh(pair.refresh_token)

    def test_logout_is_idempotent_for_already_invalid_token(self, auth_service):
        # Should not raise even though this token was never issued.
        auth_service.logout("not-a-real-token")
