# Research: Core POS, Products, and Inventory Management

**Date**: 2026-04-04
**Feature**: 001-core-pos-products-inventory

## Overview

This document resolves technical unknowns and establishes best practices for implementing Phase 1 of the EZOO POS system. Phase 0 (Foundation) is assumed complete, providing project scaffolding, database setup, settings engine, categories, and payment methods.

## Technical Decisions

### 1. Sale Creation Flow: Immediate vs. Draft State

**Decision**: Immediate confirmation (no draft state)

**Rationale**: 
- Specification explicitly states "Sale is immediately confirmed on submit" (clarification session)
- Simplifies implementation by eliminating state management complexity
- Aligns with Constitution IV (Immutable Financial Records)
- Corrections handled via reversals rather than edits

**Alternatives Considered**:
- Draft state with explicit confirmation workflow
  - Rejected: Adds unnecessary complexity; reversals provide cleaner audit trail

### 2. Financial Calculation Precision

**Decision**: Python `Decimal` type with `ROUND_HALF_UP` rounding to 2 decimal places

**Rationale**:
- Constitution I requires DECIMAL types everywhere
- Python's `Decimal` from `decimal` module provides exact arithmetic
- `ROUND_HALF_UP` is standard commercial rounding (3.335 → 3.34)
- Aligns with specification clarification on rounding rules

**Implementation**:
```python
from decimal import Decimal, ROUND_HALF_UP

TWOPLACES = Decimal(10) ** -2  # 0.01

def round_currency(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)
```

**Alternatives Considered**:
- Float type
  - Rejected: Violates Constitution I, leads to precision errors
- Decimal with different rounding
  - Rejected: ROUND_HALF_UP is specified in clarifications

### 3. Stock Management: Optimistic vs. Pessimistic Locking

**Decision**: Database-level check with transaction atomicity

**Rationale**:
- PostgreSQL provides ACID guarantees for atomic stock deduction
- Use `SELECT ... FOR UPDATE` within transaction to prevent race conditions
- Check stock ≥ requested quantity before confirmation
- Reject sale if insufficient stock with clear error message

**Implementation Pattern**:
```python
async with db.begin():  # Transaction
    # Lock product row
    product = await db.execute(
        select(Product).where(Product.id == item_id).with_for_update()
    )
    if product.stock_quantity < requested_qty:
        raise InsufficientStockError(product.name, product.stock, requested_qty)
    # Deduct stock
    product.stock_quantity -= requested_qty
    # Create inventory log
    # Create sale record
```

**Alternatives Considered**:
- Pessimistic locking at application level
  - Rejected: PostgreSQL transactions provide sufficient guarantees for single-user system
- Optimistic locking (check at end)
  - Rejected: Could fail late, providing poor user experience

### 4. Real-Time Stock Updates: WebSocket vs. Polling

**Decision**: WebSocket with automatic reconnection

**Rationale**:
- Specification requires real-time updates (<2s propagation)
- WebSocket provides push-based updates without polling overhead
- Frontend should display connection status during disconnections
- Implementation plan explicitly mentions WebSocket manager

**Implementation**:
- Backend: FastAPI WebSocket endpoint at `/ws/stock-updates`
- Frontend: WebSocket client with reconnect logic
- Broadcast stock changes after: sale confirmation, reversal, restock, adjustment

**Alternatives Considered**:
- Polling (HTTP)
  - Rejected: Inefficient for real-time requirement
- Server-Sent Events (SSE)
  - Rejected: WebSocket is bidirectional and already in implementation plan

### 5. Product Search: Database Query vs. Full-Text Search Engine

**Decision**: Database query with indexed LIKE/ILIKE for name and exact match for SKU

**Rationale**:
- Catalog size ≤5,000 products (specification assumption)
- PostgreSQL `ILIKE` with `pg_trgm` extension provides sufficient performance
- No external search service complexity
- SKU search is exact match (indexed)

**Implementation**:
```sql
CREATE INDEX idx_products_name ON products USING gin(name gin_trgm_ops);
CREATE INDEX idx_products_sku ON products(sku);
```

**Search Query**:
```python
# Name search (partial, case-insensitive)
results = await db.execute(
    select(Product).where(Product.name.ilike(f"%{search_term}%"))
)

# SKU search (exact match)
results = await db.execute(
    select(Product).where(Product.sku == search_term)
)
```

**Alternatives Considered**:
- Elasticsearch/Meilisearch
  - Rejected: Over-engineered for 5,000 products; adds deployment complexity

### 6. Sale Reversal: New Negative Sale vs. Status Change

**Decision**: Create separate reversal record linking to original sale

