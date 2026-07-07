def register_and_login(client, email="ada@example.com"):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Ada Lovelace", "password": "Sup3rSecret1"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def income_payload(**overrides):
    payload = {
        "category": "salary",
        "amount": "1500.00",
        "description": "July salary",
        "date": "2026-07-01",
    }
    payload.update(overrides)
    return payload


class TestCreateIncomeEndpoint:
    def test_requires_authentication(self, client):
        response = client.post("/api/v1/income", json=income_payload())

        assert response.status_code == 401

    def test_creates_income_entry(self, client):
        headers = register_and_login(client)

        response = client.post("/api/v1/income", json=income_payload(), headers=headers)

        assert response.status_code == 201
        body = response.json()
        assert body["amount"] == "1500.00"
        assert body["category"] == "salary"
        assert "id" in body

    def test_rejects_non_positive_amount(self, client):
        headers = register_and_login(client)

        response = client.post(
            "/api/v1/income", json=income_payload(amount="0"), headers=headers
        )

        assert response.status_code == 422

    def test_rejects_invalid_category(self, client):
        headers = register_and_login(client)

        response = client.post(
            "/api/v1/income", json=income_payload(category="bonus"), headers=headers
        )

        assert response.status_code == 422


class TestGetIncomeEndpoint:
    def test_returns_owned_income(self, client):
        headers = register_and_login(client)
        created = client.post("/api/v1/income", json=income_payload(), headers=headers).json()

        response = client.get(f"/api/v1/income/{created['id']}", headers=headers)

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_404_for_another_users_income(self, client):
        headers_a = register_and_login(client, email="a@example.com")
        headers_b = register_and_login(client, email="b@example.com")
        created = client.post("/api/v1/income", json=income_payload(), headers=headers_a).json()

        response = client.get(f"/api/v1/income/{created['id']}", headers=headers_b)

        assert response.status_code == 404

    def test_404_for_nonexistent_income(self, client):
        headers = register_and_login(client)

        response = client.get("/api/v1/income/999999", headers=headers)

        assert response.status_code == 404


class TestUpdateIncomeEndpoint:
    def test_patch_updates_only_sent_fields(self, client):
        headers = register_and_login(client)
        created = client.post("/api/v1/income", json=income_payload(), headers=headers).json()

        response = client.patch(
            f"/api/v1/income/{created['id']}", json={"amount": "2000.00"}, headers=headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["amount"] == "2000.00"
        assert body["description"] == "July salary"

    def test_404_for_another_users_income(self, client):
        headers_a = register_and_login(client, email="a@example.com")
        headers_b = register_and_login(client, email="b@example.com")
        created = client.post("/api/v1/income", json=income_payload(), headers=headers_a).json()

        response = client.patch(
            f"/api/v1/income/{created['id']}", json={"amount": "1.00"}, headers=headers_b
        )

        assert response.status_code == 404


class TestDeleteIncomeEndpoint:
    def test_delete_then_get_returns_404(self, client):
        headers = register_and_login(client)
        created = client.post("/api/v1/income", json=income_payload(), headers=headers).json()

        delete_response = client.delete(f"/api/v1/income/{created['id']}", headers=headers)
        assert delete_response.status_code == 204

        get_response = client.get(f"/api/v1/income/{created['id']}", headers=headers)
        assert get_response.status_code == 404

    def test_404_for_another_users_income(self, client):
        headers_a = register_and_login(client, email="a@example.com")
        headers_b = register_and_login(client, email="b@example.com")
        created = client.post("/api/v1/income", json=income_payload(), headers=headers_a).json()

        response = client.delete(f"/api/v1/income/{created['id']}", headers=headers_b)

        assert response.status_code == 404


class TestListIncomeEndpoint:
    def test_lists_only_own_income_with_pagination_envelope(self, client):
        headers_a = register_and_login(client, email="a@example.com")
        headers_b = register_and_login(client, email="b@example.com")
        client.post("/api/v1/income", json=income_payload(), headers=headers_a)
        client.post("/api/v1/income", json=income_payload(), headers=headers_b)

        response = client.get("/api/v1/income", headers=headers_a)

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["page"] == 1
        assert len(body["items"]) == 1

    def test_filters_by_category(self, client):
        headers = register_and_login(client)
        client.post("/api/v1/income", json=income_payload(category="salary"), headers=headers)
        client.post("/api/v1/income", json=income_payload(category="freelance"), headers=headers)

        response = client.get("/api/v1/income?category=freelance", headers=headers)

        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["category"] == "freelance"

    def test_filters_by_date_range(self, client):
        headers = register_and_login(client)
        client.post("/api/v1/income", json=income_payload(date="2026-06-15"), headers=headers)
        client.post("/api/v1/income", json=income_payload(date="2026-07-15"), headers=headers)

        response = client.get(
            "/api/v1/income?start_date=2026-07-01&end_date=2026-07-31", headers=headers
        )

        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["date"] == "2026-07-15"

    def test_pagination_params_are_validated(self, client):
        headers = register_and_login(client)

        response = client.get("/api/v1/income?page_size=1000", headers=headers)

        assert response.status_code == 422
