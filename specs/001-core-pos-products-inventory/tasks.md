# Implementation Tasks: Core POS, Products, and Inventory Management

**Feature Branch**: 001-core-pos-products-inventory
**Version**: 1.0
**Generated**: 2026-04-04

## Overview

This document provides a complete, sequential task list for implementing Phase 1 of the EZOO POS system. Tasks are organized by user story to enable independent implementation and testing.

**Total Tasks**: 89
**Estimated Duration**: 2-3 weeks
**Parallel Opportunities**: 40+ tasks can run in parallel within phases

---

## Implementation Strategy

### MVP-First Approach

1. **MVP Scope**: User Story 1 (Complete a Sale) + User Story 2 (Manage Product Catalog)
2. **Incremental Delivery**: Each user story is independently testable
3. **Dependencies**: User Stories 1-2 are prerequisites for Stories 3-5

### Dependency Graph

```text
Setup (Phase 1)
  └─→ Foundations (Phase 2)
       ├─→ US2: Manage Products (P2) ─┐
       │                                ├─→ US1: Complete Sale (P1)
       └─→ Data models & APIs ─────────┘      │
                                               ├─→ US3: Reverse Sale (P3)
                                                │
                                               └─→ US4: Track Inventory (P4)
                                                     │
                                                      └─→ US5: Real-Time Updates (P5)
```

**Critical Path**: Setup → Foundations → US2 + US1 → US3/US4 → US5

---

## Phase 1: Setup

**Goal**: Initialize project infrastructure and development environment.

**Duration**: 1-2 days

### Tasks

- [X] T001 Enable PostgreSQL `pg_trgm` extension for fast product name search in database
- [X] T002 [P] Create Alembic migration for `products` table in backend/alembic/versions/
- [X] T003 [P] Create Alembic migration for `inventory_log` table in backend/alembic/versions/
- [X] T004 [P] Create Alembic migration for `sales` table in backend/alembic/versions/
- [X] T005 [P] Create Alembic migration for `sale_items` table in backend/alembic/versions/
- [X] T006 [P] Create Alembic migration for `sale_fees` table in backend/alembic/versions/
- [X] T007 [P] Create Alembic migration for `sale_reversals` table in backend/alembic/versions/
- [X] T008 Run all Alembic migrations to create database schema
- [X] T009 [P] Create backend/app/core/calculations.py with rounding utilities
- [X] T010 [P] Set up pytest configuration in backend/tests/conftest.py

**Parallel Opportunities**: T002-T007 (all migrations), T009-T010 (calc engine and tests)

**Completion Criteria**:
- Database schema matches data-model.md exactly
- All migrations run successfully
- `round_currency()` function passes edge case tests

---

## Phase 2: Foundational Components

**Goal**: Implement core services and calculation engine needed by all user stories.

**Duration**: 2-3 days

### Tasks

#### Calculation Engine

- [X] T011 Implement `calculate_line_total()` in backend/app/core/calculations.py
- [X] T012 Implement `calculate_fee_amount()` for fixed and percentage fees in backend/app/core/calculations.py
- [X] T013 Implement `calculate_vat()` for enabled/disabled VAT scenarios in backend/app/core/calculations.py
- [X] T014 Implement `calculate_sale_total()` for full breakdown calculation in backend/app/core/calculations.py
- [X] T015 [P] Write unit tests for round_currency edge cases in backend/tests/unit/test_calculations.py
- [X] T016 [P] Write unit tests for VAT calculation edge cases in backend/tests/unit/test_calculations.py
- [X] T017 [P] Write unit tests for fee calculation edge cases in backend/tests/unit/test_calculations.py

#### Base Models and Schemas

- [X] T018 Create base SQLAlchemy model with timestamps in backend/app/models/base.py
- [X] T019 [P] Create Product Pydantic schemas (Create, Update, Response) in backend/app/schemas/product.py
- [X] T020 [P] Create Category Pydantic schemas (Create, Update, Response) in backend/app/schemas/category.py
- [X] T021 [P] Create Sale Pydantic schemas (Create, CalculationRequest, Response, Breakdown) in backend/app/schemas/sale.py
- [X] T022 [P] Create Inventory Pydantic schemas (Restock, Adjust, LogResponse) in backend/app/schemas/inventory.py

#### WebSocket Infrastructure