**Rationale**:
- Constitution IV requires immutable financial records
- Original sale must remain unchanged for audit trail
- Reversal record provides explicit traceability (specification FR-022)
- Stock restoration logged in inventory_log with reason "reversal"

**Implementation**:
- Create `sale_reversals` table with `original_sale_id`, `reversal_sale_id`, `reason`
- Reversal creates new sale with negative quantities
- Both records linked for audit trail

**Alternatives Considered**:
- Update sale status to "reversed"
  - Rejected: Violates Constitution IV (immutability)

### 7. Fee Calculation: Fixed vs. Percentage

**Decision**: Support both fixed amount and percentage, stored explicitly

**Rationale**:
- Specification FR-010 requires both types
- Constitution III requires storing type, value, and calculated amount
- Must work for subtotal-based percentage calculation

**Implementation**:
```python
def calculate_fee_amount(
    fee_value: Decimal,
    fee_value_type: str,  # 'fixed' or 'percent'
    subtotal: Decimal
) -> Decimal:
    if fee_value_type == 'fixed':
        return round_currency(fee_value)
    else:  # percent
        return round_currency(subtotal * (fee_value / Decimal(100)))
```

**Storage**:
- `sale_fees` table columns: `fee_type`, `fee_value`, `fee_value_type`, `calculated_amount`

### 8. Price Override: Validation Requirements

**Decision**: Allow override, warn if selling_price < base_price (cost)

**Rationale**:
- Specification clarification: operators can manually edit unit price
- Edge case specification: system allows sale below cost but SHOULD display warning
- No hard rejection to preserve operator flexibility

**Implementation**:
- Frontend displays visual warning indicator
- Backend stores the overridden price in `sale_items.unit_price`
- No backend validation blocking sale (warning is non-blocking)

### 9. Zero-Stock Product: Search Visibility vs. Add Prevention

**Decision**: Show in search results, mark "Out of Stock", prevent add to cart

**Rationale**:
- Specification FR-008a: prevent adding if stock = 0
- Edge case: products must still appear in search
- Clear UI indication (disabled "Add" button, "Out of Stock" label)

**Implementation**:
- Product search returns all products regardless of stock
- Frontend displays stock quantity
- Frontend disables "Add" action if stock = 0
- Backend validates stock at sale confirmation (prevents race conditions)

### 10. VAT Calculation: Per-Sale vs. Global Rate

**Decision**: Store VAT rate and amount per sale using global settings at time of sale

**Rationale**:
- Constitution III: percentages must be saved with transaction
- Global settings may change over time
- Historical sales must use rate at time of sale, not current global rate

**Implementation**:
- `sales` table includes `vat_rate` and `vat_amount` columns
- Value copied from settings at sale creation
- Calculation applies to (subtotal + fees total)

**Best Practices Applied**

### Python/FastAPI Conventions

1. **Async/Await**: All database operations use async SQLAlchemy
2. **Dependency Injection**: FastAPI `Depends()` for DB sessions
3. **Pydantic Schemas**: Separate request/response schemas for validation
4. **Service Layer**: Business logic in service classes, not in routes
5. **Repository Pattern**: Not required—direct SQLAlchemy ORM sufficient for this scope

### Database Design

1. **Foreign Keys**: All relationships use explicit FKs with appropriate ON DELETE actions
2. **Timestamps**: All tables have `created_at` (immutable) and `updated_at`
3. **Soft Deletes**: Products use `is_active` flag when referenced in sales
4. **Constraints**: CHECK constraints for stock ≥ 0, valid price ranges
5. **Extensibility Columns**: `user_id`, `branch_id` nullable columns on all tables

### Testing Strategy

1. **Unit Tests**: Calculation engine, service methods
2. **Integration Tests**: API endpoints with test database
3. **Edge Cases**: Zero quantities, zero stock, negative prices, maximum values
4. **Concurrency**: Test simultaneous stock deduction scenarios

## Dependencies

### Required (Already in Phase 0)

- FastAPI
- SQLAlchemy async
- Alembic
- Pydantic
- PostgreSQL with `pg_trgm` extension
- Python `decimal` module

### New for Phase 1

- No additional dependencies beyond Phase 0 foundation

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Floating-point precision errors | Enforce `Decimal` everywhere; linter rules forbid `float` |
| Stock race conditions | Use `FOR UPDATE` in transactions |
| VAT calculation confusion | Explicit documentation: VAT applied to (subtotal + fees) |
| Reversal double-spending | Track reversed status; reject double reversal |
| Real-time update delays | WebSocket with <2s target; polling fallback for resilience |

## Open Questions

All questions resolved through specification clarifications and constitution principles.

## Next Steps

1. Design data model (see `data-model.md`)
2. Define API contracts (see `contracts/` directory)
3. Create implementation tasks (via `/speckit.tasks`)