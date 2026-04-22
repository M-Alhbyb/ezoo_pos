# Quick Start: Supplier Accounting System

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- PostgreSQL database
- Already running EZOO POS backend

### Backend Setup

1. **Database Migrations**
   - Create new Alembic migration for Supplier, Purchase, PurchaseItem, SupplierLedger models
   - Run migration: `alembic upgrade head`

2. **Environment Variables**
   - No new env vars required (uses existing DATABASE_URL)

3. **Run Backend**
   ```bash
   cd src
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Run Frontend**
   ```bash
   npm run dev
   ```

## Key Files to Create

### Backend

| File | Purpose |
|------|---------|
| `src/models/supplier.py` | SQLAlchemy models |
| `src/services/supplier_service.py` | Business logic |
| `src/api/suppliers.py` | API routes |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/pages/suppliers/index.tsx` | Supplier list page |
| `frontend/src/pages/suppliers/[id].tsx` | Supplier detail page |
| `frontend/src/pages/purchases/index.tsx` | Purchase list/create page |

## Testing

```bash
# Backend tests
cd src
pytest

# Lint
ruff check .
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/suppliers | List all suppliers |
| POST | /api/suppliers | Create supplier |
| GET | /api/suppliers/{id} | Get supplier details |
| POST | /api/purchases | Create purchase |
| GET | /api/purchases | List purchases |
| GET | /api/purchases/{id} | Get purchase details |
| POST | /api/suppliers/{id}/payments | Record payment |
| POST | /api/purchases/{id}/return | Return items |
| GET | /api/reports/suppliers | All suppliers summary |
| GET | /api/reports/suppliers/{id} | Supplier statement |

## First Steps

1. Create Supplier model and migration
2. Implement Supplier CRUD API
3. Create Purchase and PurchaseItem models
4. Implement Purchase creation with inventory increase
5. Implement SupplierLedger entries
6. Build payment recording
7. Build return processing
8. Create reports endpoints
9. Build frontend pages
