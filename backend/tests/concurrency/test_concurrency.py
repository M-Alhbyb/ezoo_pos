import pytest
import asyncio

@pytest.mark.anyio
async def test_overselling_stock(async_client):
    # create product with 5 stock
    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 5
    })
    product = res.json()

    async def buy():
        return await async_client.post("/api/sales", json={
            "items": [{"product_id": product["id"], "quantity": 5}]
        })

    results = await asyncio.gather(buy(), buy())

    success = [r for r in results if r.status_code == 200]
    failure = [r for r in results if r.status_code != 200]

    assert len(success) == 1
    assert len(failure) == 1

@pytest.mark.anyio
async def test_double_click_sale(async_client):
    # create product
    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 10
    })
    product = res.json()

    payload = {
        "items": [{"product_id": product["id"], "quantity": 1}],
        "idempotency_key": "abc-123"
    }

    res1 = await async_client.post("/api/sales", json=payload)
    res2 = await async_client.post("/api/sales", json=payload)

    assert res1.status_code == 200
    assert res2.status_code == 200

    # ensure only one sale exists
    res = await async_client.get("/api/sales")
    sales = res.json()

    # The backend might return {"items": [...]} or a list directly. Let's assume list or items.
    # Adjust based on real logic, but for template adherence:
    if isinstance(sales, dict) and "items" in sales:
        assert len(sales["items"]) == 1
    else:
        assert len(sales) == 1
