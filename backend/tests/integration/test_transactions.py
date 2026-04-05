import pytest

@pytest.mark.anyio
async def test_sale_atomicity(async_client):
    # create product
    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 5
    })
    product = res.json()

    # force failure (invalid payload)
    res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product["id"], "quantity": 10}]
    })

    assert res.status_code != 200

    # check stock unchanged
    res = await async_client.get(f"/api/products/{product['id']}")
    data = res.json()

    assert data["stock_quantity"] == 5
