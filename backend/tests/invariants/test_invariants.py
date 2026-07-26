from decimal import Decimal

import pytest


@pytest.mark.anyio
async def test_profit_consistency(async_client):
    # create category
    cat = await async_client.post("/api/categories", json={"name": "Test"})
    category_id = cat.json()["id"]

    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 10,
        "category_id": category_id,
    })
    product = res.json()

    # ensure a payment method exists
    pm = await async_client.post(
        "/api/settings/payment-methods",
        json={"name": "Cash", "is_active": True},
    )
    pm_id = pm.json()["id"]

    res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product["id"], "quantity": 1}],
        "payment_method_id": pm_id,
    })
    sale = res.json()

    res = await async_client.get(f"/api/sales/{sale['id']}")
    data = res.json()

    profit = Decimal(str(data["total"])) - Decimal(str(data.get("total_cost", 0)))

    assert profit == Decimal(str(data.get("profit", 0)))

@pytest.mark.anyio
async def test_sale_reversal(async_client):
    # create category
    cat = await async_client.post("/api/categories", json={"name": "Test"})
    category_id = cat.json()["id"]

    # create product
    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 5,
        "category_id": category_id,
    })
    product = res.json()

    # ensure a payment method exists
    pm = await async_client.post(
        "/api/settings/payment-methods",
        json={"name": "Cash", "is_active": True},
    )
    pm_id = pm.json()["id"]

    # create sale
    res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product["id"], "quantity": 2}],
        "payment_method_id": pm_id,
    })
    sale = res.json()

    # reverse
    res = await async_client.post(
        f"/api/sales/{sale['id']}/reverse",
        json={"reason": "Test reversal"},
    )
    assert res.status_code == 200

    # stock restored
    res = await async_client.get(f"/api/products/{product['id']}")
    data = res.json()

    assert data["stock_quantity"] == 5
