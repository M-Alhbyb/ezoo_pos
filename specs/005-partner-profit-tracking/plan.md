# Implementation Plan: Partner Profit Tracking

**Branch**: `005-partner-profit-tracking` | **Date**: 2026-04-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-partner-profit-tracking/spec.md`

## Summary

Implement partner profit tracking system that allows assigning specific products/quantities to partners, calculating their profit share on sales, and maintaining wallet balances. The system integrates with existing sales workflow, uses atomic transactions with record locking for concurrency safety, and maintains full audit trails per constitution requirements.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5, PostgreSQL  
**Storage**: PostgreSQL (sole source of truth per constitution)  
**Testing**: pytest  
**Target Platform**: Linux server  
**Project Type**: Web service (FastAPI monolith backend + Next.js frontend)  
**Performance Goals**: <30s for assignment, <2s for profit calculation, <3s for wallet queries  
**Constraints**: Single-user POS (concurrent access still handled), DECIMAL types for all monetary values  
**Scale/Scope**: 100+ items across 10+ partners, full audit trail

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Evidence |
|-----------|-------------|--------|----------|
| **I. Financial Accuracy First** | All monetary calculations deterministic and reproducible | ✓ PASS | Profit calculated from stored values (quantity ×unit_price × share_percentage); all values persisted at transaction time |
| | Totals traceable to source line items | ✓ PASS | Every partner transaction references sale_id; balance_after stored on each transaction |
| | No hidden calculations | ✓ PASS | Each wallet transaction stores description with calculation breakdown |
| | DECIMAL type for all monetary values | ✓ PASS | `amount` and `balance_after` use Numeric(12, 2) |
| **II. Single Source of Truth** | PostgreSQL is the only authoritative data store | ✓ PASS | All partner data stored in PostgreSQL; wallet balance computed from transactions |
| | Backend owns business logic | ✓ PASS | All calculation in PartnerProfitService; frontend consumes API responses |
| | No secondary caches for financial data | ✓ PASS | No caching layer for wallet/transaction data |
| **III. Explicit Over Implicit** | Every value persisted at transaction time | ✓ PASS | ProductAssignment stores share_percentage; PartnerWalletTransaction stores amount, balance_after |
| | Percentages saved with transaction | ✓ PASS | Assignment has share_percentage override; Partner default stored once |
| | Recalculation uses stored values | ✓ PASS | Transaction records immutable; historical values preserved |
| **IV. Immutable Financial Records** | Confirmed records not edited in place | ✓ PASS | PartnerWalletTransaction immutable after creation |
| | Corrections via reversal entries | ⚠️ NOTE | Manual wallet adjustments supported via adjustment transactions (not reversals of sale transactions) |
| | Mutations timestamped and logged | ✓ PASS | created_at on all records; updated_at on mutable records |
| **V. Simplicity of Use** | Minimal clicks for POS operations | ✓ PASS | Assignment created once; profit calculation automatic on sale |
| | Financial breakdowns visible | ⚠️ NEEDS UI | Backend returns transaction history; frontend needs to display breakdown |
| | Clear error messages | ✓ PASS | Assignment conflicts raise explicit errors (insufficient quantity, partner not found) |
| **VI. Data Integrity** | DECIMAL type for monetary columns | ✓ PASS | All amount columns use Numeric(12, 2) |
| | Timestamps on all records | ✓ PASS | created_at on all entities; updated_at on ProductAssignment |
| | Stock never negative | ✓ PASS | remaining_quantity >= 0 CHECK constraint; assignment exhaustion checked before sale |
| | Inventory changes logged | ✓ PASS | Existing InventoryLog pattern; PartnerWalletTransaction logs all profit events |
| **VII. Backend Authority** | All validation in backend | ✓ PASS | Pydantic schemas validate input; service layer enforces business rules |
| | Frontend thin presentation layer | ✓ PASS | Frontend consumes API responses only |
| | WebSocket for real-time updates | 📋 TODO | May need WebSocket broadcast for wallet updates (optional enhancement) |
| **VIII. Input Validation** | All endpoints validate against schemas | ✓ PASS | Pydantic schemas for all create/update endpoints |
| | Structured error responses | ✓ PASS | Consistent error response format existing pattern |
| **IX. Extensibility by Design** | Supports multi-user | ✓ PASS | user_id inherited from BaseModel |
| | Supports multi-branch | ✓ PASS | branch_id inherited from BaseModel |
| | No schema changes destroy historical records | ✓ PASS | New tables added; no breaking changes to existing tables |

**Constitution Check Status**: ✓ PASS (with notes)

**Notes**:
- Manual wallet adjustments use adjustment transactions (consistent with existing patterns)
- Frontend UI needs to display transaction breakdowns (implementation detail)
- WebSocket broadcast optional (can be added in future phase)

## Project Structure

### Documentation (this feature)

```text
specs/005-partner-profit-tracking/
├── spec.md              # Feature specification (initialized)
├── plan.md              # This file
├── research.md          # Phase 0 output (initialized)
├── data-model.md        # Phase 1 output (pending)
├── quickstart.md        # Phase 1 output (pending)
├── contracts/           # Phase 1 output (pending)
│   ├── api.md           # REST API contracts
│   └── schemas.md       # Pydantic schema definitions
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── partner.py                    # Existing - extend with relationships
│   │   ├── partner_distribution.py       # Existing - for reference
│   │   ├── product_assignment.py         # NEW - Product Assignment entity
│   │   ├── partner_wallet_transaction.py # NEW - Wallet Transaction entity
│   │   └── __init__.py                   # Update with new models
│   ├── schemas/
│   │   ├── partner.py                    # Existing - extend with wallet schemas
│   │   ├── product_assignment.py         # NEW - Assignment schemas
│   │   └── __init__.py                   # Update
│   ├── modules/
│   │   ├── partners/
│   │   │   ├── service.py                # Existing - extend with new methods
│   │   │   ├── routes.py                 # Existing - extend with new endpoints
│   │   │   └── partner_profit_service.py # NEW - Profit calculation logic
│   │   └── pos/
│   │       └── service.py                # Existing - integrate profit processing
│   └── alembic/
│       └── versions/
│           └── xxxx_add_partner_profit_tracking.py  # NEW - Migration
│
└── tests/
    ├── unit/
    │   ├── test_partner_profit_service.py    # NEW - Unit tests
    │   └── test_product_assignment.py        # NEW - Unit tests
    └── integration/
        └── test_partner_wallet_flow.py        # NEW - Integration tests

frontend/
└── src/
    ├── components/
    │   └── partners/
    │       ├── ProductAssignmentForm.tsx     # NEW - Assignment creation
    │       ├── PartnerWalletView.tsx         # NEW - Wallet display
    │       └── AssignmentList.tsx            # NEW - Assignment list
    └── app/
        └── partners/
            ├── assignments/
            │   └── page.tsx                  # NEW - Assignment management page
            └── wallet/
                └── [partnerId]/
                    └── page.tsx              # NEW - Partner wallet page
```

**Structure Decision**: Single backend monolith with existing module structure. New models added to existing models/ directory. New service (PartnerProfitService) added to modules/partners/. Frontend adds new pages under partners/ route following existing Next.js 14 App Router pattern.

## Complexity Tracking

> No constitution violations requiring justification.

All complexity is within approved patterns:
- Hybrid wallet balance (balance_after per transaction) follows existing PartnerDistribution snapshot pattern
- Atomic transaction processing follows existing InventoryService pattern
- New tables added without modifying existing schema (additive only)