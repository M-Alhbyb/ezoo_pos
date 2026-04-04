# Quickstart: Core POS, Products, and Inventory Management

**Feature**: 001-core-pos-products-inventory
**Estimated Time**: 2-3 weeks

## Prerequisites

- Phase 0 completed (project scaffolding, database, settings, categories, payment methods)
- Python 3.11+ installed
- PostgreSQL database running
- Node.js 18+ installed (for frontend)

## Quick Setup

### 1. Database Setup

Run Alembic migrations to create Phase 1 tables:

```bash
cd backend
alembic revision --autogenerate -m "Add Phase 1 tables: products, sales, inventory_log"
alembic upgrade head
```

**Tables created**:
- `products`
- `sales`
- `sale_items`
- `sale_fees`
- `sale_reversals`
- `inventory_log`

Also ensure `pg_trgm` extension is enabled for fast name search:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

---

### 2. Backend Structure

Create the following directories and files:

```bash
backend/app/
├── core/
│   └── calculations.py          # NEW: Financial calculation engine
├── models/
│   ├── product.py                # NEW: Product model
│   ├── sale.py                   # NEW: Sale model
│   ├── sale_item.py              # NEW: SaleItem model
│   ├── sale_fee.py               # NEW: SaleFee model
│   ├── sale_reversal.py          # NEW: SaleReversal model
│   └── inventory_log.py          # NEW: InventoryLog model
├── schemas/
│   ├── product.py                # NEW: Product Pydantic schemas
│   ├── sale.py                   # NEW: Sale Pydantic schemas
│   └── inventory.py               # NEW: Inventory Pydantic schemas
├── modules/
│   ├── products/
│   │   ├── routes.py             # NEW: Product API routes
│   │   ├── service.py            # NEW: Product business logic
│   │   └── __init__.py
│   ├── pos/
│   │   ├── routes.py             # NEW: Sale API routes
│   │   ├── service.py            # NEW: Sale business logic
│   │   └── __init__.py
│   └── inventory/
│       ├── routes.py             # NEW: Inventory API routes
│       ├── service.py            # NEW: Inventory business logic
│       └── __init__.py
└── websocket/
    └── manager.py                # UPDATE: Add stock update broadcasting
```

---

### 3. Calculation Engine

**File**: `backend/app/core/calculations.py`

```python
from decimal import Decimal, ROUND_HALF_UP
from typing import List

TWOPLACES = Decimal(10) ** -2  # 0.01

def round_currency(value: Decimal) -> Decimal:
    """Round to 2 decimal places using ROUND_HALF_UP."""
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)

def calculate_line_total(quantity: int, unit_price: Decimal) -> Decimal:
    """Calculate line total for a sale item."""
    return round_currency(quantity * unit_price)

def calculate_fee_amount(
    fee_value: Decimal,
    fee_value_type: str,
    subtotal: Decimal
) -> Decimal:
    """Calculate fee amount based on type (fixed or percent)."""
    if fee_value_type == 'fixed':
        return round_currency(fee_value)
    else:  # percent
        return round_currency(subtotal * (fee_value / Decimal(100)))

def calculate_vat(
    subtotal: Decimal,
    fees_total: Decimal,
    vat_enabled: bool,
    vat_type: str,
    vat_value: Decimal
) -> tuple[Decimal, Decimal | None]:
    """
    Calculate VAT amount based on settings.
    Returns (vat_amount, vat_rate).
    """
    if not vat_enabled:
        return Decimal('0'), None
    
    taxable_amount = subtotal + fees_total
    
    if vat_type == 'fixed':
        vat_amount = round_currency(vat_value)
    else:  # percent
        vat_amount = round_currency(taxable_amount * (vat_value / Decimal(100)))
    
    return vat_amount, vat_value

def calculate_sale_total(
    items: List[dict],
    fees: List[dict],
    vat_enabled: bool,
    vat_type: str,
    vat_value: Decimal
) -> dict:
    """
    Calculate full sale breakdown.
    Returns dict with subtotal, fees_total, vat_amount, total.
    """
    # Calculate subtotal
    subtotal = sum(
        calculate_line_total(item['quantity'], item['unit_price'])
        for item in items
    )
    
    # Calculate fees
    fees_total = sum(
        calculate_fee_amount(fee['fee_value'], fee['fee_value_type'], subtotal)
        for fee in fees
    )
    
    # Calculate VAT
    vat_amount, vat_rate = calculate_vat(
        subtotal, fees_total, vat_enabled, vat_type, vat_value
    )
    
    # Calculate total
    total = round_currency(subtotal + fees_total + vat_amount)
    
    return {
        'subtotal': subtotal,
        'fees_total': fees_total,
        'vat_amount': vat_amount,
        'vat_rate': vat_rate,
        'total': total
    }
```

---

### 4. Key Backend Endpoints

#### Products API

**File**: `backend/app/modules/products/routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.modules.products.service import ProductService

router = APIRouter(prefix="/api/products", tags=["products"])

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    return await service.create_product(product_data)

@router.get("/", response_model=list[ProductResponse])
async def list_products(
    category_id: str | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    service = ProductService(db)
    return await service.list_products(category_id=category_id, search=search)
```

#### Sales API

**File**: `backend/app/modules/pos/routes.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.sale import SaleCreate, SaleResponse, SaleCalculationRequest
from app.modules.pos.service import SaleService

router = APIRouter(prefix="/api/sales", tags=["sales"])

@router.post("/calculate", response_model=dict)
async def calculate_sale(
    calc_data: SaleCalculationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Calculate financial breakdown without creating sale."""
    service = SaleService(db)
    return await service.calculate_breakdown(calc_data)

@router.post("/", response_model=SaleResponse, status_code=201)
async def create_sale(
    sale_data: SaleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create confirmed sale with atomic stock deduction."""
    service = SaleService(db)
    return await service.create_sale(sale_data)
```

