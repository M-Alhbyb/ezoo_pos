# Quickstart: Partner Profit System

## Backend Setup

1. **Database migrations**:
   - Add `base_cost` column to products table
   - Create `product_assignments` table
   - Create `partner_wallet_transactions` table

2. **Environment**: Existing Python 3.11 + FastAPI

3. **Run backend**:
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

## Testing

```bash
cd backend
pytest tests/unit/test_partner_profit_service.py -v
```

## Key Flows

1. **Assign product to partner**: Admin creates product assignment via `/api/partners/{id}/products`
2. **POS sale**: Sale completion triggers profit credit to linked partner
3. **Refund**: Sale refund triggers profit reversal
4. **Dashboard**: Partner views profit via `/api/partners/{id}/wallet`