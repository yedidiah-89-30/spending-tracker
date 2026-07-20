from datetime import date


def register_and_get_token(client, email="ada@example.com", currency=None):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "full_name": "Ada Lovelace", "password": "Sup3rSecret1"},
    )
    return response.json()["access_token"]


class TestDashboardSummaryEndpoint:
    def test_requires_authentication(self, client):
        response = client.get("/api/v1/dashboard/summary")

        assert response.status_code == 401

    def test_returns_zeroed_summary_for_new_user(self, client):
        token = register_and_get_token(client)

        response = client.get(
            "/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["total_income"] == "0.00"
        assert body["total_expenses"] == "0.00"
        assert body["net_profit_loss"] == "0.00"
        assert body["total_savings"] == "0.00"
        assert body["recent_transactions"] == []
        assert len(body["income_data"]) == 6
        assert all(point["amount"] == 0.0 for point in body["income_data"])
        assert set(body["pending_features"]) == {
            "savings_goals",
            "subscriptions",
        }
        assert "income" not in body["pending_features"]
        assert "expenses" not in body["pending_features"]

    def test_defaults_to_current_month_and_year(self, client):
        token = register_and_get_token(client)
        today = date.today()

        response = client.get(
            "/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"}
        )

        body = response.json()
        assert body["month"] == today.month
        assert body["year"] == today.year

    def test_accepts_explicit_month_and_year(self, client):
        token = register_and_get_token(client)

        response = client.get(
            "/api/v1/dashboard/summary?month=3&year=2025",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["month"] == 3
        assert body["year"] == 2025

    def test_rejects_invalid_month(self, client):
        token = register_and_get_token(client)

        response = client.get(
            "/api/v1/dashboard/summary?month=13",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 422

    def test_reflects_the_authenticated_users_currency(self, client):
        token = register_and_get_token(client)

        response = client.get(
            "/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"}
        )

        # Default currency for a freshly registered user, set in the User model.
        assert response.json()["currency"] == "$"


class TestIncomeDataField:
    def test_income_data_shape_matches_the_frontend_chart_contract(self, client):
        token = register_and_get_token(client)

        response = client.get(
            "/api/v1/dashboard/summary", headers={"Authorization": f"Bearer {token}"}
        )

        point = response.json()["income_data"][0]
        assert set(point.keys()) == {"month", "amount"}
        assert isinstance(point["month"], str)
        assert isinstance(point["amount"], (int, float))

    def test_income_data_reflects_real_income_entries(self, client):
        token = register_and_get_token(client)
        headers = {"Authorization": f"Bearer {token}"}
        client.post(
            "/api/v1/income",
            json={"category": "salary", "amount": "1500.00", "date": "2026-07-05"},
            headers=headers,
        )

        response = client.get("/api/v1/dashboard/summary?month=7&year=2026", headers=headers)

        income_data = response.json()["income_data"]
        july_point = next(p for p in income_data if p["month"] == "Jul 2026")
        assert july_point["amount"] == 1500.0
