def register_payload(email="ada@example.com", password="Sup3rSecret1"):
    return {"email": email, "full_name": "Ada Lovelace", "password": password}


class TestRegisterEndpoint:
    def test_register_returns_201_with_tokens_and_user(self, client):
        response = client.post("/api/v1/auth/register", json=register_payload())

        assert response.status_code == 201
        body = response.json()
        assert body["user"]["email"] == "ada@example.com"
        assert "hashed_password" not in body["user"]
        assert body["access_token"]
        assert body["refresh_token"]

    def test_register_rejects_duplicate_email(self, client):
        client.post("/api/v1/auth/register", json=register_payload())

        response = client.post("/api/v1/auth/register", json=register_payload())

        assert response.status_code == 409

    def test_register_rejects_weak_password(self, client):
        response = client.post("/api/v1/auth/register", json=register_payload(password="short"))

        assert response.status_code == 422


class TestLoginEndpoint:
    def test_login_succeeds_with_correct_credentials(self, client):
        client.post("/api/v1/auth/register", json=register_payload())

        response = client.post(
            "/api/v1/auth/login", json={"email": "ada@example.com", "password": "Sup3rSecret1"}
        )

        assert response.status_code == 200
        assert response.json()["access_token"]

    def test_login_fails_with_wrong_password(self, client):
        client.post("/api/v1/auth/register", json=register_payload())

        response = client.post(
            "/api/v1/auth/login", json={"email": "ada@example.com", "password": "WrongPass1"}
        )

        assert response.status_code == 401


class TestRefreshEndpoint:
    def test_refresh_rotates_tokens(self, client):
        register_response = client.post("/api/v1/auth/register", json=register_payload())
        old_refresh_token = register_response.json()["refresh_token"]

        response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})

        assert response.status_code == 200
        assert response.json()["refresh_token"] != old_refresh_token

    def test_reusing_rotated_refresh_token_fails(self, client):
        register_response = client.post("/api/v1/auth/register", json=register_payload())
        old_refresh_token = register_response.json()["refresh_token"]
        client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})

        response = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh_token})

        assert response.status_code == 401


class TestLogoutEndpoint:
    def test_logout_then_refresh_fails(self, client):
        register_response = client.post("/api/v1/auth/register", json=register_payload())
        refresh_token = register_response.json()["refresh_token"]

        logout_response = client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token})
        assert logout_response.status_code == 204

        refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert refresh_response.status_code == 401


class TestMeEndpoint:
    def test_me_requires_authentication(self, client):
        response = client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_me_returns_current_user_with_valid_token(self, client):
        register_response = client.post("/api/v1/auth/register", json=register_payload())
        access_token = register_response.json()["access_token"]

        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        assert response.json()["email"] == "ada@example.com"

    def test_me_rejects_garbage_token(self, client):
        response = client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
        )

        assert response.status_code == 401