- [X] T023 Create WebSocket connection manager in backend/app/websocket/manager.py
- [X] T024 Implement broadcast_stock_update() method in WebSocket manager
- [X] T025 Add WebSocket endpoint to FastAPI app in backend/main.py

**Parallel Opportunities**: T015-T017 (tests), T019-T022 (all schemas)

**Blocking Dependencies**: None

**Completion Criteria**:
- All calculation functions pass unit tests
- Pydantic schemas validate/correctly
- WebSocket manager can broadcast messages

---

## Phase 3: User Story 2 - Manage Product Catalog (Priority: P2)

**User Story**: "The shop operator manages a catalog of solar panels, batteries, and accessories. They can create new products with a name, optional SKU, category, base price (cost), selling price, and initial stock quantity. They can update product details and organize products into categories. Products referenced in past sales cannot be permanently removed."

**Why P2 Before P1**: Product catalog is a prerequisite for creating sales. Products must exist before they can be sold.

**Independent Test**: Can be fully tested by creating, updating, and organizing products with categories, then verifying data persists correctly and search works.

**Duration**: 2-3 days

### Tasks

#### Data Models [US2]

- [X] T026 [US2] Create Product SQLAlchemy model in backend/app/models/product.py
- [X] T027 [US2] Add CHECK constraints for base_price, selling_price, stock_quantity in Product model

#### Backend Services [US2]

- [X] T028 [US2] Create ProductService class in backend/app/modules/products/service.py
- [X] T029 [US2] Implement create_product() with SKU uniqueness validation in ProductService
- [X] T030 [US2] Implement list_products() with category filter and name/SKU search in ProductService
- [X] T031 [US2] Implement get_product() by ID in ProductService
- [X] T032 [US2] Implement update_product() with soft-delete prevention in ProductService
- [X] T033 [US2] Implement soft_delete_product() for referenced products in ProductService

#### Backend API Routes [US2]

- [X] T034 [US2] [P] Create POST /api/products endpoint in backend/app/modules/products/routes.py
- [X] T035 [US2] [P] Create GET /api/products endpoint with filters in backend/app/modules/products/routes.py
- [X] T036 [US2] [P] Create GET /api/products/{id} endpoint in backend/app/modules/products/routes.py
- [X] T037 [US2] [P] Create PUT /api/products/{id} endpoint in backend/app/modules/products/routes.py
- [X] T038 [US2] [P] Create DELETE /api/products/{id} endpoint in backend/app/modules/products/routes.py
- [X] T039 [US2] [P] Create GET /api/products/search/by-sku endpoint in backend/app/modules/products/routes.py

#### Category Endpoints (Phase 0 Foundation) [US2]

- [X] T040 [US2] Verify Category CRUD endpoints exist from Phase 0 (GET, POST, PUT, DELETE)
- [X] T041 [US2] Test category deletion protection when products exist

#### Frontend Components [US2]

- [X] T042 [US2] [P] Create ProductList component in frontend/components/products/ProductList.tsx
- [X] T043 [US2] [P] Create ProductForm component (create/edit modal) in frontend/components/products/ProductForm.tsx
- [X] T044 [US2] [P] Create CategoryFilter component in frontend/components/products/CategoryFilter.tsx

#### Frontend Pages [US2]

- [X] T045 [US2] Create products page with list and form in frontend/app/products/page.tsx
- [X] T046 [US2] Implement product search by name and SKU in frontend/app/products/page.tsx

#### Integration Tests [US2]

- [X] T047 [US2] [P] Write integration test for POST /api/products (create product) in backend/tests/integration/test_product_api.py
- [X] T048 [US2] [P] Write integration test for product SKU uniqueness validation
- [X] T049 [US2] [P] Write integration test for product soft delete behavior
- [X] T050 [US2] [P] Write integration test for product search functionality

**Parallel Opportunities**: T034-T039 (all routes), T042-T044 (all components), T047-T050 (all tests)

**Completion Criteria**:
- ✅ Can create product with all required fields
- ✅ SKU uniqueness enforced
- ✅ Can search by name (partial) and SKU (exact)
- ✅ Selling price validation (≥ base price)
- ✅ Soft delete for referenced products
- ✅ Category deletion blocked when products exist

---

## Phase 4: User Story 1 - Complete a Sale (Priority: P1)

