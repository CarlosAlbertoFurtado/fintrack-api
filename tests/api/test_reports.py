import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestReportsSummary:
    async def test_summary_returns_structure(
        self, client: AsyncClient, auth_headers: dict,
    ):
        resp = await client.get("/api/reports/summary", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_income" in data
        assert "total_expenses" in data
        assert "balance" in data

    async def test_summary_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/reports/summary")
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestCategoryBreakdown:
    async def test_breakdown_returns_list(
        self, client: AsyncClient, auth_headers: dict,
    ):
        resp = await client.get("/api/reports/by-category", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)


@pytest.mark.asyncio
class TestMonthlyTrend:
    async def test_trend_returns_data(
        self, client: AsyncClient, auth_headers: dict,
    ):
        resp = await client.get(
            "/api/reports/monthly-trend", headers=auth_headers,
        )
        assert resp.status_code == 200
        assert "data" in resp.json()


@pytest.mark.asyncio
class TestHealthCheck:
    async def test_health(self, client: AsyncClient):
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