---

### 5. Frontendstructure

Create the following directories and files:

```bash
frontend/
├── app/
│   ├── pos/
│   │   └── page.tsx              # NEW: POS interface
│   └── products/
│       └── page.tsx              # NEW: Product management
├── components/
│   ├── pos/
│   │   ├── ProductSearch.tsx     # NEW: Search products by name/SKU
│   │   ├── POSCart.tsx           # NEW: Cart with items and quantities
│   │   ├── FeeEditor.tsx         # NEW: Add/edit fees
│   │   ├── SaleBreakdown.tsx     # NEW: Display financial totals
│   │   └── ConfirmButton.tsx     # NEW: Submit sale
│   └── products/
│       ├── ProductList.tsx       # NEW: Product list
│       └── ProductForm.tsx       # NEW: Create/edit product
└── lib/
    ├── api-client.ts            # NEW: HTTP client for backend
    └── websocket-client.ts       # NEW: WebSocket for stock updates
```

---

### 6. POS Data Flow

**Key Principle**: Frontend NEVER computes financial totals. It calls `/api/sales/calculate`.

```typescript
// frontend/components/pos/POSCart.tsx

const updateBreakdown = async () => {
  const response = await fetch('/api/sales/calculate', {
    method: 'POST',
    body: JSON.stringify({ items, fees })
  });
  const breakdown = await response.json();
  setBreakdown(breakdown);
};

// Call on every cart or fee change
useEffect(() => {
  updateBreakdown();
}, [items, fees]);
```

---

### 7. WebSocket Integration

**Frontend**:

```typescript
// frontend/lib/websocket-client.ts

const connectWebSocket = () => {
  const ws = new WebSocket('ws://localhost:8000/ws/stock-updates');
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.event === 'stock_updated') {
      // Update product stock in real-time
      updateProductStock(data.data.product_id, data.data.stock_quantity);
    }
  };
  
  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
    // Reconnect logic
  };
};
```

**Backend**:

```python
# backend/app/websocket/manager.py

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def broadcast_stock_update(self, product_id: str, stock_quantity: int):
        message = {
            "event": "stock_updated",
            "data": {
                "product_id": product_id,
                "stock_quantity": stock_quantity
            }
        }
        await self.broadcast(json.dumps(message))
```

---

### 8. Test Scenarios

#### Product Management Test

```python
# backend/tests/integration/test_product_api.py

async def test_create_product_success(client: AsyncClient):
    response = await client.post("/api/products", json={
        "name": "Panel X",
        "sku": "PNL-001",
        "category_id": "some-uuid",
        "base_price": 100.00,
        "selling_price": 150.00,
        "stock_quantity": 50
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Panel X"
    assert data["stock_quantity"] == 50
```

#### Sale Creation Test

```python
# backend/tests/integration/test_sale_api.py

async def test_create_sale_with_stock_deduction(client: AsyncClient):
    # Setup: create product with stock 10
    product = await create_test_product(stock=10)
    
    # Create sale for 3 units
    response = await client.post("/api/sales", json={
        "items": [{"product_id": product.id, "quantity": 3}],
        "payment_method_id": "some-uuid"
    })
    
    assert response.status_code == 201
    
    # Verify stock deducted
    updated_product = await get_product(product.id)
    assert updated_product.stock_quantity == 7
    
    # Verify inventory log created
    log = await get_inventory_log(product.id)
    assert log[0]["delta"] == -3
    assert log[0]["reason"] == "sale"
```

#### Calculation Engine Test

```python
# backend/tests/unit/test_calculations.py

def test_vat_calculation_percent():
    subtotal = Decimal('500.00')
    fees_total = Decimal('30.00')
    vat_amount, vat_rate = calculate_vat(
        subtotal, fees_total,
        vat_enabled=True,
        vat_type='percent',
        vat_value=Decimal('16.00')
    )
    assert vat_amount == Decimal('84.80')  # (500 + 30) × 0.16

def test_rounding_edge_case():
    result = round_currency(Decimal('3.335'))
    assert result == Decimal('3.34')  # ROUND_HALF_UP
```

---

## Development Workflow

1. **Start with calculation engine**: Implement and unit-test `app/core/calculations.py`
2. **Create database models**: SQLAlchemy models for all tables
3. **Implement Pydantic schemas**: Request/response validation
4. **Build service layer**: Business logic for products, sales, inventory
5. **Create API routes**: FastAPI endpoints
6. **Write tests**: Unit tests for calculations, integration tests for APIs
7. **Frontend POS**: Build cart, product search, fee editor
8. **WebSocket integration**: Real-time stock updates
9. **End-to-end testing**: Complete sale flow testing

---

## Key Notes

- **Atomic transactions**: Stock deduction and sale creation must be in one transaction
- **No frontend calculations**: Frontend calls `/api/sales/calculate` for all totals
- **Stock validation**: Backend validates stock at sale confirmation (not just UI)
- **Inventory logging**: Every stock change creates log entry
- **Real-time updates**: WebSocket broadcasts stock changes to connected POS clients

---

## Success Criteria

- ✅ Can create, update, search products
- ✅ Can complete a sale with automatic stock deduction
- ✅ Financial breakdown accurate to the cent
- ✅ Sale reversal restores stock correctly
- ✅ Inventory log records every stock change
- ✅ Real-time stock updates on POS screen
- ✅ All calculation edge cases pass tests

---

## Next Steps

After implementing Phase 1:

1. Run `/speckit.tasks` to generate implementation task list
2. Follow tasks in order (backend → frontend → testing)
3. Verify all acceptance scenarios from spec.md
4. Proceed to Phase 2 (Projects + Expenses)