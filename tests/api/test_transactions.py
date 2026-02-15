import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCreateTransaction:
    async def test_create_with_category(self, client: AsyncClient, auth_headers: dict):
        # first get user's default categories
        cats = await client.get("/api/categories", headers=auth_headers)
        category_id = cats.json()[0]["id"] if cats.json() else None

        resp = await client.post("/api/transactions", headers=auth_headers, json={
            "description": "Supermercado Extra",
            "amount": 150.50,
            "type": "EXPENSE",
            "category_id": category_id,
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["description"] == "Supermercado Extra"
        assert data["amount"] == 150.50

    async def test_create_without_category(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/transactions", headers=auth_headers, json={
            "description": "Freelance project",
            "amount": 3000.0,
            "type": "INCOME",
        })
        assert resp.status_code == 201

    async def test_create_invalid_amount(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/transactions", headers=auth_headers, json={
            "description": "Bad amount",
            "amount": -10,
            "type": "EXPENSE",
        })
        assert resp.status_code == 422

    async def test_create_unauthorized(self, client: AsyncClient):
        resp = await client.post("/api/transactions", json={
            "description": "No auth",
            "amount": 100,
            "type": "EXPENSE",
        })
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestListTransactions:
    async def test_list_empty(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get("/api/transactions", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data

    async def test_list_with_type_filter(self, client: AsyncClient, auth_headers: dict):
        # create one income
        await client.post("/api/transactions", headers=auth_headers, json={
            "description": "Salary", "amount": 5000, "type": "INCOME",
        })
        resp = await client.get(
            "/api/transactions?type=INCOME", headers=auth_headers,
        )
        assert resp.status_code == 200
        for tx in resp.json()["data"]:
            assert tx["type"] == "INCOME"

    async def test_list_pagination(self, client: AsyncClient, auth_headers: dict):
        resp = await client.get(
            "/api/transactions?page=1&limit=5", headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["limit"] == 5


@pytest.mark.asyncio
class TestDeleteTransaction:
    async def test_delete_own(self, client: AsyncClient, auth_headers: dict):
        create = await client.post("/api/transactions", headers=auth_headers, json={
            "description": "To delete", "amount": 10, "type": "EXPENSE",
        })
        tx_id = create.json()["id"]
        resp = await client.delete(f"/api/transactions/{tx_id}", headers=auth_headers)
        assert resp.status_code == 204

    async def test_delete_nonexistent(self, client: AsyncClient, auth_headers: dict):
        resp = await client.delete(
            "/api/transactions/00000000-0000-0000-0000-000000000000",
            headers=auth_headers,
        )
        assert resp.status_code == 404
