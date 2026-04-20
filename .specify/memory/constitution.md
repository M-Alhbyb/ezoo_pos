<!--
  SYNC IMPACT REPORT
  ==================
  Version change: 0.0.0 → 1.0.0
  Bump rationale: MAJOR — initial ratification of all principles
    and governance rules (no prior version existed).

  Modified principles: N/A (initial creation)

  Added sections:
    - Core Principles (9 principles: I–IX)
    - Domain Rules (Products, Sales, Inventory, Projects, Partners,
      Expenses, VAT & Fees, Reporting)
    - Development Workflow (Tech stack, API contract, testing,
      deployment)
    - Governance

  Removed sections: None

  Templates requiring updates:
    ✅ plan-template.md — Constitution Check section is generic;
       compatible with new principles (no changes needed).
    ✅ spec-template.md — No constitution-specific constraints
       referenced; compatible as-is.
    ✅ tasks-template.md — Task categorization is generic;
       compatible as-is.

  Deferred items: None
-->

# EZOO POS Constitution

## Core Principles

### I. Financial Accuracy First

All monetary calculations MUST be deterministic and reproducible.

- All totals MUST be traceable to their source line items
- Profit MUST always be derived from stored data, never computed
  ad-hoc from volatile state
- No hidden calculations: every fee, discount, and adjustment
  MUST appear explicitly in the transaction record
- All monetary values MUST be stored as `DECIMAL`; floating-point
  types are strictly prohibited

### II. Single Source of Truth

PostgreSQL is the only authoritative data store.

- The backend MUST be the sole owner of business logic and
  calculations
- The frontend MUST NOT contain duplicated financial logic; it
  consumes API responses only
- No secondary caches or derived stores may serve as a source of
  truth for financial data

### III. Explicit Over Implicit

Every value that affects a financial outcome MUST be persisted at
the time of the transaction.

- Every fee MUST store: type, value, and final calculated amount
- Every percentage (VAT rate, partner share, expense rate) MUST be
  saved with the transaction or distribution record
- Recalculation MUST NOT rely on current global configuration;
  historical records MUST use their own stored values

### IV. Immutable Financial Records

Confirmed financial records MUST NOT be edited in place.

- Sales, project results, and partner distributions are immutable
  after confirmation
- Corrections MUST be performed via reversal entries or new
  compensating transactions
- Every mutation to financial state MUST be timestamped and logged

### V. Simplicity of Use

The system MUST prioritize speed and clarity for daily POS
operations.

- Sale completion MUST require minimal clicks
- Financial breakdowns (subtotal, fees, VAT, total) MUST be visible
  on every transaction screen
- Error messages MUST be clear, specific, and blocking — the user
  MUST NOT be able to proceed past a validation failure silently

### VI. Data Integrity

All persisted data MUST satisfy strict integrity constraints.

- All monetary columns MUST use `DECIMAL` / `NUMERIC` types
- All records MUST carry a created-at timestamp; mutable records
  MUST also carry an updated-at timestamp
- Stock levels MUST never go below zero; the system MUST reject
  any operation that would cause a negative stock balance
- Every inventory change MUST be logged with reason, quantity
  delta, and resulting balance

### VII. Backend Authority

The FastAPI monolith is the single enforcement point for all
business rules.

- All validation, calculation, and authorization MUST occur in the
  backend
- The frontend MUST NOT enforce business rules; it MAY provide
  optimistic UI hints but the backend is authoritative
- WebSocket is used exclusively for real-time POS updates pushed
  from backend to frontend

### VIII. Input Validation

The system MUST validate all inputs despite being single-user.

- All API endpoints MUST validate request payloads against schemas
- Invalid input MUST return structured error responses
- No endpoint may trust client-side validation alone

### IX. Extensibility by Design

The data model and architecture MUST support future growth without
breaking existing data.

- Schema design MUST anticipate multi-user support (user ID foreign
  keys, even if only one user exists today)
- Schema design MUST anticipate multi-branch support (branch ID
  columns or equivalent)
- Advanced accounting features MUST be addable without migrations
  that destroy historical records

## Domain Rules

### Products

- Each product MUST have `base_price` and `selling_price`
- Product profit = `selling_price − base_price`
- Stock MUST never go below zero

### Sales (POS)

- A sale consists of one or more line items, optional extra fees
  (shipping, installation, custom), and optional VAT
- VAT applies only when enabled in system settings
- VAT rate and amount MUST be stored per sale
- Sale total MUST equal: `Σ(line items) + Σ(fees) + VAT`

### Inventory

- Stock decreases on sale confirmation
- Stock increases only via manual adjustment or restock entry
- Every stock change MUST be logged with timestamp, delta, reason,
  and resulting balance

### Projects

- A project represents a solar installation job
- `total_cost = Σ(product costs) + Σ(expenses)`
- `profit = selling_price − total_cost`
- Projects MUST track their own products, expenses, and final
  selling price independently

### Partners

- Each partner has `invested_amount` and `profit_percentage`
- `partner_profit = total_profit × percentage`
- The percentage used MUST be the one stored at calculation time,
  not the current global value

### Expenses

- Expenses may be fixed amount or percentage-based
- Expenses may be global or project-specific
- Supported frequencies: daily, weekly, monthly, once
- The system MUST apply expenses correctly based on scope and
  frequency

### VAT and Fees

- VAT is configurable as fixed amount or percentage
- VAT can be enabled or disabled globally via settings
- Extra fees (shipping, installation, custom) MUST each store:
  type, value, and final calculated amount

### Reporting

- Reports MUST be generated from stored data only
- Required reports: sales summary, profit summary, inventory
  status, partner earnings, project profitability
- Report generation MUST NOT modify any data

## Development Workflow

### Technology Stack

- **Backend**: Python / FastAPI (monolith)
- **Database**: PostgreSQL (sole source of truth)
- **Frontend**: Consumes backend APIs only
- **Real-time**: WebSocket for POS live updates

### API Contract

- All business logic lives in the backend
- Frontend is a thin presentation layer
- Every API response MUST include enough data for the frontend to
  render without local computation of financial values

### Testing Discipline

- Financial calculation functions MUST have unit tests covering
  edge cases (zero quantities, zero prices, maximum values)
- Integration tests MUST verify that confirmed records cannot be
  mutated via API
- Inventory tests MUST verify that stock cannot go negative

### Non-Goals (Current Version)

The system will NOT:

- Handle external accounting integrations
- Support multi-currency
- Include complex tax systems beyond VAT

## Governance

- This constitution supersedes all other development guidelines
  for the EZOO POS project
- Amendments MUST be documented with a version bump, rationale,
  and migration plan if data model changes are involved
- Every feature spec and implementation plan MUST include a
  Constitution Check verifying compliance with these principles
- Complexity beyond what the constitution permits MUST be
  explicitly justified in the plan's Complexity Tracking table
- Use this constitution as the runtime development guidance
  reference

**Version**: 1.0.0 | **Ratified**: 2026-04-04 | **Last Amended**: 2026-04-04
