# Implementation Plan: Customer Accounting System

**Branch**: `009-customer-accounting` | **Date**: 2026-04-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/009-customer-accounting/spec.md`

## Summary

Implement a robust, ledger-based customer accounting system for EZOO POS. The system uses an append-only `CustomerLedger` to track all financial interactions (SALE, PAYMENT, RETURN) and derives the current balance dynamically (`total_sales - total_payments - total_returns`). This ensures 100% auditability and follows the "Immutable Financial Records" principle. Key features include credit limit enforcement with user confirmation, "on account" payment allocation, and global debt reporting.

## Technical Context

**Language/Version**: Python 3.11 (Backend), TypeScript 5.x (Frontend)  
**Primary Dependencies**: FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5, Next.js 14, React 18, TailwindCSS 3.4  
**Storage**: PostgreSQL (via existing SQLAlchemy models)  
**Testing**: pytest (backend unit/integration tests)  
**Target Platform**: Linux server / Web Browser  
**Project Type**: Web Application (POS)  
**Performance Goals**: <100ms for credit limit checks, <2s for statement generation  
**Constraints**: Immutable financial records, Decimal-only monetary values, Backend as sole source of truth  
**Scale/Scope**: Full accounting module for local business customers  

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Implementation Strategy |
|-----------|:------:|-------------------------|
| **I. Financial Accuracy First** | ✅ | Using `Decimal` for all `amount` fields; balance is always derived from source ledger entries. |
| **II. Single Source of Truth** | ✅ | Backend calculates all balances; frontend consumes API responses without local computation. |
| **III. Explicit Over Implicit** | ✅ | Ledger entries store `type`, `amount`, `reference_id`, and `payment_method` explicitly. |
| **IV. Immutable Financial Records** | ✅ | `CustomerLedger` is append-only; updates and deletes are blocked at the application/ORM level. |
| **V. Simplicity of Use** | ✅ | POS integration shows balance and credit warnings clearly with simple confirmation flows. |
| **VI. Data Integrity** | ✅ | PostgreSQL `DECIMAL` types and foreign key constraints on `customer_id` and `sale_id`. |
| **VII. Backend Authority** | ✅ | FastAPI handles all validation and balance derivation; credit limits enforced at the API layer. |
| **VIII. Input Validation** | ✅ | Pydantic schemas for all ledger entry creations and payment recordings. |
| **IX. Extensibility by Design** | ✅ | Schema includes `customer_id` and `reference_id` to allow future cross-module tracking. |

## Project Structure

### Documentation (this feature)

```text
specs/009-customer-accounting/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (API definitions)
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   ├── customer.py      # Customer and CustomerLedger models
│   ├── schemas/
│   │   ├── customer.py      # Pydantic schemas for IO
│   ├── api/
│   │   ├── v1/
│   │   │   ├── customers.py # API endpoints for management/ledger
│   ├── services/
└── tests/
    ├── unit/
    │   ├── test_accounting.py # Calculation unit tests

frontend/
├── src/
│   ├── components/
│   │   ├── customers/       # Ledger table, statement viewer
│   ├── pages/
│   │   ├── customers/       # List and Detail (ID) pages
│   ├── services/
│   │   ├── api.ts           # Customer API client methods
```

**Structure Decision**: Web application structure (backend/frontend split) to maintain separation of concerns and backend authority.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations detected.*
