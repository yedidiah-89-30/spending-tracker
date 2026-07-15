def register_and_login(client, email="ada@example.com"):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Ada Lovelace", "password": "Sup3rSecret1"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def expense_payload(**overrides):
    payload = {
        "category": "food",
        "amount": "50.00",
        "description": "Groceries",
        "date": "2026-07-01",
    }
    payload.update(overrides)
    return payload


class TestCreateExpenseEndpoint:
    def test_requires_authentication(self, client):
        response = client.post("/api/v1/expenses", json=expense_payload())

        assert response.status_code == 401

    def test_creates_expense_entry(self, client):
        headers = register_and_login(client)

        response = client.post("/api/v1/expenses", json=expense_payload(), headers=headers)

        assert response.status_code == 201
        body = response.json()
        assert body["amount"] == "50.00"
        assert body["category"] == "food"
        assert "id" in body

    def test_rejects_non_positive_amount(self, client):
        headers = register_and_login(client)

        response = client.post(
            "/api/v1/expenses", json=expense_payload(amount="0"), headers=headers
        )

        assert response.status_code == 422

    def test_rejects_negative_amount(self, client):
        headers = register_and_login(client)

        response = client.post(
            "/api/v1/expenses", json=expense_payload(amount="-10.00"), headers=headers
        )

        assert response.status_code == 422

    def test_rejects_invalid_category(self, client):
        headers = register_and_login(client)

        response = client.post(
            "/api/v1/expenses", json=expense_payload(category="vacation"), headers=headers
        )

        assert response.status_code == 422

    def test_rejects_missing_required_fields(self, client):
        headers = register_and_login(client)

        response = client.post("/api/v1/expenses", json={"amount": "10.00"}, headers=headers)

        assert response.status_code == 422


class TestGetExpenseEndpoint:
    def test_returns_owned_expense(self, client):
        headers = register_and_login(client)
        created = client.post("/api/v1/expenses", json=expense_payload(), headers=headers).json()

        response = client.get(f"/api/v1/expenses/{created['id']}", headers=headers)

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    def test_404_for_another_users_expense(self, client):
        headers_a = register_and_login(client, email="a@example.com")
        headers_b = register_and_login(client, email="b@example.com")
        created = client.post("/api/v1/expenses", json=expense_payload(), headers=headers_a).json()

        response = client.get(f"/api/v1/expenses/{created['id']}", headers=headers_b)

        assert response.status_code == 404

    def test_404_for_nonexistent_expense(self, client):
        headers = register_and_login(client)

        response = client.get("/api/v1/expenses/999999", headers=headers)

        assert response.status_code == 404


class TestUpdateExpenseEndpoint:
    def test_patch_updates_only_sent_fields(self, client):
        headers = register_and_login(client)
        created = client.post("/api/v1/expenses", json=expense_payload(), headers=headers).json()

        response = client.patch(
            f"/api/v1/expenses/{created['id']}", json={"amount": "75.00"}, headers=headers
        )

        assert response.status_code == 200
        body = response.json()
        assert body["amount"] == "75.00"
        assert body["description"] == "Groceries"

    def test_patch_rejects_non_positive_amount(self, client):
        headers = register_and_login(client)
        created = client.post("/api/v1/expenses", json=expense_payload(), headers=headers).json()

        response = client.patch(
            f"/api/v1/expenses/{created['id']}", json={"amount": "0"}, headers=headers
        )

        assert response.status_code == 422

    def test_404_for_another_users_expense(self, client):
        headers_a = register_and_login(client, email="a@example.com")
        headers_b = register_and_login(client, email="b@example.com")
        created = client.post("/api/v1/expenses", json=expense_payload(), headers=headers_a).json()

        response = client.patch(
            f"/api/v1/expenses/{created['id']}", json={"amount": "1.00"}, headers=headers_b
        )

        assert response.status_code == 404


