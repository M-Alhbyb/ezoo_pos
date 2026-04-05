import pytest

@pytest.mark.anyio
async def test_partner_distribution(async_client):
    # create partner
    res = await async_client.post("/api/partners", json={
        "name": "Ali",
        "percentage": "10"
    })
    partner = res.json()

    # simulate project profit
    await async_client.post("/api/projects", json={
        "name": "proj",
        "selling_price": "1000",
        "cost": "0",
        "status": "completed"
    })

    res = await async_client.post("/api/partners/distribute", json={})
    data = res.json()

    assert data["distributions"][0]["amount"] == "100"

@pytest.mark.anyio
async def test_no_double_distribution(async_client):
    await async_client.post("/api/partners/distribute", json={})
    res = await async_client.post("/api/partners/distribute", json={})

    assert res.status_code != 200
