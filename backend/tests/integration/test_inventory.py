import pytest

@pytest.mark.anyio
async def test_no_negative_stock(async_client):
    print("--- POST /api/products ---")
    res = await async_client.post("/api/products", json={
        "name": "panel",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 1
    })
    print("--- POST /api/products response:", res.status_code, res.text)
    product = res.json()

    print("--- POST /api/sales ---")
    res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product["id"], "quantity": 2}]
    })
    print("--- POST /api/sales response:", res.status_code)

    assert res.status_code != 200