**User Story**: "The shop operator opens the POS screen, searches for products by name or SKU, adds them to the cart with desired quantities, optionally adjusts the unit price (overriding the catalog default), optionally adds extra fees (shipping, installation, or custom), selects a payment method, and confirms the sale. The system instantly calculates the full financial breakdown — subtotal (using overridden prices where applicable), individual fee amounts, VAT (if enabled), and grand total — and presents it before confirmation. On confirmation the sale is recorded permanently and stock is deducted."

**Why P1**: This is the primary revenue-generating action. Without the ability to complete a sale, the system has no business value.

**Dependencies**: User Story 2 (products must exist)

**Independent Test**: Can be fully tested by adding products to the system, performing a sale through the POS, and verifying the resulting sale record, financial breakdown, and stock deduction.

**Duration**: 4-5 days

### Tasks

#### Data Models [US1]

- [X] T051 [US1] [P] Create Sale SQLAlchemy model in backend/app/models/sale.py
- [X] T052 [US1] [P] Create SaleItem SQLAlchemy model in backend/app/models/sale_item.py
- [X] T053 [US1] [P] Create SaleFee SQLAlchemy model in backend/app/models/sale_fee.py
- [X] T054 [US1] [P] Create SaleReversal SQLAlchemy model in backend/app/models/sale_reversal.py
- [X] T055 [US1] [P] Create InventoryLog SQLAlchemy model in backend/app/models/inventory_log.py

#### Backend Services [US1]

- [X] T056 [US1] Create SaleService class in backend/app/modules/pos/service.py
- [X] T057 [US1] Implement calculate_breakdown() for financial preview in SaleService
- [X] T058 [US1] Implement create_sale() with atomic stock deduction in SaleService
- [X] T059 [US1] Implement validate_stock_availability() before sale confirmation
- [X] T060 [US1] Implement list_sales() with date range filter in SaleService
- [X] T061 [US1] Implement get_sale_detail() with full breakdown in SaleService
- [X] T062 [US1] Integrate calculation engine functions in SaleService

#### Backend API Routes [US1]

- [X] T063 [US1] [P] Create POST /api/sales/calculate endpoint in backend/app/modules/pos/routes.py
- [X] T064 [US1] [P] Create POST /api/sales endpoint (create sale) in backend/app/modules/pos/routes.py
- [X] T065 [US1] [P] Create GET /api/sales endpoint with filters in backend/app/modules/pos/routes.py
- [X] T066 [US1] [P] Create GET /api/sales/{id} endpoint in backend/app/modules/pos/routes.py

#### Inventory Integration [US1]

- [X] T067 [US1] Create InventoryService class in backend/app/modules/inventory/service.py
- [X] T068 [US1] Implement deduct_stock() with inventory log creation in InventoryService
- [X] T069 [US1] Implement emit_stock_update() via WebSocket in InventoryService

#### Frontend Components [US1]

- [X] T070 [US1] [P] Create ProductSearch component in frontend/components/pos/ProductSearch.tsx
- [X] T071 [US1] [P] Create POSCart component in frontend/components/pos/POSCart.tsx
- [X] T072 [US1] [P] Create FeeEditor component in frontend/components/pos/FeeEditor.tsx
- [X] T073 [US1] [P] Create SaleBreakdown component in frontend/components/pos/SaleBreakdown.tsx
- [X] T074 [US1] [P] Create PaymentMethodSelect component in frontend/components/pos/PaymentMethodSelect.tsx
- [X] T075 [US1] [P] Create ConfirmButton component in frontend/components/pos/ConfirmButton.tsx

#### Frontend Pages [US1]

- [X] T076 [US1] Create POS page with all components in frontend/app/pos/page.tsx
- [X] T077 [US1] Implement cart state management in frontend/app/pos/page.tsx
- [X] T078 [US1] Implement real-time breakdown calculation via /calculate endpoint
- [X] T079 [US1] Handle stock validation errors and display to user

#### Integration Tests [US1]

- [ ] T080 [US1] [P] Write integration test for POST /api/sales/calculate (all scenarios) in backend/tests/integration/test_sale_api.py
- [ ] T081 [US1] [P] Write integration test for POST /api/sales (create sale with stock deduction)
- [ ] T082 [US1] [P] Write integration test for insufficient stock error
- [ ] T083 [US1] [P] Write integration test for VAT calculation (enabled/disabled)
- [ ] T084 [US1] [P] Write integration test for fee calculation (fixed/percentage)

