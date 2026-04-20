import pytest
from decimal import Decimal

@pytest.mark.anyio
async def test_sale_price_snapshot(async_client):
    # create product
    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100.00",
        "selling_price": "150.00",
        "stock_quantity": 10
    })
    product = res.json()

    # create sale
    res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product["id"], "quantity": 1}]
    })
    sale = res.json()

    # change product price
    await async_client.patch(f"/api/products/{product['id']}", json={
        "selling_price": "300.00"
    })

    # fetch sale
    res = await async_client.get(f"/api/sales/{sale['id']}")
    data = res.json()

    assert data["items"][0]["price"] == "150.00"

@pytest.mark.anyio
async def test_vat_snapshot(async_client):
    # set VAT 10%
    await async_client.post("/api/settings/vat", json={
        "enabled": True,
        "type": "percent",
        "value": "10"
    })

    # create product
    res = await async_client.post("/api/products", json={
        "name": "battery",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 10
    })
    product = res.json()

    # create sale
    res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product["id"], "quantity": 1}]
    })
    sale = res.json()

    # change VAT
    await async_client.post("/api/settings/vat", json={
        "enabled": True,
        "type": "percent",
        "value": "20"
    })

    res = await async_client.get(f"/api/sales/{sale['id']}")
    data = res.json()

    assert data["vat_percentage"] == "10"
