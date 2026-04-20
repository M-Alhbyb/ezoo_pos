# Implementation Plan: CorePOS, Products, and Inventory Management

**Branch**: `001-core-pos-products-inventory` | **Date**: 2026-04-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-core-pos-products-inventory/spec.md`

## Summary

Build the core point-of-sale system with product catalog management, real-time inventory tracking, and sale processing. This is Phase 1 of the implementation plan, building upon the Phase 0 foundation (project scaffolding, database, settings, categories, payment methods). The feature includes: product CRUD with categories, POS interface with cart management, fees and VAT calculation, sale confirmation with atomic stock deduction, sale reversals, and complete inventory audit trail.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/Next.js 14 (frontend)
**Primary Dependencies**: FastAPI (backend), Next.js 14 App Router (frontend), SQLAlchemy async (ORM), Alembic (migrations), Pydantic (validation), WebSocket (real-time updates)
**Storage**: PostgreSQL (sole source of truth), DECIMAL/NUMERIC types for all monetary columns
**Testing**: pytest (backend), Jest/Vitest (frontend)
**TargetPlatform**: Linux server (backend), Web browser (frontend), local network deployment
**Project Type**: Web application (FastAPI monolith + Next.js frontend)
**Performance Goals**: Product search <1s for 5,000 products, stock updates <2s propagation to POS, sale completion <30s for typical 3-item transaction
**Constraints**: Single-user system (no RBAC), offline-capable stock validation at confirmation, stock must never go negative
**Scale/Scope**: Up to 5,000 products, local network deployment, one operator at a time

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Implementation Status |
|-----------|-------------|----------------------|
| **I. Financial Accuracy** | All monetary calculations deterministic, traceable, DECIMAL types | ✅ Backend calculation engine in `app/core/calculations.py`, all values as Decimal, never float |
| **II. Single Source of Truth** | PostgreSQL only, backend calculates, frontend displays | ✅ All business logic in FastAPI backend, frontend calls API for calculations, no duplicated logic |
| **III. Explicit Over Implicit** | Every fee stores type=value=amount, percentages saved with transaction | ✅ `sale_fees` table has `fee_type`, `fee_value`, `fee_value_type`, `calculated_amount`; VAT rate stored per sale |
| **IV. Immutable Financial Records** | Confirmed records not editable, corrections via reversals | ✅ Sales immediately confirmed and immutable, reversals create separate correction records |
| **V. Simplicity of Use** | Minimal clicks, visible breakdowns, clear error messages | ✅ POS flow: search → add → fees → confirm; financial breakdown always visible; validation blocks invalid actions |
| **VI. Data Integrity** | DECIMAL columns, timestamps, stock ≥ 0, logged changes | ✅ All monetary columns DECIMAL(12,2); all tables have created_at/updated_at; CHECK constraint stock ≥ 0; inventory_log for every change |
| **VII. Backend Authority** | FastAPI enforces all validation and calculation | ✅ All validation in Pydantic schemas + service layer; frontend displays API responses only |
| **VIII. Input Validation** | All endpoints validate inputs | ✅ Pydantic schemas validate all request payloads; structured error responses |
| **IX. Extensibility** | Schema anticipates multi-user/multi-branch | ✅ All tables include `user_id` and `branch_id` columns (nullable, defaulting to single-user/single-branch) |

**Gate Status**: ✅ PASS—all principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-core-pos-products-inventory/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── products-api.md
│   ├── categories-api.md
│   ├── sales-api.md
│   └── inventory-api.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── calculations.py      # Financial calculation engine
│   ├── models/
│   │   ├── base.py              # Base model with timestamps, user_id, branch_id
│   │   ├── category.py
│   │   ├── product.py
│   │   ├── sale.py
│   │   ├── sale_item.py
│   │   ├── sale_fee.py
│   │   ├── sale_reversal.py
│   │   ├── inventory_log.py
│   │   ├── payment_method.py
│   │   └── settings.py
│   ├── schemas/
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── sale.py
│   │   └── inventory.py
│   ├── modules/
│   │   ├── products/
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   └── __init__.py
│   │   ├── categories/
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   └── __init__.py
│   │   ├── pos/
│   │   │   ├── routes.py
│   │   │   ├── service.py
│   │   │   └── __init__.py
│   │   └── inventory/
│   │       ├── routes.py
│   │       ├── service.py
│   │       └── __init__.py
│   └── websocket/
│       └── manager.py
├── tests/
│   ├── unit/
│   │   ├── test_calculations.py
│   │   ├── test_product_service.py
│   │   └── test_sale_service.py
│   ├── integration/
│   │   ├── test_product_api.py
│   │   ├── test_sale_api.py
│   │   └── test_inventory_api.py
│   └── conftest.py
├── alembic/
│   └── versions/
├── alembic.ini
├── requirements.txt
└── main.py

frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── pos/
│   │   └── page.tsx
│   ├── products/
│   │   └── page.tsx
│   └── settings/
│       └── page.tsx
├── components/
│   ├── pos/
│   │   ├── ProductSearch.tsx
│   │   ├── POSCart.tsx
│   │   ├── FeeEditor.tsx
│   │   ├── VATToggle.tsx
│   │   ├── PaymentMethodSelect.tsx
│   │   ├── SaleBreakdown.tsx
│   │   └── ConfirmButton.tsx
│   ├── products/
│   │   ├── ProductList.tsx
│   │   ├── ProductForm.tsx
│   │   └── CategoryFilter.tsx
│   └── shared/
│       ├── DataTable.tsx
│       ├── Modal.tsx
│       └── StatusBadge.tsx
├── lib/
│   ├── api-client.ts
│   └── websocket-client.ts
├── package.json
└── next.config.js
```

**Structure Decision**: Web application structure with FastAPI backend monolith and Next.js 14 frontend. Backend follows modular structure with core services, models, and API routes. Frontend uses App Router with feature-based page organization. Real-time stock updates via WebSocket connection.

## Complexity Tracking

> No violations—all design choices align with constitution principles.