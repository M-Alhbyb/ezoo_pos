import pytest

@pytest.mark.anyio
async def test_no_negative_stock(async_client):
    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 1
    })
    product = res.json()

    res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product["id"], "quantity": 2}]
    })

    assert res.status_code != 200
