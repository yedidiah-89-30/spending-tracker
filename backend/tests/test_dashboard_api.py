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
