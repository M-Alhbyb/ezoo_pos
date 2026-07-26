"""
Invariant tests for partner payout accounting.

Verifies that:
1. PartnerDistribution is the sole source of truth for the partners report
2. Sale profit accrual (PartnerWalletTransaction) is NOT double-counted
3. Wallet balance is NOT affected by manual distributions
"""
from decimal import Decimal

import pytest


@pytest.mark.anyio
async def test_partner_distribution_report_nonzero(async_client):
    """
    A partner with 20% share on a product sold at margin 100
    produces a non-zero payout in the partners report.
    """
    # Create partner
    p_res = await async_client.post("/api/partners", json={
        "name": "Report Test Partner",
        "share_percentage": "20",
        "investment_amount": "500",
    })
    assert p_res.status_code == 201
    partner_id = p_res.json()["id"]

    # Create category + product
    cat = await async_client.post("/api/categories", json={"name": "Inv Cat"})
    cat_id = cat.json()["id"]

    prod = await async_client.post("/api/products", json={
        "name": "High Margin Product",
        "base_price": "50",
        "selling_price": "150",
        "stock_quantity": 10,
        "category_id": cat_id,
        "partner_id": partner_id,
    })
    assert prod.status_code == 201
    product_id = prod.json()["id"]

    # Payment method
    pm = await async_client.post(
        "/api/settings/payment-methods",
        json={"name": "Cash", "is_active": True},
    )
    pm_id = pm.json()["id"]

    # Manual distribution of 1000 profit -> partner gets 20% = 200
    dist = await async_client.post(
        "/api/partners/distribute", json={"profit": "1000.00"}
    )
    assert dist.status_code == 200
    dist_data = dist.json()
    assert float(dist_data["distributions"][0]["amount"]) == 200.0

    # Report must show 200
    report = await async_client.get("/api/reports/partners")
    assert report.status_code == 200
    data = report.json()
    assert float(data["total_payout"]) == 200.0
    assert any(
        p["partner_name"] == "Report Test Partner"
        and float(p["total_payout"]) == 200.0
        for p in data["payouts_by_partner"]
    )


@pytest.mark.anyio
async def test_sale_plus_distribution_no_double_count(async_client):
    """
    A sale credits the wallet; a subsequent distribution does NOT add to the
    report total. The report reads only PartnerDistribution records.
    """
    # Setup
    p_res = await async_client.post("/api/partners", json={
        "name": "No Double Partner",
        "share_percentage": "20",
        "investment_amount": "500",
    })
    partner_id = p_res.json()["id"]

    cat = await async_client.post("/api/categories", json={"name": "DC Cat"})
    cat_id = cat.json()["id"]

    prod = await async_client.post("/api/products", json={
        "name": "DC Product",
        "base_price": "50",
        "selling_price": "150",
        "stock_quantity": 10,
        "category_id": cat_id,
        "partner_id": partner_id,
    })
    product_id = prod.json()["id"]

    pm = await async_client.post(
        "/api/settings/payment-methods",
        json={"name": "Cash", "is_active": True},
    )
    pm_id = pm.json()["id"]

    # Sale: 2 units, profit per unit = 150-50 = 100, partner gets 20% = 40
    sale = await async_client.post("/api/sales", json={
        "items": [{"product_id": product_id, "quantity": 2}],
        "payment_method_id": pm_id,
    })
    assert sale.status_code == 201

    # Report after sale: should be 0 (no PartnerDistribution records yet)
    r1 = await async_client.get("/api/reports/partners")
    assert float(r1.json()["total_payout"]) == Decimal("0.00")

    # Wallet after sale: should be 40 (automatic accrual)
    w1 = await async_client.get(f"/api/partners/{partner_id}/wallet")
    assert float(w1.json()["current_balance"]) == 40.0

    # Manual distribution of 200 profit -> partner gets 40
    dist = await async_client.post(
        "/api/partners/distribute", json={"profit": "200.00"}
    )
    assert dist.status_code == 200

    # Report after distribution: should be exactly 40, not 80
    r2 = await async_client.get("/api/reports/partners")
    assert float(r2.json()["total_payout"]) == Decimal("40.00")

    # Wallet after distribution: must still be 40 (distribution doesn't touch wallet)
    w2 = await async_client.get(f"/api/partners/{partner_id}/wallet")
    assert float(w2.json()["current_balance"]) == 40.0


@pytest.mark.anyio
async def test_wallet_balance_not_affected_by_distribution(async_client):
    """
    balance_after in PartnerWalletTransaction must NOT move when a
    manual distribution is recorded.
    """
    p_res = await async_client.post("/api/partners", json={
        "name": "Wallet Dir Partner",
        "share_percentage": "10",
        "investment_amount": "100",
    })
    partner_id = p_res.json()["id"]

    cat = await async_client.post("/api/categories", json={"name": "WD Cat"})
    cat_id = cat.json()["id"]

    prod = await async_client.post("/api/products", json={
        "name": "WD Product",
        "base_price": "100",
        "selling_price": "200",
        "stock_quantity": 10,
        "category_id": cat_id,
        "partner_id": partner_id,
    })
    product_id = prod.json()["id"]

    pm = await async_client.post(
        "/api/settings/payment-methods",
        json={"name": "Cash", "is_active": True},
    )
    pm_id = pm.json()["id"]

    # Sale: profit = 200-100 = 100, partner gets 10% = 10
    await async_client.post("/api/sales", json={
        "items": [{"product_id": product_id, "quantity": 1}],
        "payment_method_id": pm_id,
    })

    wallet_before = await async_client.get(f"/api/partners/{partner_id}/wallet")
    balance_before = float(wallet_before.json()["current_balance"])
    assert balance_before == 10.0

    # Distribution should not move wallet
    await async_client.post(
        "/api/partners/distribute", json={"profit": "500.00"}
    )
    # 10% of 500 = 50 -> PartnerDistribution.payout_amount = 50
    # But wallet balance must remain at 10

    wallet_after = await async_client.get(f"/api/partners/{partner_id}/wallet")
    balance_after = float(wallet_after.json()["current_balance"])
    assert balance_after == balance_before, (
        f"Wallet balance moved from {balance_before} to {balance_after} "
        f"after distribution — distribution must not affect wallet"
    )
