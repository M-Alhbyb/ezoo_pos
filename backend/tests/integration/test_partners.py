import pytest

@pytest.mark.anyio
async def test_partner_distribution(async_client):
    # create partner
    res = await async_client.post("/api/partners", json={
        "name": "Ali",
        "profit_percentage": "10"
    })
    partner = res.json()

    # simulate project profit
    res = await async_client.post("/api/projects", json={
        "name": "proj",
        "selling_price": "1000",
        "cost": "0",
        "status": "draft"
    })
    proj_id = res.json()["id"]
    await async_client.post(f"/api/projects/{proj_id}/complete")

    res = await async_client.post("/api/partners/distribute", json={})
    data = res.json()

    assert float(data["distributions"][0]["amount"]) == 100.0

@pytest.mark.anyio
async def test_no_double_distribution(async_client):
    await async_client.post("/api/partners/distribute", json={})
    res = await async_client.post("/api/partners/distribute", json={})

    assert res.status_code != 200
