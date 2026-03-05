import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestListCategories:
    async def test_list_defaults(self, client: AsyncClient, auth_headers: dict):
        """After registration, user should have 12 default categories."""
        resp = await client.get("/api/categories", headers=auth_headers)
        assert resp.status_code == 200
        cats = resp.json()
        assert len(cats) >= 10  # at least the defaults
        assert all(c["is_default"] for c in cats)

    async def test_list_unauthorized(self, client: AsyncClient):
        resp = await client.get("/api/categories")
        assert resp.status_code == 403


@pytest.mark.asyncio
class TestCreateCategory:
    async def test_create_custom(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/categories", headers=auth_headers, json={
            "name": "Investimentos",
            "type": "INCOME",
            "color": "#10B981",
        })
        assert resp.status_code == 201
        assert resp.json()["name"] == "Investimentos"
        assert resp.json()["is_default"] is False

    async def test_create_invalid_color(self, client: AsyncClient, auth_headers: dict):
        resp = await client.post("/api/categories", headers=auth_headers, json={
            "name": "Bad Color",
            "type": "EXPENSE",
            "color": "red",  # not a hex
        })
        assert resp.status_code == 422


@pytest.mark.asyncio
class TestDeleteCategory:
    async def test_cannot_delete_default(self, client: AsyncClient, auth_headers: dict):
        cats = await client.get("/api/categories", headers=auth_headers)
        default_cat = next(c for c in cats.json() if c["is_default"])
        resp = await client.delete(
            f"/api/categories/{default_cat['id']}", headers=auth_headers,
        )
        assert resp.status_code == 400

    async def test_delete_custom(self, client: AsyncClient, auth_headers: dict):
        create = await client.post("/api/categories", headers=auth_headers, json={
            "name": "Temp", "type": "EXPENSE",
        })
        cat_id = create.json()["id"]
        resp = await client.delete(f"/api/categories/{cat_id}", headers=auth_headers)
        assert resp.status_code == 204
