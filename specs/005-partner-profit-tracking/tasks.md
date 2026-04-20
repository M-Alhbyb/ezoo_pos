# Tasks: Partner Profit Tracking

**Input**: Design documents from `/specs/005-partner-profit-tracking/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included based on constitution principles requiring financial accuracy validation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web application**: `backend/app/`, `frontend/src/`
- Paths shown assume FastAPI monolith backend and Next.js frontend

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database schema and module structure initialization

- [x] T001 Create Alembic migration for partner profit tracking tables in backend/alembic/versions/73cb9f780be4_add_partner_profit_tracking.py
- [x] T002 Run database migration to create product_assignments and partner_wallet_transactions tables
- [x] T003 Create partner_profit_service.py module structure in backend/app/modules/partners/partner_profit_service.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and schemas that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create ProductAssignment model in backend/app/models/product_assignment.py
- [x] T005 [P] Create PartnerWalletTransaction model in backend/app/models/partner_wallet_transaction.py
- [x] T006 Update backend/app/models/__init__.py to export ProductAssignment and PartnerWalletTransaction
- [x] T007 [P] Create ProductAssignment Pydantic schemas in backend/app/schemas/product_assignment.py
- [x] T008 [P] Extend partner schemas for wallet in backend/app/schemas/partner.py
- [x] T009 Update backend/app/schemas/__init__.py to export new schemas
- [x] T010 Initialize PartnerProfitService class structure in backend/app/modules/partners/partner_profit_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Assign Products to Partners (Priority: P1) 🎯 MVP

**Goal**: Enable business owners to assign product quantities to partners, establishing the partner-product relationship

**Independent Test**: Create a partner, assign products/quantities to them, verify the assignment persists correctly with proper tracking of assigned vs remaining quantities

### Tests for User Story 1

- [x] T011 [P] [US1] Create unit test for ProductAssignment model in tests/unit/test_product_assignment.py
- [x] T012 [P] [US1] Create integration test for assignment creation workflow in tests/integration/test_partner_product_assignment.py

### Implementation for User Story 1

- [x] T013 [US1] Implement create_assignment method in backend/app/modules/partners/service.py
- [x] T014 [US1] Implement get_assignment, list_assignments methods in backend/app/modules/partners/service.py
- [x] T015 [US1] Implement update_assignment method in backend/app/modules/partners/service.py
- [x] T016 [US1] Implement delete_assignment method in backend/app/modules/partners/service.py
- [x] T017 [US1] Add assignment management endpoints in backend/app/modules/partners/routes.py (POST/GET/PATCH/DELETE /assignments)
- [x] T018 [US1] Add validation for one active assignment per product constraint
- [x] T019 [US1] Extend Product endpoint GET /api/v1/products to include assignment information in response

**Checkpoint**: Assignment CRUD operations should now work independently - can create, read, update, delete assignments and view product inventory with assignment status

---

## Phase 4: User Story 2 - Calculate and Track Partner Profits (Priority: P2)

**Goal**: Automatically calculate partner profit share on sales and update wallet balances

**Independent Test**: Sell products that are assigned to partners, verify: (1) partner profit calculated correctly (quantity × unit_price × share_percentage), (2) wallet balance updated, (3) assignment remaining_quantity decreased

### Tests for User Story 2

- [x] T020 [P] [US2] Create unit test for profit calculation logic in tests/unit/test_partner_profit_service.py
- [x] T021 [P] [US2] Create integration test for sale-with-profit-distribution in tests/integration/test_partner_wallet_flow.py

### Implementation for User Story 2

- [x] T022 [US2] Implement get_partner_for_update with SELECT FOR UPDATE locking in backend/app/modules/partners/partner_profit_service.py
- [x] T023 [US2] Implement get_product_assignment_for_update with SELECT FOR UPDATE locking in backend/app/modules/partners/partner_profit_service.py
- [x] T024 [US2] Implement calculate_partner_profit method in backend/app/modules/partners/partner_profit_service.py (quantity × unit_price × share_percentage)
- [x] T025 [US2] Implement credit_partner_wallet method in backend/app/modules/partners/partner_profit_service.py (creates PartnerWalletTransaction)
- [x] T026 [US2] Implement process_sale_partner_profits method in backend/app/modules/partners/partner_profit_service.py (main integration point)
- [x] T027 [US2] Integrate partner profit processing into SaleService.create_sale in backend/app/modules/pos/service.py (call after stock deduction, before commit)
- [x] T028 [US2] Add error handling for profit calculation failures per FR-014 (rollback entire sale if calculation fails)
- [x] T029 [US2] Implement concurrent sales safety with sorted lock ordering to prevent deadlocks

**Checkpoint**: Automatic profit distribution should now work - selling assigned products credits partner wallets atomically

---

## Phase 5: User Story 3 - Maintain Partner Wallet Balance (Priority: P2)

**Goal**: Enable administrators to view partner wallet balances and transaction history

**Independent Test**: View partner wallet after sales occur, verify balance matches sum of transactions, transaction history shows all profit credits and manual adjustments with timestamps

### Tests for User Story 3

- [x] T030 [P] [US3] Create unit test for wallet balance calculation in tests/unit/test_partner_wallet.py
- [x] T031 [P] [US3] Create integration test for manual wallet adjustment in tests/integration/test_partner_wallet_flow.py

### Implementation for User Story 3

- [x] T032 [US3] Implement get_partner_wallet_balance method in backend/app/modules/partners/service.py (O(1) using balance_after on latest transaction)
- [x] T033 [US3] Implement get_partner_wallet_transactions method in backend/app/modules/partners/service.py (paginated history)
- [x] T034 [US3] Implement adjust_wallet method in backend/app/modules/partners/service.py (manual adjustments)
- [x] T035 [US3] Add wallet management endpoints in backend/app/modules/partners/routes.py (GET /wallet, GET /wallet/transactions, POST /wallet/adjust)
- [x] T036 [US3] Add authorization check for admin-only wallet access per FR-013

**Checkpoint**: Wallet viewing and manual adjustments should now work independently - administrators can view balances, transaction history, and make manual adjustments

---

## Phase 6: User Story 4 - Handle Partial Sales from Assigned Inventory (Priority: P3)

**Goal**: Support selling fewer units than assigned, with proper remaining_quantity tracking

**Independent Test**: Assign 10 units to partner, sell 3 units, verify: (1) partner profit for 3 units only, (2) remaining_quantity updated to 7, (3) assignment remains active

### Tests for User Story 4

- [x] T037 [P] [US4] Create integration test for partial sale from assigned inventory in tests/integration/test_partner_wallet_flow.py

### Implementation for User Story 4

- [x] T038 [US4] Verify existing process_sale_partner_profits handles partial sales correctly (remaining_quantity deduction already implemented in US2)
- [x] T039 [US4] Add edge case handling: selling more than assigned quantity (use assigned_quantity only)
- [x] T040 [US4] Add auto-fulfillment logic when remaining_quantity reaches zero per FR-015
- [x] T041 [US4] Add validation for assignment status transitions (active → fulfilled)

**Checkpoint**: Partial sale handling should work - remaining_quantity tracking and fulfillment auto-close

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T042 [P] Add logging for all partner profit operations in backend/app/modules/partners/partner_profit_service.py
- [x] T043 [P] Add error handling documentation in backend/app/schemas/errors.py for assignment-specific errors
- [x] T044 [P] Create frontend ProductAssignmentForm component in frontend/src/components/partners/ProductAssignmentForm.tsx
- [x] T045 [P] Create frontend AssignmentList component in frontend/src/components/partners/AssignmentList.tsx
- [x] T046 [P] Create frontend PartnerWalletView component in frontend/src/components/partners/PartnerWalletView.tsx
- [x] T047 Create assignment management page in frontend/src/app/partners/assignments/page.tsx
- [x] T048 Create partner wallet page in frontend/src/app/partners/wallet/[partnerId]/page.tsx
- [x] T049 [P] Add unit tests for edge cases in tests/unit/test_partner_profit_service.py (concurrent sales, assignment exhaustion, zero remaining)
- [x] T050 Run quickstart.md validation scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 (ProductAssignment must exist to calculate profits) - But independently testable once assignments exist
- **User Story 3 (P2)**: Depends on User Story 2 (wallet transactions from profit distribution) - But independently testable for manual adjustments
- **User Story 4 (P3)**: Depends on User Story 2 (builds on profit calculation flow) - Refines existing behavior

### Within Each User Story

- Tests (T011-T012, T020-T021, T030-T031, T037) can run in parallel with each other
- Models (T004-T005, T007-T008) must complete before services (T013-T016)
- Services (T013-T016) must complete before endpoints (T017)
- Core implementation before integration (T027)

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T001-T003)
- All Foundational tasks marked [P] can run in parallel within Phase 2 (T004-T005, T007-T009)
- Tests for each story can run in parallel (T011-T012, T020-T021)
- Different user stories can be worked on in parallel by different team members after Phase 2 completes
- Polish tasks T042-T049 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "T011 [P] [US1] Create unit test for ProductAssignment model"
Task: "T012 [P] [US1] Create integration test for assignment creation workflow"

# Launch all parallelizable models for foundational:
Task: "T004 [P] Create ProductAssignment model"
Task: "T005 [P] Create PartnerWalletTransaction model"
Task: "T007 [P] Create ProductAssignment Pydantic schemas"
Task: "T008 [P] Extend partner schemas for wallet"
```

