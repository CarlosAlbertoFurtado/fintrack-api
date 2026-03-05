import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestReportsSummary:
    async def test_summary_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/reports/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_income"] == 0
        assert data["total_expenses"] == 0
        assert data["balance"] == 0

    async def test_summary_with_transactions(self, client: AsyncClient, auth_headers: dict):
        await client.post("/api/transactions", headers=auth_headers, json={
            "description": "Salary", "amount": 5000, "type": "INCOME",
        })
        await client.post("/api/transactions", headers=auth_headers, json={
            "description": "Rent", "amount": 1500, "type": "EXPENSE",
        })
        resp = await client.get("/api/reports/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_income"] == 5000
        assert data["total_expenses"] == 1500
        assert data["balance"] == 3500
        assert data["transaction_count"] == 2

    async def test_summary_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/reports/summary")
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestCategoryBreakdown:
    async def test_breakdown_returns_list(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/reports/by-category", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestMonthlyTrend:
    async def test_trend_returns_data(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/reports/monthly-trend", headers=auth_headers)
        assert resp.status_code == 200
        assert "data" in resp.json()


@pytest.mark.asyncio
class TestHealthCheck:
    async def test_health(self, client: AsyncClient):
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