**Parallel Opportunities**: T051-T055 (all models), T063-T066 (all routes), T070-T075 (all components), T080-T084 (all tests)

**Completion Criteria**:
- ✅ Can create sale with multiple items
- ✅ Financial breakdown accurate (subtotal, fees, VAT, total)
- ✅ Stock deducted atomically on confirmation
- ✅ Inventory log created for each stock change
- ✅ Can override unit price
- ✅ Can add fees (fixed and percentage)
- ✅ Error message for insufficient stock
- ✅ Can list and filter sales by date range

---

## Phase 5: User Story 3 - Reverse a Sale (Priority: P3)

**User Story**: "When a mistake is made or a customer returns items, the operator can perform a full reversal of a confirmed sale. The reversal creates a separate correction record that negates the entire sale's financial impact and restores stock for all items. The original sale record remains untouched for audit purposes."

**Why P3**: Corrections are essential for financial accuracy but happen less frequently than normal sales.

**Dependencies**: User Story 1 (sales must exist)

**Independent Test**: Can be fully tested by completing a sale, reversing it, and verifying that stock is restored, the original sale is unchanged, and a linked reversal record exists.

**Duration**: 2-3 days

### Tasks

#### Backend Services [US3]

- [X] T085 [US3] Implement reverse_sale() with stock restoration in SaleService
- [X] T086 [US3] Implement prevent_double_reversal() validation
- [X] T087 [US3] Create inventory log entries with reason 'reversal'

#### Backend API Routes [US3]

- [X] T088 [US3] Create POST /api/sales/{id}/reverse endpoint in backend/app/modules/pos/routes.py

#### Frontend Components [US3]

- [X] T089 [US3] Add "Reverse Sale" button to sale detail view in frontend/app/pos/page.tsx
- [X] T090 [US3] Implement reversal reason input modal

#### Integration Tests [US3]

- [X] T091 [US3] [P] Write integration test for sale reversal with stock restoration
- [X] T092 [US3] [P] Write integration test for double reversal prevention
- [X] T093 [US3] [P] Write integration test for reversal record linking

**Parallel Opportunities**: T091-T093 (all tests)

**Completion Criteria**:
- ✅ Can reverse a sale with required reason
- ✅ Stock restored for all items
- ✅ Inventory log created with reason 'reversal'
- ✅ Original sale marked as reversed
- ✅ Cannot reverse a sale twice

---

## Phase 6: User Story 4 - Track Inventory Changes (Priority: P4)

**User Story**: "Every change to product stock — whether from a sale, a reversal, a manual restock, or an adjustment — is logged with the quantity change, reason, and resulting balance. The operator can view the full stock movement history for any product and manually add stock via restock or adjustment entries."

**Why P4**: Inventory logging is critical for accountability but operates behind the scenes.

**Dependencies**: User Story 1 and 3 (inventory log entries created automatically)

**Independent Test**: Can be fully tested by performing various stock-changing actions and verifying each one creates a corresponding log entry with correct data.

**Duration**: 1-2 days

### Tasks

#### Backend Services [US4]

- [X] T094 [US4] Implement restock_product() in InventoryService
- [X] T095 [US4] Implement adjust_stock() with stock ≥ 0 validation in InventoryService
- [X] T096 [US4] Implement get_inventory_log() with pagination in InventoryService
- [X] T097 [US4] Implement get_low_stock_products() in InventoryService

#### Backend API Routes [US4]

- [X] T098 [US4] [P] Create POST /api/inventory/restock endpoint in backend/app/modules/inventory/routes.py
- [X] T099 [US4] [P] Create POST /api/inventory/adjust endpoint in backend/app/modules/inventory/routes.py
- [X] T100 [US4] [P] Create GET /api/inventory/log/{product_id} endpoint in backend/app/modules/inventory/routes.py
- [X] T101 [US4] [P] Create GET /api/inventory/low-stock endpoint in backend/app/modules/inventory/routes.py

#### Frontend Pages [US4]

- [X] T102 [US4] Create inventory management page in frontend/app/inventory/page.tsx
- [X] T103 [US4] Display inventory log with chronological order
- [X] T104 [US4] Add restock and adjustment forms

#### Integration Tests [US4]

