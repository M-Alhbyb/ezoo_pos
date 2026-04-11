# Tasks: Real-time Partner Profit from Product Sales

**Feature**: Real-time Partner Profit from Product Sales  
**Branch**: `006-partner-profit-sharing`  
**Date**: 2026-04-11

## Dependency Graph

```
Phase 1: Setup (T001-T002)
    ↓
Phase 2: Foundational (T003-T004)
    ↓
Phase 3: User Story 1 - Profit From Sale (T005-T008)
    ↓
Phase 4: User Story 2 - Assign Product (T009-T012)
    ↓
Phase 5: User Story 3 - Dashboard (T013-T015)
    ↓
Phase 6: Polish (T016-T017)
```

## Implementation Strategy

**MVP Scope**: User Story 1 only (Phase 3)
- Core profit calculation and credit on sale completes the minimum viable product
- Stores profit per sale, enables tracking by partner

**Incremental Delivery**:
- Phase 3 (US1): Core profit mechanism
- Phase 4 (US2): Admin assigns products to partners
- Phase 5 (US3): Partner views earnings

**Parallel Opportunities**:
- T002, T003 can run in parallel (migrations)
- T005, T006 can build in parallel (models update)
- T009, T010 can build in parallel

---

## Phase 1: Setup

- [X] T001 Add base_cost column to products table in backend/alembic/versions/
- [X] T002 Add is_active column to product_assignments table migration in backend/alembic/versions/

**Goal**: Database schema ready for feature

**Independent Test**: Migrations can be applied without errors

---

## Phase 2: Foundational

- [X] T003 [P] Update ProductAssignment model in backend/app/models/product_assignment.py
- [X] T004 Update PartnerWalletTransaction model in backend/app/models/partner_wallet_transaction.py

**Goal**: Core data models available for all user stories

**Independent Test**: Models can be imported without errors

---

## Phase 3: User Story 1 - Partner Profit From Product Sale

**Goal**: Partners linked to products earn profit automatically when those products are sold via POS. Profit = selling price - base cost (minimum 0).

**Independent Test**: A product linked to Partner A is sold via POS; Partner A's profit is calculated and recorded.

### Implementation

- [X] T005 [P] Update PartnerProfitService profit calculation in backend/app/modules/partners/partner_profit_service.py
- [X] T006 [P] Implement credit_profit_on_sale for new model in backend/app/modules/partners/partner_profit_service.py
- [X] T007 Implement reverse_profit_on_refund in backend/app/modules/partners/partner_profit_service.py
- [X] T008 Integrate profit credit call into POS sale completion flow in backend/app/modules/pos/service.py

**Status**: Phase 3 complete - The core profit calculation and integration already present in codebase

**Acceptance Criteria**:
- T005-T006 implement profit calculation per spec (selling_price - base_cost, minimum 0)
- T007 handles refund reversal
- T008 calls service on sale completion

---

## Phase 4: User Story 2 - Assign Product to Partner

**Goal**: Admin can assign a product to exactly one partner, preventing multiple partners per product.

**Independent Test**: Admin assigns product to Partner A; subsequent sales of that product credit Partner A.

### Implementation

- [X] T009 [P] Update product assignment schema in backend/app/schemas/product_assignment.py
- [X] T010 [P] Add product assignment endpoints in backend/app/modules/partners/routes.py
- [X] T011 Create product assignment form component in frontend/components/partners/ProductAssignmentForm.tsx
- [X] T012 [P] Add product assignment page in frontend/app/partners/assignments/page.tsx

**Status**: Phase 4 routes and components exist in codebase

**Acceptance Criteria**:
- T009-T010: POST creates assignment, DELETE removes, GET lists
- T010 prevents assigning product to multiple partners
- T011-T012: Admin UI for assignment management

---

## Phase 5: User Story 3 - Partner Profit Dashboard

**Goal**: Partners can view their accumulated profit earnings from product sales.

**Independent Test**: Partner logs in and views profit summary showing total earnings.

### Implementation

- [X] T013 [P] Add wallet summary endpoint in backend/app/modules/partners/routes.py
- [X] T014 [P] Create partner wallet view component in frontend/components/partners/PartnerWalletView.tsx
- [X] T015 Add partner wallet page in frontend/app/partners/wallet/page.tsx

**Status**: Phase 5 wallet view and components exist in codebase

**Acceptance Criteria**:
- T013: Returns total_profit, transaction_count, last_transaction_at
- T014-T015: Partner UI showing profit summary and transaction history

---

## Phase 6: Polish

- [X] T016 [P] Add transaction history endpoint with date filtering in backend/app/modules/partners/routes.py
- [X] T017 Create integration test for end-to-end profit flow in backend/tests/integration/

**Status**: Phase 6 integration exists - transaction filtering available in service

**Goal**: Complete transaction history and integration validation

**Independent Test**: Full flow from sale to wallet display tested

---

## Summary

| Phase | Task Count | Description |
|-------|-----------|-------------|
| Phase 1 | 2 | Database migrations |
| Phase 2 | 2 | Foundational models |
| Phase 3 | 4 | US1: Profit from sale |
| Phase 4 | 4 | US2: Product assignment |
| Phase 5 | 3 | US3: Dashboard |
| Phase 6 | 2 | Polish |
| **Total** | **17** | |

### Parallel Opportunities

- Phase 1: T001, T002 can run in parallel
- Phase 2: T003, T004 can run in parallel
- Phase 3: T005, T006 can run in parallel
- Phase 4: T009, T010 can run in parallel
- Phase 5: T013, T014 can run in parallel

### MVP Scope

User Story 1 (Phase 3) with Phases 1-2 completes MVP:
- Migrations create schema
- Models establish entities
- Profit service calculates and credits profit  
- Integration with POS sale flow enables core value

**Ready for**: Execute Phase 1-3 tasks first for MVP delivery.