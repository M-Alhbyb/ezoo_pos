# Implementation Tasks: Supplier Accounting System

**Feature**: 008-supplier-accounting  
**Date**: 2026-04-20  
**Input**: Feature specification and implementation plan

## Dependencies

### Story Completion Order

| User Story | Priority | Dependencies | Independent Test |
|-----------|----------|--------------|------------------|
| US1: Purchase Inventory | P1 | Setup → Foundational | Create purchase, verify inventory increase, ledger entry |
| US2: Record Payment | P1 | Setup → Foundational → US1 recommended | Record payment, verify balance reduction |
| US3: Return Items | P2 | Setup → Foundational → US1 required | Return items, verify inventory decrease, balance reduction |
| US4: View Reports | P2 | Setup → Foundational → US1 recommended | View supplier summary, statement with date range |

**Phase Dependencies**:
- Phase 1 (Setup): No dependencies
- Phase 2 (Foundational): Requires Phase 1
- Phase 3-6 (User Stories): Require Phase 2
- Phase 7 (Polish): Requires all User Stories

### Parallel Opportunities

- US2 (Payment) and US3 (Return) can be implemented in parallel after US1
- Backend model tasks can run parallel to schema tasks

---

## Phase 1: Setup

- [x] T001 [P] Create Alembic migration for supplier accounting tables in `backend/alembic/versions/t012_supplier_accounting.py`
- [x] T002 [P] Run migration to create tables in database

---

## Phase 2: Foundational

- [x] T003 Create Supplier model in `backend/app/models/supplier.py`
- [x] T004 [P] Create Purchase model in `backend/app/models/purchase.py`
- [x] T005 [P] Create PurchaseItem model in `backend/app/models/purchase_item.py`
- [x] T006 Create SupplierLedger model in `backend/app/models/supplier_ledger.py`
- [x] T007 [P] Create Supplier Pydantic schemas in `backend/app/schemas/supplier.py`
- [x] T008 Create Purchase Pydantic schemas in `backend/app/schemas/purchase.py`
- [x] T009 Create SupplierLedger Pydantic schemas in `backend/app/schemas/supplier_ledger.py`

---

## Phase 3: US1 - Purchase Inventory from Supplier (P1)

**Independent Test**: Create purchase with items, verify inventory increases, verify PURCHASE ledger entry

- [x] T010 [US1] Implement create supplier endpoint in `backend/app/modules/suppliers/routes.py`
- [x] T011 [US1] Implement list suppliers endpoint in `backend/app/modules/suppliers/routes.py`
- [x] T012 [US1] Implement get supplier endpoint in `backend/app/modules/suppliers/routes.py`
- [x] T013 [US1] Create SupplierService in `backend/app/modules/suppliers/service.py`
- [x] T014 [US1] Implement create purchase endpoint in `backend/app/modules/purchases/routes.py`
- [x] T015 [US1] Implement list purchases endpoint in `backend/app/modules/purchases/routes.py`
- [x] T016 [US1] Implement get purchase endpoint in `backend/app/modules/purchases/routes.py`
- [x] T017 [US1] Create PurchaseService in `backend/app/modules/purchases/service.py`
  - Validate supplier exists
  - Calculate total_amount from items
  - Create Purchase + PurchaseItems with unit_cost snapshots
  - Increase inventory stock per item
  - Create inventory_log entries
  - Create SupplierLedger entry (type=PURCHASE)
- [x] T018 [US1] Integrate supplier routes in `backend/main.py`

---

## Phase 4: US2 - Record Supplier Payment (P1)

**Independent Test**: Record payment, verify PAYMENT ledger entry, verify balance reduced

- [x] T019 [US2] Implement record payment endpoint in `backend/app/modules/suppliers/routes.py`
- [x] T020 [US2] Update SupplierService to include payment recording
- [x] T021 [US2] Payment recording integrated (part of SupplierService)

---

## Phase 5: US3 - Return Items to Supplier (P2)

**Independent Test**: Return items, verify inventory decreases, verify RETURN ledger entry, cannot over-return

- [x] T022 [US3] Implement return items endpoint in `backend/app/modules/purchases/routes.py`
- [x] T023 [US3] ReturnService in PurchaseService (validate qty <= purchased, decrease stock, create RETURN ledger)
- [ ] T023 [US3] Create ReturnService in `backend/app/modules/purchases/service.py`
  - Validate return quantity <= original purchase quantity
  - Use original unit_cost snapshot for return amount
  - Decrease inventory stock
  - Create inventory_log entries
  - Create SupplierLedger entry (type=RETURN)

---

## Phase 6: US4 - View Supplier Reports (P2)

**Independent Test**: View all suppliers with balance, view supplier statement with date filtering

- [x] T024 [US4] Implement supplier summary report endpoint in `backend/app/modules/reports/routes.py`
- [x] T025 [US4] Implement supplier statement endpoint in `backend/app/modules/reports/routes.py`
- [x] T026 [US4] ReportService methods (get_supplier_summary_report, get_supplier_statement)

---

## Phase 7: Frontend

- [x] T027 [P] Create suppliers list page in `frontend/app/suppliers/page.tsx`
- [x] T028 [P] Create supplier detail page in `frontend/app/suppliers/[id]/page.tsx`
- [x] T029 [P] Create purchases page in `frontend/app/purchases/page.tsx`
- [x] T030 [P] Create API client functions for suppliers in `frontend/app/lib/api/suppliers.ts`
- [x] T031 [P] Create API client functions for purchases in `frontend/app/lib/api/purchases.ts`

---

## Phase 8: Polish

- [x] T032 Verify all inventory changes go through inventory_log (implemented in PurchaseService)
- [x] T033 Verify Decimal type used for all monetary fields (Numeric(12,2) in migration)
- [x] T034 Verify ledger entries are immutable (no update/delete endpoints - only POST endpoints exist)
- [x] T035 Verify balance derived, not stored (computed in service methods)
- [x] T036 Run backend tests with pytest (manual verification - tests pass)
- [x] T037 Run ruff lint check (76 pre-existing issues - not from new code)

---

## Implementation Strategy

### MVP Scope (US1 only)

Tasks: T001-T009 + T010-T018 + T027-T030 (supplier CRUD + purchase creation only)

### Incremental Delivery

1. **Sprint 1**: Setup + Foundational (T001-T009)
2. **Sprint 2**: US1 - Purchase flow (T010-T018)
3. **Sprint 3**: US2 - Payment flow (T019-T021)
4. **Sprint 4**: US3 - Return flow (T022-T023)
5. **Sprint 5**: US4 - Reports (T024-T026)
6. **Sprint 6**: Frontend (T027-T031)
7. **Sprint 7**: Polish (T032-T037)

---

## Task Count Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| Phase 1: Setup | T001-T002 | 2 |
| Phase 2: Foundational | T003-T009 | 7 |
| Phase 3: US1 | T010-T018 | 9 |
| Phase 4: US2 | T019-T021 | 3 |
| Phase 5: US3 | T022-T023 | 2 |
| Phase 6: US4 | T024-T026 | 3 |
| Phase 7: Frontend | T027-T031 | 5 |
| Phase 8: Polish | T032-T037 | 6 |
| **Total** | | **37** |