---

## Implementation Strategy

### MVP First (User Story 1 + Foundational)

1. Complete Phase 1: Setup (database migration)
2. Complete Phase 2: Foundational (models and schemas) - CRITICAL
3. Complete Phase 3: User Story 1 (Product Assignment)
4. **STOP and VALIDATE**: Test assignment creation, reading, updating independently
5. Deploy/demo if ready (basic product-partner assignment works)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP! Assignments work)
3. Add User Story 2 → Test independently → Deploy/Demo (Profit calculation works)
4. Add User Story 3 → Test independently → Deploy/Demo (Wallet viewing works)
5. Add User Story 4 → Test independently → Deploy/Demo (Partial sales work correctly)
6. Add Polish → Final validation and frontend → Full feature complete

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (Phases 1-2)
2. Once Foundational is done:
   - Developer A: User Story 1 (Assignments)
   - Developer B: User Story 2 (Profit calculation - *wait for US1 models to complete*)
   - Developer C: User Story 3 (Wallet viewing - *wait for US2 core to complete*)
3. Stories complete and integrate independently
4. User Story 4 can be started after US2 core is complete

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- US1 (Assignments) is the foundation - US2 and US3 extend from it
- Financial calculations use DECIMAL types per constitution principle I
- All wallet transactions are immutable per constitution principle IV
- Concurrent sales handled with SELECT FOR UPDATE locking per research.md
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence