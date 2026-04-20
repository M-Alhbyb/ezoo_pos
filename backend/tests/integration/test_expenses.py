import pytest

@pytest.mark.anyio
async def test_percentage_expense(async_client):
    res = await async_client.post("/api/projects", json={
        "name": "solar project",
        "selling_price": "1000"
    })
    project = res.json()

    await async_client.post("/api/expenses", json={
        "project_id": project["id"],
        "type": "percent",
        "value": "10"
    })

    res = await async_client.get(f"/api/projects/{project['id']}")
    data = res.json()

    assert float(data["total_expenses"]) == 100.0
