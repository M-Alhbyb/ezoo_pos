# Quickstart: Partner Profit Tracking

**Feature**: 005-partner-profit-tracking
**Date**: 2026-04-08

## Prerequisites

- PostgreSQL database running
- Backend virtual environment activated
- Database migrations applied
- At least one product and partner created in the system

## Quick Reference

### 1. Create a Partner

```bash
curl -X POST http://localhost:8000/api/v1/partners \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Solar Partner Inc",
    "share_percentage": 15.00,
    "investment_amount": 10000.00
  }'
```

### 2. Create a Product Assignment

Assign 10 units of a product to the partner with 20% profit share (overrides partner default):

```bash
curl -X POST http://localhost:8000/api/v1/partners/assignments \
  -H "Content-Type: application/json" \
  -d '{
    "partner_id": "PARTNER_UUID",
    "product_id": "PRODUCT_UUID",
    "assigned_quantity": 10,
    "share_percentage": 20.00
  }'
```

### 3. Check Assignment Status

```bash
curl http://localhost:8000/api/v1/partners/assignments/{assignment_id}
```

Response shows:
- `assigned_quantity`: Original quantity assigned
- `remaining_quantity`: Units still unsold
- `status`: 'active' or 'fulfilled'

### 4. View Product Inventory with Assignments

```bash
curl http://localhost:8000/api/v1/products
```

Each product includes an `assignment` field showing which partner has units assigned.

### 5. Make a Sale

Use existing POS workflow. Partner profit is automatically calculated and credited.

```bash
curl -X POST http://localhost:8000/api/v1/sales \
  -H "Content-Type: application/json" \
  -d '{
    "payment_method_id": "PAYMENT_METHOD_UUID",
    "items": [
      {
        "product_id": "PRODUCT_UUID",
        "quantity": 3,
        "unit_price": 350.00
      }
    ]
  }'
```

**What happens automatically**:
1. System checks if product has active assignment
2. If assigned: calculates partner profit (3 × 350 × 20% = $210)
3. Credits partner wallet
4. Decreases `remaining_quantity` from 10 to 7
5. If `remaining_quantity` hits 0: status → 'fulfilled'

### 6. Check Partner Wallet Balance

```bash
curl http://localhost:8000/api/v1/partners/{partner_id}/wallet
```

Response:
```json
{
  "partner_id": "UUID",
  "partner_name": "Solar Partner Inc",
  "current_balance": "210.00",
  "last_transaction_at": "2026-04-08T14:30:00Z"
}
```

### 7. View Partner Transaction History

```bash
curl http://localhost:8000/api/v1/partners/{partner_id}/wallet/transactions
```

Shows all profit credits and manual adjustments.

### 8. Manual Wallet Adjustment (Admin)

Add or subtract from wallet for payouts, corrections, etc.:

```bash
curl -X POST http://localhost:8000/api/v1/partners/{partner_id}/wallet/adjust \
  -H "Content-Type: application/json" \
  -d '{
    "amount": -100.00,
    "description": "Payout for March 2026"
  }'
```

## Common Workflows

### Workflow 1: Partner Profit Setup

```python
# 1. Register partner
partner = await partner_service.create_partner(
    PartnerCreate(
        name="Solar Partner Inc",
        share_percentage=15.00,
        investment_amount=5000.00
    )
)

# 2. Assign products to partner
assignment = await partner_service.create_assignment(
    ProductAssignmentCreate(
        partner_id=partner.id,
        product_id=solar_panel_id,
        assigned_quantity=20,
        share_percentage=18.00  # Override default
    )
)

# 3. Partner profit automatically credited on sale
# No manual action needed
```

### Workflow 2: Monitor Partner Earnings

```python
# Get current balance
balance = await partner_service.get_wallet_balance(partner_id)

# Get transaction history
transactions = await partner_service.get_wallet_transactions(
    partner_id=partner_id,
    limit=50,
    offset=0
)

# Calculate earnings this month
from datetime import datetime, timedelta
month_start = datetime.now(timezone.utc).replace(day=1)
month_transactions = await partner_service.get_wallet_transactions(
    partner_id=partner_id,
    start_date=month_start,
    transaction_type='sale_profit'
)
month_earnings = sum(tx.amount for tx in month_transactions)
```

### Workflow 3: Close Fulfilled Assignments

```python
# List fulfilled assignments for cleanup/reporting
fulfilled = await partner_service.get_assignments(
    status='fulfilled',
    limit=100
)

# Business logic: archive, report, or analyze
for assignment in fulfilled:
    print(f"{assignment.product_name}: {assignment.assigned_quantity} units "
          f"fulfilled on {assignment.fulfilled_at}")
```

## Error Handling

### Insufficient Assigned Quantity

If trying to sell more units than assigned:

```json
{
  "detail": "Insufficient assigned quantity",
  "errors": [
    {
      "field": "quantity",
      "message": "Cannot sell 15 units: only 10 assigned"
    }
  ]
}
```

### Duplicate Active Assignment

If product already has active assignment:

```json
{
  "detail": "Product already has an active assignment",
  "errors": [
    {
      "field": "product_id",
      "message": "Product Solar Panel already assigned to Partner X"
    }
  ]
}
```

### Assignment Fulfilled

If trying to update a fulfilled assignment:

```json
{
  "detail": "Cannot update fulfilled assignment",
  "errors": [
    {
      "field": "status",
      "message": "Assignment is fulfilled and cannot be modified"
    }
  ]
}
```

## Performance Tips

1. **Batch Assignment Queries**: Use pagination (`limit`, `offset`) when listing assignments
2. **Index Usage**: Queries on `(product_id, status)` use composite index
3. **Balance Calculation**: O(1) lookup using `balance_after` on latest transaction
4. **Concurrent Sales**: Sorted lock ordering prevents deadlocks

## Testing

### Unit Tests

```bash
pytest tests/unit/test_partner_profit_service.py -v
pytest tests/unit/test_product_assignment.py -v
```

### Integration Tests

```bash
pytest tests/integration/test_partner_wallet_flow.py -v
```

### Test Coverage

- Assignment creation, update, deletion
- Profit calculation on sale
- Wallet balance tracking
- Concurrent transaction safety
- Assignment fulfillment
- Manual wallet adjustments

## Constitution Compliance

Every operation follows constitution principles:

- **Financial Accuracy**: DECIMAL for all monetary values
- **Immutable Records**: Transactions cannot be updated/deleted
- **Explicit Values**: share_percentage stored with each transaction
- **Audit Trail**: Every transaction has `balance_after` snapshot

## Next Steps

After implementing this feature:

1. Run database migrations
2. Verify assignment creation flow
3. Test profit calculation with small sale
4. Verify wallet balance update
5. Test concurrent sales scenario
6. Review transaction history
7. Test manual adjustment

## Troubleshooting

### Balance Not Updating

Check:
1. Assignment exists and status = 'active'
2. Product being sold has assignment
3. `remaining_quantity` > 0
4. Transaction was committed (no rollback)

### Assignment Not Found During Sale

This is normal behavior - not all products have assignments. System keeps full profit for unassigned products.

### Deadlock Errors

Ensure lock ordering: always sort partner IDs before acquiring `SELECT FOR UPDATE`.

## Support

For implementation questions, refer to:
- `data-model.md` for database schema
- `contracts/api.md` for API specifications
- `contracts/schemas.md` for Pydantic schemas
- `research.md` for technical decisions