- [X] T105 [US4] [P] Write integration test for restock with log creation
- [X] T106 [US4] [P] Write integration test for adjustment with stock validation
- [X] T107 [US4] [P] Write integration test for inventory log retrieval

**Parallel Opportunities**: T098-T101 (all routes), T105-T107 (all tests)

**Completion Criteria**:
- ✅ Can restock products with inventory log
- ✅ Can adjust stock (positive/negative) with reason
- ✅ Stock cannot go below zero
- ✅ Inventory log shows all movements chronologically
- ✅ Low stock products identified

---

## Phase 7: User Story 5 - Real-Time Stock Updates (Priority: P5)

**User Story**: "While the POS screen is open, stock levels update in real time without requiring a page refresh. If stock changes due to a sale, reversal, or restock happening elsewhere, the product search results reflect the updated availability immediately."

**Why P5**: Real-time updates improve operator confidence but are not critical for functionality.

**Dependencies**: User Story 1, 3, 4 (stock change operations must exist)

**Independent Test**: Can be tested by opening the POS screen, triggering a stock change from a separate action, and verifying the POS product list updates automatically.

**Duration**: 1-2 days

### Tasks

#### WebSocket Integration [US5]

- [X] T108 [US5] Broadcast stock updates after sale confirmation in SaleService
- [X] T109 [US5] Broadcast stock updates after reversal in SaleService
- [X] T110 [US5] Broadcast stock updates after restock in InventoryService
- [X] T111 [US5] Broadcast stock updates after adjustment in InventoryService

#### Frontend WebSocket Client [US5]

- [X] T112 [US5] Create WebSocket client with reconnect logic in frontend/lib/websocket-client.ts
- [X] T113 [US5] Subscribe to /ws/stock-updates channel on POS page load
- [X] T114 [US5] Update product list on stock update event
- [X] T115 [US5] Display connection status indicator
- [X] T116 [US5] Implement auto-reconnect on connection loss

#### Tests [US5]

- [X] T117 [US5] [P] Write integration test for WebSocket stock broadcast after sale
- [X] T118 [US5] [P] Write integration test for WebSocket stock broadcast after restock
- [X] T119 [US5] [P] Verify connection status updates on disconnect/reconnect

**Parallel Opportunities**: T117-T119 (all tests)

**Completion Criteria**:
- ✅ Stock updates appear in POS within 2 seconds
- ✅ Connection status displayed
- ✅ Auto-reconnect on connection loss
- ✅ All stock changes broadcast via WebSocket

---

## Phase 8: Polish & Cross-Cutting Concerns

**Goal**: Finalize the feature with error handling, validation, and user experience improvements.

**Duration**: 1-2 days

### Tasks

#### Error Handling

- [X] T120 [P] Add structured error responses for all API endpoints
- [X] T121 [P] Implement custom exception handlers in backend/app/core/exceptions.py
- [X] T122 [P] Add frontend error boundary components
- [X] T123 [P] Implement user-friendly error messages (insufficient stock, validation errors, etc.)

#### Input Validation

- [X] T124 [P] Add Pydantic validation for edge cases (zero quantity, negative prices, etc.)
- [X] T125 [P] Add backend validation for price override warning (selling_price < base_price)
- [X] T126 [P] Add frontend validation for zero-stock products

#### User Experience

- [X] T127 [P] Add loading states for all async operations
- [X] T128 [P] Implement optimistic UI updates for cart operations
- [X] T129 [P] Add keyboard shortcuts for POS operations
- [X] T130 [P] Implement form validation feedback
- [X] T131 [P] Add pagination for sales list and inventory log

#### Performance

- [X] T132 [P] Add database indexes per data-model.md specifications
- [X] T133 [P] Implement query optimization for product search (pg_trgm)
- [X] T134 [P] Add connection pooling for WebSocket clients

#### Documentation

- [X] T135 [P] Update API documentation with error codes
- [X] T136 [P] Add inline code comments for calculation engine
- [X] T137 [P] Document environment variables and configuration

**Parallel Opportunities**: T120-T137 (most polish tasks)

**Completion Criteria**:
- ✅ All errors return structured JSON
- ✅ Frontend displays clear error messages
- ✅ All validations tested
- ✅ Performance goals met (<1s search, <2s stock update)

---

## Test Scenarios

### Acceptance Tests (From Spec)

