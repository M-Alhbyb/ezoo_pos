import pytest
from decimal import Decimal
from datetime import datetime, timedelta
from httpx import AsyncClient


@pytest.mark.anyio
async def test_sales_report(async_client: AsyncClient):
    # 1. Setup sample data
    # Create a payment method
    pm_res = await async_client.get("/api/settings/payment-methods")
    pm_data = pm_res.json()
    if not pm_data["items"]:
        await async_client.post("/api/settings/payment-methods", json={"name": "Cash", "is_active": True})
        pm_res = await async_client.get("/api/settings/payment-methods")
        pm_data = pm_res.json()
    
    pm_id = pm_data["items"][0]["id"]

    # Create a category
    cat_res = await async_client.post("/api/categories", json={"name": "Report Category"})
    category_id = cat_res.json()["id"]

    # Create a product
    prod_res = await async_client.post("/api/products", json={
        "name": "Report Product",
        "base_price": "50.00",
        "selling_price": "100.00",
        "stock_quantity": 10,
        "category_id": category_id
    })
    product_id = prod_res.json()["id"]

    # Create a sale
    sale_res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product_id, "quantity": 2}],
        "payment_method_id": pm_id
    })
    assert sale_res.status_code == 201

    # 2. Call report endpoint
    res = await async_client.get("/api/reports/sales")
    assert res.status_code == 200
    data = res.json()

    assert float(data["total_revenue"]) == 200.0
    assert float(data["total_cost"]) == 100.0
    assert float(data["total_profit"]) == 100.0
    assert data["sales_count"] == 1
    assert len(data["daily_breakdown"]) >= 1


@pytest.mark.anyio
async def test_projects_report(async_client: AsyncClient):
    # 1. Create a project
    await async_client.post("/api/projects", json={
        "name": "Analytic Project",
        "selling_price": "500.00",
        "cost": "200.00",
        "status": "in_progress"
    })

    # 2. Call report endpoint
    res = await async_client.get("/api/reports/projects")
    assert res.status_code == 200
    data = res.json()

    assert data["total_projects"] >= 1
    assert float(data["total_selling_price"]) >= 500.0
    assert any(p["name"] == "Analytic Project" for p in data["project_list"])


@pytest.mark.anyio
async def test_partners_report(async_client: AsyncClient):
    # 1. Setup partner and distribution
    # Create partner
    p_res = await async_client.post("/api/partners", json={
        "name": "Report Partner",
        "profit_percentage": "20",
        "investment_amount": "1000"
    })
    partner_id = p_res.json()["id"]

    # Create completed project with profit
    proj_res = await async_client.post("/api/projects", json={
        "name": "Profit Project",
        "selling_price": "1000.00",
        "cost": "500.00"
    })
    project_id = proj_res.json()["id"]
    await async_client.post(f"/api/projects/{project_id}/complete")

    # Distribute profit
    await async_client.post("/api/partners/distribute")

    # 2. Call report endpoint
    res = await async_client.get("/api/reports/partners")
    assert res.status_code == 200
    data = res.json()

    # 20% of 500 profit = 100 payout
    assert float(data["total_payout"]) >= 100.0
    assert any(p["partner_name"] == "Report Partner" for p in data["payouts_by_partner"])


@pytest.mark.anyio
async def test_inventory_report(async_client: AsyncClient):
    # 1. Create data to ensure movements exist
    # Create a category if not exists (or just create a unique one)
    cat_res = await async_client.post("/api/categories", json={"name": "Inventory Category"})
    category_id = cat_res.json()["id"]

    prod_res = await async_client.post("/api/products", json={
        "name": "Inventory Report Product",
        "base_price": "50.00",
        "selling_price": "100.00",
        "stock_quantity": 10,
        "category_id": category_id
    })
    product_id = prod_res.json()["id"]

    pm_res = await async_client.get("/api/settings/payment-methods")
    pm_data = pm_res.json()
    if not pm_data["items"]:
        await async_client.post("/api/settings/payment-methods", json={"name": "Cash", "is_active": True})
        pm_res = await async_client.get("/api/settings/payment-methods")
        pm_data = pm_res.json()
    
    pm_id = pm_data["items"][0]["id"]

    sale_res = await async_client.post("/api/sales", json={
        "items": [{"product_id": product_id, "quantity": 1}],
        "payment_method_id": pm_id
    })
    assert sale_res.status_code == 201
    
    # 2. Call report endpoint
    res = await async_client.get("/api/reports/inventory")
    assert res.status_code == 200
    data = res.json()

    assert data["total_movements"] >= 1
    # Check if 'sale' reason exists
    assert any(m["reason"] == "sale" for m in data["movements_by_reason"])


@pytest.mark.anyio
async def test_report_date_filtering(async_client: AsyncClient):
    # Future date that should return zero results
    future_start = (datetime.now() + timedelta(days=10)).isoformat()
    future_end = (datetime.now() + timedelta(days=11)).isoformat()

    res = await async_client.get(f"/api/reports/sales?start_date={future_start}&end_date={future_end}")
    assert res.status_code == 200
    data = res.json()

    assert float(data["total_revenue"]) == 0.0
    assert data["sales_count"] == 0
