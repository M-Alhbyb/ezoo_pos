import pytest
from decimal import Decimal

@pytest.mark.anyio
async def test_profit_consistency(async_client):
    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 10
    })
    product = res.json()

    res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product["id"], "quantity": 1}]
    })
    sale = res.json()

    res = await async_client.get(f"/api/sales/{sale['id']}")
    data = res.json()

    profit = Decimal(str(data["total"])) - Decimal(str(data.get("total_cost", 0)))

    assert profit == Decimal(str(data.get("profit", 0)))

@pytest.mark.anyio
async def test_sale_reversal(async_client):
    # create product
    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 5
    })
    product = res.json()

    # create sale
    res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product["id"], "quantity": 2}]
    })
    sale = res.json()

    # reverse
    res = await async_client.post(f"/api/sales/{sale['id']}/reverse")
    assert res.status_code == 200

    # stock restored
    res = await async_client.get(f"/api/products/{product['id']}")
    data = res.json()

    assert data["stock_quantity"] == 5