#### User Story 1 — Complete a Sale

```text
1. Create products: Panel A (price 150, stock 10), Battery B (price 200, stock 5)
2. Create sale: 2× Panel A + 1× Battery B + shipping fee 30
3. Verify: subtotal = 500, fees = 30, VAT correct, total correct
4. Verify: stock Panel A = 8, Battery B = 4
5. Verify: inventory log has entries (delta=-2, reason=sale)
6. Test insufficient stock (try to sell 6 units when only 3 available)
7. Test price override below base price (should allow with warning)
```

#### User Story 2 — Manage Product Catalog

```text
1. Create product "Panel X" with SKU "PNL-001", base price 100, selling price 150, stock 50
2. Update selling price to 170
3. Verify: future sales use new price, past sales retain old price
4. Create sale with product, then attempt to delete product
5. Verify: product soft-deleted (is_active=false)
6. Delete category with products, verify error
```

#### User Story 3 — Reverse a Sale

```text
1. Create sale for 3× Panel A
2. Reverse sale with reason "Customer return"
3. Verify: stock restored (+3), original sale marked reversed
4. Verify: inventory log has reversal entry (delta=+3, reason=reversal)
5. Attempt to reverse again, verify error
```

#### User Story 4 — Track Inventory Changes

```text
1. Sell 3 units, verify log: delta=-3, reason=sale, balance=17
2. Reverse sale, verify log: delta=+3, reason=reversal, balance=20
3. Restock 50 units, verify log: delta=+50, reason=restock, balance=70
4. Adjust -5 units (damaged), verify log: delta=-5, reason=adjustment, balance=65
5. View chronological log for product
```

#### User Story 5 — Real-Time Stock Updates

```text
1. Open POS screen showing Panel A stock = 20
2. In separate action, restock Panel A by 10 units
3. Verify: POS updates to stock = 30 without refresh (within 2 seconds)
4. Disconnect network, verify connection status indicator
5. Reconnect, verify auto-reconnect
```

---

## Parallel Execution Examples

### Phase 3: User Story 2 (ProductCatalog)

**Tasks that can run in parallel**:

```text
Backend Developer A: T026-T027 (Product model)
Backend Developer B: T028-T033 (ProductService)
Frontend Developer: T042-T046 (UI components and pages)
QA Engineer: T047-T050 (Integration tests)
```

**Estimated parallel time**: 2-3 days (vs. 5-6 days sequential)

### Phase 4: User Story 1 (Complete Sale)

**Tasks that can run in parallel**:

```text
Backend Developer A: T051-T055 (Data models)
Backend Developer B: T056-T062 (SaleService)
Backend Developer C: T063-T066 (API routes)
Frontend Developer A: T070-T075 (Components)
Frontend Developer B: T076-T079 (POS page)
QA Engineer: T080-T084 (Integration tests)
```

**Estimated parallel time**: 4-5 days (vs. 10-12 days sequential)

---

## Format Validation

✅ **All tasks follow the checklist format**:
- Checkbox: `- [ ]`
- Task ID: Sequential (T001-T137)
- [P] marker: Where applicable (parallelizable tasks)
- [Story] label: Present for all user story tasks (US2, US1, US3, US4, US5)
- Description: Clear action with file path

✅ **Task IDs are sequential**: T001 → T137

✅ **Story labels are correct**: US2, US1, US3, US4, US5 match spec.md priorities

✅ **Parallel markers are accurate**: Only on tasks with no dependencies on incomplete work

---

## Summary

- **Total Tasks**: 137
- **Setup Tasks**: 10
- **Foundation Tasks**: 15
- **User Story 2**: 25 tasks (Product Catalog)
- **User Story 1**: 34 tasks (Complete Sale)
- **User Story 3**: 9 tasks (Reverse Sale)
- **User Story 4**: 14 tasks (Inventory Tracking)
- **User Story 5**: 12 tasks (Real-Time Updates)
- **Polish Tasks**: 18

**Parallel Opportunities**: 40+ tasks marked with [P]

**MVP Scope**: Phases 1-4 (Setup + Foundations + US2 + US1)
**MVP Duration**: ~10-14 days with parallel execution

**Full Feature Duration**: 2-3 weeks with team of3-4developers

**Independent Testing**: Each user story phase has clear acceptance criteria and can be tested independently before moving to the next phase.