class TestDeleteExpenseEndpoint:
    def test_delete_then_get_returns_404(self, client):
        headers = register_and_login(client)
        created = client.post("/api/v1/expenses", json=expense_payload(), headers=headers).json()

        delete_response = client.delete(f"/api/v1/expenses/{created['id']}", headers=headers)
        assert delete_response.status_code == 204

        get_response = client.get(f"/api/v1/expenses/{created['id']}", headers=headers)
        assert get_response.status_code == 404

    def test_404_for_another_users_expense(self, client):
        headers_a = register_and_login(client, email="a@example.com")
        headers_b = register_and_login(client, email="b@example.com")
        created = client.post("/api/v1/expenses", json=expense_payload(), headers=headers_a).json()

        response = client.delete(f"/api/v1/expenses/{created['id']}", headers=headers_b)

        assert response.status_code == 404


class TestListExpensesEndpoint:
    def test_lists_only_own_expenses_with_pagination_envelope(self, client):
        headers_a = register_and_login(client, email="a@example.com")
        headers_b = register_and_login(client, email="b@example.com")
        client.post("/api/v1/expenses", json=expense_payload(), headers=headers_a)
        client.post("/api/v1/expenses", json=expense_payload(), headers=headers_b)

        response = client.get("/api/v1/expenses", headers=headers_a)

        assert response.status_code == 200
        body = response.json()
        assert body["total"] == 1
        assert body["page"] == 1
        assert len(body["items"]) == 1

    def test_filters_by_category(self, client):
        headers = register_and_login(client)
        client.post("/api/v1/expenses", json=expense_payload(category="food"), headers=headers)
        client.post("/api/v1/expenses", json=expense_payload(category="rent"), headers=headers)

        response = client.get("/api/v1/expenses?category=rent", headers=headers)

        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["category"] == "rent"

    def test_filters_by_date_range(self, client):
        headers = register_and_login(client)
        client.post("/api/v1/expenses", json=expense_payload(date="2026-06-15"), headers=headers)
        client.post("/api/v1/expenses", json=expense_payload(date="2026-07-15"), headers=headers)

        response = client.get(
            "/api/v1/expenses?start_date=2026-07-01&end_date=2026-07-31", headers=headers
        )

        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["date"] == "2026-07-15"

    def test_filters_by_amount_range(self, client):
        headers = register_and_login(client)
        client.post("/api/v1/expenses", json=expense_payload(amount="5.00"), headers=headers)
        client.post("/api/v1/expenses", json=expense_payload(amount="500.00"), headers=headers)

        response = client.get("/api/v1/expenses?min_amount=100", headers=headers)

        body = response.json()
        assert body["total"] == 1
        assert body["items"][0]["amount"] == "500.00"

    def test_searches_description(self, client):
        headers = register_and_login(client)
        client.post(
            "/api/v1/expenses", json=expense_payload(description="weekend groceries"), headers=headers
        )
        client.post(
            "/api/v1/expenses", json=expense_payload(description="electricity bill"), headers=headers
        )

        response = client.get("/api/v1/expenses?search=electricity", headers=headers)

        body = response.json()
        assert body["total"] == 1
        assert "electricity" in body["items"][0]["description"]

    def test_sorts_by_amount(self, client):
        headers = register_and_login(client)
        client.post("/api/v1/expenses", json=expense_payload(amount="30.00"), headers=headers)
        client.post("/api/v1/expenses", json=expense_payload(amount="10.00"), headers=headers)
        client.post("/api/v1/expenses", json=expense_payload(amount="20.00"), headers=headers)

        response = client.get("/api/v1/expenses?sort_by=amount&sort_order=asc", headers=headers)

        body = response.json()
        assert [item["amount"] for item in body["items"]] == ["10.00", "20.00", "30.00"]

    def test_pagination_params_are_validated(self, client):
        headers = register_and_login(client)

        response = client.get("/api/v1/expenses?page_size=1000", headers=headers)

        assert response.status_code == 422

    def test_invalid_sort_by_is_rejected(self, client):
        headers = register_and_login(client)

        response = client.get("/api/v1/expenses?sort_by=not_a_column", headers=headers)

        assert response.status_code == 422
