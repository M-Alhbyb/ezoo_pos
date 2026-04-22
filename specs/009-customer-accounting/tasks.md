# Tasks: Customer Accounting System

**Input**: Design documents from `/specs/009-customer-accounting/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and base migrations

- [X] T001 Create Customer and CustomerLedger migration in `backend/alembic/versions/`
- [X] T002 [P] Register Customer models in `backend/app/models/__init__.py`
- [X] T003 [P] Add customer-related constants/enums in `backend/app/core/constants.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure for customer management and balance derivation

- [X] T004 Create Customer model in `backend/app/models/customer.py`
- [X] T005 Create CustomerLedger model in `backend/app/models/customer.py` (same file)
- [X] T006 Create Customer Pydantic schemas in `backend/app/schemas/customer.py`
- [X] T007 Implement basic `CustomerService` skeleton in `backend/app/modules/customers/service.py`
- [X] T008 Implement balance derivation logic using SQL aggregation in `backend/app/modules/customers/service.py`
- [X] T009 [P] Setup customer API routes in `backend/app/modules/customers/routes.py`
- [X] T010 [P] Register customers module in `backend/app/main.py`
- [X] T010.5 Implement immutability enforcement (SQLAlchemy listeners) for `CustomerLedger` in `backend/app/models/customer.py`

**Checkpoint**: Foundation ready - customer management and balance calculation is functional.

---

## Phase 3: User Story 1 - POS Credit Sale (Priority: P1) 🎯 MVP

**Goal**: Enable selling items on credit to a selected customer with credit limit enforcement.

**Independent Test**: Perform a sale in POS with a customer selected; verify SALE entry in ledger and balance update.

### Implementation for User Story 1

- [X] T011 [US1] Add nullable `customer_id` to `Sale` model in `backend/app/models/sale.py`
- [X] T012 [US1] Update `SaleCreate` schema to include optional `customer_id` and ensure it is nullable in `backend/app/schemas/sale.py`
- [X] T013 [US1] Implement `check_credit_limit` (using `remaining_amount` only) in `backend/app/modules/customers/service.py`
- [X] T014 [US1] Integrate credit limit check into `SaleService.create_sale` in `backend/app/modules/pos/service.py`
- [X] T015 [US1] Implement SALE ledger entry creation (amount = grand_total - paid_amount) in `SaleService.create_sale`
- [X] T015.5 [US1] Implement PAYMENT ledger entry creation for `paid_amount` during sale in `SaleService.create_sale`
- [X] T016 [P] [US1] Update POS frontend to allow customer selection and display balance in `frontend/src/components/pos/CustomerSelector.tsx`
- [X] T017 [US1] Implement credit limit warning/confirmation dialog in `frontend/src/components/pos/CreditWarningModal.tsx`
- [X] T017.5 [US1] Add real-time balance display in POS UI in `frontend/src/components/pos/POSHeader.tsx`

**Checkpoint**: User Story 1 is functional. Credit sales correctly update the customer ledger.

---

## Phase 4: User Story 2 - Customer Payment (Priority: P1)

**Goal**: Allow recording customer payments to reduce their outstanding balance.

**Independent Test**: Record a payment via the customer detail page; verify PAYMENT entry in ledger and balance decrease.

### Implementation for User Story 2

- [X] T018 [US2] Implement `record_payment` in `backend/app/modules/customers/service.py`
- [X] T019 [US2] Create payment recording endpoint in `backend/app/modules/customers/routes.py`
- [X] T019.5 [US2] Ensure no duplicate payment entries via idempotency/locking in `backend/app/modules/customers/service.py`
- [X] T020 [P] [US2] Create Payment recording form in `frontend/src/components/customers/PaymentForm.tsx`
- [X] T021 [US2] Add "Add Payment" action to Customer detail page in `frontend/src/pages/customers/[id].tsx`

**Checkpoint**: User Story 2 is functional. Payments correctly reduce customer debt.

---

## Phase 5: User Story 3 - Customer Returns (Priority: P2)

**Goal**: Automatically record returns in the customer ledger when a sale is reversed.

**Independent Test**: Reverse a customer-linked sale; verify RETURN entry in ledger.

### Implementation for User Story 3

- [X] T022 [US3] Update `SaleService.reverse_sale` to detect customer-linked sales in `backend/app/modules/pos/service.py`
- [X] T023 [US3] Implement RETURN ledger entry creation (amount = reversed financial amount) in `SaleService.reverse_sale`
- [X] T024 [P] [US3] Ensure reversal UI displays customer impact in `frontend/src/components/pos/ReversalDetail.tsx`

**Checkpoint**: User Story 3 is functional. Returns are correctly tracked in the ledger.

---

## Phase 6: User Story 4 - Customer Statement & Reporting (Priority: P2)

**Goal**: Provide detailed transaction history and global debt reports.

**Independent Test**: View a customer statement filtered by date; verify all entries appear correctly.

### Implementation for User Story 4

- [X] T025 [US4] Implement ledger listing with date filters in `backend/app/modules/customers/service.py`
- [X] T026 [US4] Create global customer report endpoint in `backend/app/modules/customers/routes.py`
- [X] T027 [P] [US4] Implement Ledger table component in `frontend/src/components/customers/LedgerTable.tsx`
- [X] T028 [P] [US4] Implement Global Report page in `frontend/src/pages/reports/CustomersReport.tsx`
- [X] T029 [US4] Implement PDF statement generation service in `backend/app/modules/reports/pdf_service.py`
- [X] T030 [P] [US4] Add "Print Statement" button to frontend in `frontend/src/pages/customers/[id].tsx`

**Checkpoint**: All user stories are functional. Full visibility into customer debt is available.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and verification

- [X] T031 [P] Add unit tests for balance calculation in `backend/tests/unit/test_accounting.py`
- [X] T032 [P] Add integration tests for credit limit enforcement in `backend/tests/integration/test_credit_limit.py`
- [X] T032.5 Add performance test for customer statement generation (SC-003) in `backend/tests/performance/test_accounting_speed.py`
- [X] T033 Code cleanup and validation against `quickstart.md`
- [X] T034 [P] Final UI/UX polish for customer management pages

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 & 2**: MUST be completed first.
- **Phase 3 (US1)**: Priority 1.
- **Phase 4 (US2)**: Priority 1. Can run in parallel with US1 if models are ready.
- **Phase 5 & 6 (US3, US4)**: Priority 2. Depend on foundational accounting logic.

### Parallel Opportunities
- Frontend development ([P] tasks) can run in parallel with backend once API contracts are stable.
- US1 and US2 implementation can be split between developers.
- Reports and Statement generation (Phase 6) can be worked on independently.

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Setup (Phase 1)
2. Complete Foundational (Phase 2)
3. Complete US1 (Phase 3)
4. **STOP and VALIDATE**: Verify that credit sales work and the ledger records the SALE.

### Incremental Delivery
1. Foundation → Basic Customer CRUD
2. US1 → Credit Sales (Debt accumulation)
3. US2 → Payments (Debt reduction)
4. US3 → Returns (Correction logic)
5. US4 → Statements (Visibility)
