# EZOO POS Backend

Core POS system with product catalog, inventory tracking, and sale processing.

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- pip

### Installation

1. Create virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Enable PostgreSQL extensions:
```bash
psql -U postgres -d ezoo_pos -f setup_extensions.sql
```

5. Run migrations:
```bash
alembic upgrade head
```

6. Start the server:
```bash
uvicorn main:app --reload
```

## Project Structure

```
backend/
├── app/
│   ├── core/           # Configuration, database, calculations
│   ├── models/         # SQLAlchemy models
│   ├── schemas/        # Pydantic schemas
│   ├── modules/        # Business modules (products, pos, inventory)
│   └── websocket/      # WebSocket manager
├── tests/
│   ├── unit/           # Unit tests
│   └── integration/    # Integration tests
├── alembic/            # Database migrations
└── main.py             # FastAPI application
```

## Database Migrations

### Create a new migration:
```bash
alembic revision --autogenerate -m "Description of change"
```

### Apply migrations:
```bash
alembic upgrade head
```

### Rollback one migration:
```bash
alembic downgrade -1
```

## Testing

Run tests with pytest:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=app --cov-report=html
```

## API Documentation

Once the server is running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Calculation Engine

All financial calculations use the `Decimal` type with `ROUND_HALF_UP` rounding to ensure accuracy.

### Key Functions:

- `round_currency(value)`: Round to 2 decimal places
- `calculate_line_total(quantity, unit_price)`: Calculate line item total
- `calculate_fee_amount(fee_value, fee_type, subtotal)`: Calculate fee (fixed or percentage)
- `calculate_vat(subtotal, fees_total, vat_enabled, vat_type, vat_value)`: Calculate VAT
- `calculate_sale_total(items, fees, vat_enabled, vat_type, vat_value)`: Full sale breakdown

## Constitution Compliance

This implementation follows the EZOO POS Constitution:

- **I. Financial Accuracy**: All monetary values use `Decimal`, never `float`
- **II. Single Source of Truth**: PostgreSQL is the only data store
- **III. Explicit Over Implicit**: All fees store type, value, and amount
- **IV. Immutable Records**: Sales are immediately confirmed, reversals create new records
- **VI. Data Integrity**: CHECK constraints enforce non-negative values
- **VII. Backend Authority**: All validation in backend service layer
- **VII. Input Validation**: Pydantic schemas validate all inputs

## Next Steps

After Phase 1 setup:

1. Install Python dependencies
2. Set up PostgreSQL database
3. Run migrations
4. Verify calculation engine tests pass
5. Proceed to Phase 2 (Foundational Components)