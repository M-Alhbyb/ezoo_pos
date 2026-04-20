import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_project_completion_freezes_profit(async_client: AsyncClient):
    # 1. Create a project
    res = await async_client.post("/api/projects", json={
        "name": "Immutable Project",
        "selling_price": "2000.00",
        "cost": "500.00"
    })
    assert res.status_code == 201
    project = res.json()
    project_id = project["id"]

    # 2. Add an expense
    expense_res = await async_client.post("/api/expenses", json={
        "project_id": project_id,
        "type": "fixed",
        "value": "150.00"
    })
    assert expense_res.status_code == 201

    # 3. Add a percentage expense
    percent_exp_res = await async_client.post("/api/expenses", json={
        "project_id": project_id,
        "type": "percent",
        "value": "5.00" # 5% of 2000 = 100
    })
    assert percent_exp_res.status_code == 201

    # 4. Mark project completed
    complete_res = await async_client.post(f"/api/projects/{project_id}/complete")
    assert complete_res.status_code == 200
    completed_data = complete_res.json()

    # selling=2000, items_cost=500. 
    # expenses: 150(fixed) + 100(5% of 2000) = 250
    # profit = 2000 - (500 + 250) = 1250
    assert float(completed_data["total_expenses"]) == 250.0
    assert float(completed_data["profit"]) == 1250.0
    assert completed_data["status"] == "completed"

