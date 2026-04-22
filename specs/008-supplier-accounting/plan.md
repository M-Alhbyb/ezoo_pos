# Implementation Plan: Supplier Accounting System

**Branch**: `008-supplier-accounting` | **Date**: 2026-04-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-supplier-accounting/spec.md`

## Summary

A ledger-based supplier accounting system enabling purchasing inventory from suppliers on credit, recording payments over time, and processing returns. All financial tracking uses immutable records derived from SupplierLedger entries - balance is computed (not stored) as purchases - payments - returns. Follows EZOO POS constitution: Decimal-only monetary fields, append-only ledger, inventory_log for all stock changes.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript (frontend)  
**Primary Dependencies**: FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5, PostgreSQL, Next.js 14  
**Storage**: PostgreSQL (sole source of truth per constitution)  
**Testing**: pytest (backend), existing frontend testing patterns  
**Target Platform**: Linux server (backend), Web browser (frontend)  
**Project Type**: Web service with frontend  
**Performance Goals**: API responses under 2 seconds (from SC-001)  
**Constraints**: No floating point, immutable financial records, atomic transactions  
**Scale/Scope**: Single-branch POS system, standard supplier volumes  

## Constitution Check

| Constitution Principle | Compliance | Notes |
|----------------------|-------------|-------|
| I. Financial Accuracy - Decimal only | ✅ PASS | All monetary fields use Decimal per FR-020 |
| II. Single Source of Truth - PostgreSQL | ✅ PASS | All data in PostgreSQL, frontend consumes API only |
| III. Explicit Over Implicit | ✅ PASS | Unit cost snapshot stored per FR-004, FR-012 |
| IV. Immutable Financial Records | ✅ PASS | Ledger entries are append-only per FR-017 |
| V. Simplicity of Use | ✅ PASS | Standard POS workflow patterns |
| VI. Data Integrity | ✅ PASS | Stock cannot go negative per edge cases, all changes logged |
| VII. Backend Authority | ✅ PASS | All validation in backend |
| VIII. Input Validation | ✅ PASS | Pydantic schemas for all endpoints |
| IX. Extensibility by Design | ✅ PASS | Schema supports multi-branch, user ID FKs |

**Gate Status**: ✅ PASSED - No violations

## Project Structure

### Documentation (this feature)

```text
specs/008-supplier-accounting/
├── plan.md              # This file
├── research.md          # Phase 0 (not needed - no clarifications)
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API contracts)
└── tasks.md             # Phase 2 (via /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── models/              # SQLAlchemy models (Supplier, Purchase, PurchaseItem, SupplierLedger)
├── services/            # Business logic services
├── api/                 # FastAPI routes
└── utils/               # Decimal utilities (reused)

frontend/
├── src/
│   ├── components/      # Supplier, Purchase, Payment UI components
│   ├── pages/           # /suppliers, /purchases routes
│   └── services/        # API client functions
└── tests/
```

**Structure Decision**: Follows existing EZOO POS structure - backend FastAPI with SQLAlchemy, frontend Next.js with TypeScript. New files in `src/models/`, `src/services/`, `src/api/`, `frontend/src/pages/`.

## Complexity Tracking

No Constitution violations requiring justification.

## Phase 1: Design Artifacts

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

### API Contracts

See [contracts/](./contracts/) for endpoint specifications.

### Quick Start

See [quickstart.md](./quickstart.md) for development setup.
