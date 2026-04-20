# EZOO POS — Implementation Plan

> Revised: 2026-04-04
> Source: ChatGPT draft, reviewed and amended against project constitution.
> Constitution: `.specify/memory/constitution.md` v1.0.0

---

## Clarifications (from review session 2026-04-04)

- Q: Sale lifecycle — draft or immediate?
  → A: **No draft state.** Sale is immediately confirmed on submit.
  Corrections via reversal / credit note.
- Q: How are recurring expenses applied?
  → A: **Manual trigger.** Expenses store frequency metadata; system
  calculates correct amounts on-demand for a user-selected date range.
- Q: When is partner profit distributed?
  → A: **Manual trigger with date range.** System sums project profits
  in that range, applies each partner's percentage, creates an
  immutable distribution record.
- Q: How are payment methods handled?
  → A: **Separate `payment_methods` table**, fully configurable from
  settings (user can add/edit methods).
- Q: How are products organized?
  → A: **Name + optional SKU + category.** POS search by name or SKU.

---

## 1. Execution Strategy

Build in **vertical slices**, not layers.

- ❌ Wrong: finish all DB → all backend → all frontend
- ✅ Correct: build feature end-to-end → test → move to next

Each phase produces a **working, testable feature**.

---

## 2. Phases Overview

| Phase | Scope | Depends On |
|-------|-------|------------|
| 0 | Foundation (project scaffolding, DB, base UI) | — |
| 1 | Core POS + Products + Inventory | Phase 0 |
| 2 | Projects + Expenses | Phase 1 |
| 3 | Partners + Profit Distribution | Phase 2 |
| 4 | Reports + Finalization | Phase 3 |

---

## 3. Phase 0 — Foundation

### 3.1 Database

- Setup PostgreSQL
- Create migration framework (Alembic)
- Create foundational tables:

| Table | Purpose |
|-------|---------|
| `settings` | Global config (VAT enabled, VAT type/value, default fees) |
| `categories` | Product categories (solar panels, batteries, inverters…) |
| `payment_methods` | Configurable payment methods (cash, card, transfer…) |

- **Extensibility rule (Constitution IX):** All tables that will hold
  business data MUST include `user_id` and `branch_id` columns
  (nullable, defaulting to a single-user/single-branch value).
  This prevents future migration pain.

### 3.2 Backend (FastAPI)

Project structure:

```
app/
├── core/               # config, security, exceptions, calculation engine
├── db/                 # database connection, session, base model
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic request/response schemas
├── modules/
│   ├── products/       # routes, service, schemas
│   ├── pos/            # routes, service, schemas
│   ├── inventory/      # routes, service, schemas
│   ├── projects/       # routes, service, schemas
│   ├── expenses/       # routes, service, schemas
│   ├── partners/       # routes, service, schemas
│   ├── reports/        # routes, service, schemas
│   └── settings/       # routes, service, schemas
└── websocket/          # WS manager for real-time POS updates
```

Setup:

- DB connection pool (async SQLAlchemy)
- Alembic migrations config
- Base model with `id`, `created_at`, `updated_at`, `user_id`, `branch_id`
- Global exception handler returning structured error responses
- Calculation engine stub (`app/core/calculations.py`)

### 3.3 Frontend (Next.js 14)

- Setup App Router
- Setup root layout with navigation sidebar
- Create base design system (colors, typography, spacing)
- Setup API client (axios / fetch wrapper)
- Setup WebSocket client (reconnection logic)

### 3.4 Deliverable

- App runs end-to-end
- DB connected with migrations working
- Empty UI renders with navigation
- Settings page showing VAT config + payment methods CRUD

---

## 4. Phase 1 — Core POS + Products + Inventory

> This is the most important phase.

### 4.1 Database Tables

| Table | Key Columns | Notes |
|-------|-------------|-------|
| `categories` | `id`, `name` | Already created in Phase 0 |
| `products` | `id`, `name`, `sku` (nullable unique), `category_id` (FK), `base_price` (DECIMAL), `selling_price` (DECIMAL), `stock_quantity` (INTEGER), timestamps | `stock_quantity >= 0` constraint |
| `sales` | `id`, `payment_method_id` (FK), `subtotal`, `fees_total`, `vat_rate`, `vat_amount`, `total`, `note`, timestamps | Immutable after creation |
| `sale_items` | `id`, `sale_id` (FK), `product_id` (FK), `product_name` (snapshot), `quantity`, `unit_price` (DECIMAL), `line_total` (DECIMAL) | Stores price at time of sale |
| `sale_fees` | `id`, `sale_id` (FK), `fee_type` (shipping/installation/custom), `fee_label`, `fee_value_type` (fixed/percent), `fee_value` (DECIMAL), `calculated_amount` (DECIMAL) | Constitution III: explicit fee storage |
| `sale_reversals` | `id`, `original_sale_id` (FK), `reversal_sale_id` (FK nullable), `reason`, `created_at` | Links original sale to its reversal |
| `inventory_log` | `id`, `product_id` (FK), `delta` (INTEGER), `reason` (sale/restock/adjustment), `reference_id` (nullable), `balance_after` (INTEGER), `created_at` | Constitution VI: every change logged |

**Constitution compliance:**
- All monetary columns use `DECIMAL(12,2)`
- All tables include timestamps
- All tables include `user_id`, `branch_id` (extensibility)
- `sale_fees` stores type + value + calculated amount (Constitution III)
- `inventory_log` records every stock change (Constitution VI)

### 4.2 Backend

#### Product Module (`/api/products`)

- `POST /` — Create product (with category, prices, initial stock)
- `GET /` — List products (filter by category, search by name/SKU)
- `GET /{id}` — Get product detail
- `PUT /{id}` — Update product (name, prices, category)
- `DELETE /{id}` — Soft delete (set `is_active = false`; products
  referenced in sales MUST NOT be hard-deleted)

#### Category Module (`/api/categories`)

- `POST /` — Create category
- `GET /` — List categories
- `PUT /{id}` — Update category
- `DELETE /{id}` — Delete (only if no products reference it)

#### POS Module (`/api/sales`)

- `POST /` — Create sale (immediately confirmed, immutable)
  - Receives: list of items (product_id, quantity), list of fees,
    payment_method_id
  - Backend calculates: subtotal, fee amounts, VAT (from settings),
    total
  - Backend validates: stock availability for all items
  - On success: deducts stock, creates inventory_log entries,
    returns full sale breakdown
  - **Atomic transaction**: sale + stock deduction + log in single
    DB transaction
- `GET /` — List sales (paginated, filterable by date range)
- `GET /{id}` — Get sale detail with items + fees breakdown
- `POST /{id}/reverse` — Create reversal
  - Creates a new "negative" sale (or credit note) that cancels the
    original
  - Restores stock for all items
  - Creates inventory_log entries with reason "reversal"
  - Links via `sale_reversals` table

#### Inventory Module (`/api/inventory`)

- `POST /restock` — Add stock to a product (creates inventory_log)
- `POST /adjust` — Manual adjustment with reason (creates inventory_log)
- `GET /log/{product_id}` — View stock change history for a product

#### Calculation Engine (`app/core/calculations.py`)

Centralized, pure functions:

```python
def calculate_sale_total(items, fees, vat_settings) -> SaleBreakdown
def calculate_fee_amount(fee_value, fee_type, subtotal) -> Decimal
def calculate_vat(amount, vat_type, vat_value) -> Decimal
```

- **Constitution II**: This is the ONLY place financial calculations
  live
- **Constitution I**: All inputs and outputs are Decimal, never float

### 4.3 Frontend

#### Pages

- `/products` — Product list with category filter, add/edit modal
- `/pos` — POS interface

#### POS UI Components

| Component | Responsibility |
|-----------|---------------|
| `ProductSearch` | Search by name or SKU, shows results with stock info |
| `POSCart` | Cart with items, quantities, line totals |
| `FeeEditor` | Add/edit fees (shipping, installation, custom) |
| `VATToggle` | Shows VAT status from settings, displays VAT amount |
| `PaymentMethodSelect` | Dropdown of configured payment methods |
| `SaleBreakdown` | Shows subtotal, fees, VAT, total (read-only from backend) |
| `ConfirmButton` | Submits sale; disabled until all validation passes |

#### Data Flow

1. User adds products to cart → frontend sends cart to
   `POST /api/sales/preview` (optional preview endpoint)
2. Backend returns calculated breakdown (subtotal, fees, VAT, total)
3. User confirms → frontend sends to `POST /api/sales`
4. Backend validates, creates sale, returns confirmation

#### WebSocket

- Connected on POS page load
- Backend pushes updated stock levels after any sale/restock
- Frontend updates product search results in real-time

### 4.4 Deliverable

- ✅ Fully working POS with product search, cart, fees, VAT
- ✅ Stock deducted on sale with full audit log
- ✅ Sale reversals working
- ✅ Products CRUD with categories
- ✅ All financial calculations in backend only

### 4.5 Phase 1 Testing Scenarios

```
1. Add 3 products (Panel A: base=100, sell=150, stock=10)
2. Create sale: 2x Panel A + shipping fee $20
3. Verify: subtotal=300, fees=20, VAT correct, total correct
4. Verify: Panel A stock = 8
5. Verify: inventory_log has entry (delta=-2, reason=sale)
6. Reverse the sale
7. Verify: Panel A stock = 10
8. Verify: inventory_log has reversal entry
9. Verify: original sale has linked reversal record
```

---

## 5. Phase 2 — Projects + Expenses

### 5.1 Database Tables

| Table | Key Columns | Notes |
|-------|-------------|-------|
| `projects` | `id`, `name`, `description`, `status` (draft/in_progress/completed), `selling_price` (DECIMAL), `total_cost` (DECIMAL, calculated), `profit` (DECIMAL, calculated), timestamps | Immutable when `status = completed` |
| `project_items` | `id`, `project_id` (FK), `product_id` (FK), `product_name` (snapshot), `quantity`, `unit_cost` (DECIMAL = base_price at time of adding), `line_total` | Uses base_price, not selling_price |
| `expenses` | `id`, `project_id` (FK, nullable = global), `name`, `expense_type` (fixed/percent), `value` (DECIMAL), `frequency` (daily/weekly/monthly/once), `is_active` (BOOLEAN), timestamps | Frequency stored as metadata |

**Project lifecycle:**
- `draft` → editable (add/remove items, expenses, change selling price)
- `in_progress` → editable (same as draft, signals work has started)
- `completed` → **immutable** (Constitution IV). No edits allowed.
  Corrections require creating a new project or re-opening (status
  change back to `in_progress` with a log entry).

### 5.2 Backend

#### Project Module (`/api/projects`)

- `POST /` — Create project (status = draft)
- `GET /` — List projects (filter by status)
- `GET /{id}` — Get project with items, expenses, cost breakdown
- `PUT /{id}` — Update project (only if status ≠ completed)
- `POST /{id}/items` — Add product to project (stores base_price
  as unit_cost snapshot)
- `DELETE /{id}/items/{item_id}` — Remove item (only if status ≠ completed)
- `PUT /{id}/status` — Change status (draft → in_progress → completed)
  - On completion: calculate and store `total_cost` and `profit`
  - These stored values are used for partner distribution

#### Expense Module (`/api/expenses`)

- `POST /` — Create expense (global or project-specific)
- `GET /` — List expenses (filter by scope, frequency, active status)
- `PUT /{id}` — Update expense
- `DELETE /{id}` — Deactivate expense (soft delete)

#### Expense Calculation (on-demand)

```python
def calculate_expenses_for_period(
    expenses: list[Expense],
    start_date: date,
    end_date: date
) -> Decimal:
    """
    For each expense:
    - once: apply full value if created within period
    - daily: value × days in period
    - weekly: value × weeks in period
    - monthly: value × months in period
    For percent-type: apply against project selling_price or
    total revenue (depending on scope)
    """
```

#### Profit Calculation

```python
def calculate_project_profit(project) -> ProjectProfitBreakdown:
    total_cost = sum(item.line_total for item in project.items)
    project_expenses = calculate_project_expenses(project)
    total_cost += project_expenses
    profit = project.selling_price - total_cost
    return ProjectProfitBreakdown(...)
```

### 5.3 Frontend

#### Pages

- `/projects` — Project list with status badges
- `/projects/{id}` — Project detail (items, expenses, profit breakdown)
- `/expenses` — Global expenses management

#### Project UI Components

| Component | Responsibility |
|-----------|---------------|
| `ProjectForm` | Create/edit project name, description, selling price |
| `ProjectItemList` | Add products (using base_price), show cost breakdown |
| `ProjectExpenseList` | Attach expenses, show calculated totals |
| `ProfitSummary` | Visual breakdown: cost, expenses, selling price, profit |
| `StatusBadge` | Shows draft/in_progress/completed with color coding |

### 5.4 Deliverable

- ✅ Full project lifecycle (draft → in_progress → completed)
- ✅ Accurate profit calculation (selling_price − costs − expenses)
- ✅ Expense engine supporting fixed/percent, frequency, scope
- ✅ Completed projects are immutable

### 5.5 Phase 2 Testing Scenarios

```
1. Create project "Solar Install A"
2. Add products: 5x Panel ($100 base) + 2x Battery ($200 base)
3. Add project expense: installation labor $500 (once, fixed)
4. Add global expense: office rent $1000/month
5. Set selling price: $2500
6. Verify: total_cost = 500 + 400 + 500 = $1400
7. Verify: profit = $2500 - $1400 = $1100
   (global expenses applied separately in reports)
8. Complete project → verify it becomes immutable
9. Try to edit → verify rejection
```

---

## 6. Phase 3 — Partners + Profit Distribution

### 6.1 Database Tables

| Table | Key Columns | Notes |
|-------|-------------|-------|
| `partners` | `id`, `name`, `invested_amount` (DECIMAL), `profit_percentage` (DECIMAL), `is_active`, timestamps | |
| `partner_distributions` | `id`, `distribution_date`, `period_start`, `period_end`, `total_profit` (DECIMAL), `notes`, `created_at` | Immutable after creation. One record per distribution run. |
| `partner_distribution_items` | `id`, `distribution_id` (FK), `partner_id` (FK), `percentage_used` (DECIMAL), `profit_share` (DECIMAL) | Stores the percentage at time of calculation (Constitution III) |

### 6.2 Backend

#### Partner Module (`/api/partners`)

- `POST /` — Create partner
- `GET /` — List partners
- `PUT /{id}` — Update partner (name, invested_amount, percentage)
- `DELETE /{id}` — Deactivate (soft delete)

#### Distribution Module (`/api/distributions`)

- `POST /` — Trigger distribution
  - Receives: `period_start`, `period_end`
  - Calculates: sum of profits from all **completed** projects
    within that date range
  - For each active partner: `share = total_profit × percentage`
  - Stores: distribution record + per-partner items with
    **percentage at time of calculation** (Constitution III)
  - This record is **immutable** (Constitution IV)
- `GET /` — List past distributions
- `GET /{id}` — Distribution detail with per-partner breakdown

#### Validation

- Partner percentages MUST be validated (0 < percentage ≤ 100)
- Sum of all active partner percentages should be warned (but not
  blocked) if it exceeds 100%
- Distribution MUST NOT include projects already distributed in
  a previous run (prevent double-counting)

### 6.3 Frontend

#### Pages

- `/partners` — Partner list with invested amounts and percentages

#### UI Components

| Component | Responsibility |
|-----------|---------------|
| `PartnerList` | List partners with financial summary |
| `PartnerForm` | Add/edit partner details |
| `DistributionTrigger` | Date range picker + calculate button |
| `DistributionResult` | Shows per-partner profit shares, total |
| `DistributionHistory` | Past distributions with detail drill-down |

### 6.4 Deliverable

- ✅ Partner CRUD with invested amounts
- ✅ Manual profit distribution with date range
- ✅ Immutable distribution records with snapshot percentages
- ✅ No double-counting of project profits

### 6.5 Phase 3 Testing Scenarios

```
1. Create Partner A (60%) and Partner B (40%)
2. Complete 2 projects with profits: $1000 and $500
3. Trigger distribution for date range covering both projects
4. Verify: total_profit = $1500
5. Verify: Partner A share = $900, Partner B share = $600
6. Verify: percentages stored in distribution record
7. Trigger another distribution for same period
8. Verify: already-distributed projects are excluded
9. Verify: distribution record is immutable
```

---

## 7. Phase 4 — Reports + Finalization

### 7.1 Backend

#### Report Endpoints (`/api/reports`)

| Endpoint | Returns |
|----------|---------|
| `GET /sales` | Sales summary: count, totals, by payment method, by date range |
| `GET /profit` | Profit summary: revenue, costs, expenses, net profit for period |
| `GET /inventory` | Current stock levels, low stock alerts, stock movement history |
| `GET /partners` | Partner earnings: invested vs. earned, distribution history |
| `GET /projects` | Project profitability: per-project cost/profit breakdown |

All reports:
- Accept `start_date` and `end_date` query parameters
- Return JSON with totals and detailed breakdowns
- **Constitution (Reporting):** MUST NOT modify any data
- **Constitution (Reporting):** Generated from stored data only

### 7.2 Frontend

#### Pages

- `/reports` — Report dashboard with sub-views

#### Views

| View | Content |
|------|---------|
| Sales | Daily/monthly totals, filterable by date range, payment method breakdown |
| Profit | Revenue vs. costs chart, expense impact, net profit |
| Inventory | Stock levels table, low-stock highlights, movement log |
| Partners | Per-partner earnings, distribution history timeline |
| Projects | Per-project profitability comparison |

### 7.3 Deliverable

- ✅ Full financial visibility across all domains
- ✅ Date range filtering on all reports
- ✅ Read-only reports (no data mutation)

---

## 8. Cross-Cutting Systems

### 8.1 Settings Engine

Stored in `settings` table as key-value pairs with typed values.

| Setting | Type | Example |
|---------|------|---------|
| `vat_enabled` | boolean | `true` |
| `vat_type` | enum | `percent` or `fixed` |
| `vat_value` | decimal | `16.00` |
| `default_fees` | json | `[{type: "shipping", value: 0}]` |

**Used by:** POS module, Project module, Report calculations.

**API:** `GET /api/settings`, `PUT /api/settings`

### 8.2 Calculation Engine (Critical)

Location: `app/core/calculations.py`

All financial logic lives here. **No other module may compute
financial values.** Frontend MUST NOT duplicate any calculation.

Functions:

- `calculate_sale_total(items, fees, vat_settings) → SaleBreakdown`
- `calculate_fee_amount(fee_value, fee_type, subtotal) → Decimal`
- `calculate_vat(amount, vat_type, vat_value) → Decimal`
- `calculate_project_profit(project) → ProjectProfitBreakdown`
- `calculate_expenses_for_period(expenses, start, end) → Decimal`
- `calculate_partner_distribution(total_profit, partners) → list[PartnerShare]`

**Rules:**
- All inputs/outputs are `Decimal` — never `float`
- All functions are **pure** (no DB access, no side effects)
- Services call these functions and handle persistence

### 8.3 Validation Layer

Backend validates all inputs at the API boundary:

| Check | Where |
|-------|-------|
| Stock availability ≥ requested quantity | POS service |
| All monetary values ≥ 0 | Pydantic schemas |
| Partner percentages 0 < p ≤ 100 | Partner schemas |
| Product prices: selling_price ≥ base_price | Product schemas |
| Fee values > 0 | POS schemas |
| Required fields present | Pydantic schemas |
| Immutable record not modified | Service layer checks |

---

## 9. API Structure

```
/api/
├── products/          # CRUD + search
├── categories/        # CRUD
├── sales/             # Create, list, detail, reverse
├── inventory/         # Restock, adjust, log
├── projects/          # CRUD + items + status transitions
├── expenses/          # CRUD (global + project-scoped)
├── partners/          # CRUD
├── distributions/     # Trigger + history
├── reports/           # Sales, profit, inventory, partners, projects
├── settings/          # Global configuration
└── payment-methods/   # CRUD
```

---

## 10. Frontend Structure

```
app/                        # Next.js App Router
├── layout.tsx              # Root layout with sidebar nav
├── pos/
│   └── page.tsx            # POS interface
├── products/
│   └── page.tsx            # Product management
├── projects/
│   ├── page.tsx            # Project list
│   └── [id]/page.tsx       # Project detail
├── expenses/
│   └── page.tsx            # Expense management
├── partners/
│   └── page.tsx            # Partner management + distributions
├── reports/
│   └── page.tsx            # Report dashboard
└── settings/
    └── page.tsx            # Settings (VAT, fees, payment methods)

components/
├── pos/
│   ├── ProductSearch.tsx
│   ├── POSCart.tsx
│   ├── FeeEditor.tsx
│   ├── SaleBreakdown.tsx
│   └── ConfirmButton.tsx
├── projects/
│   ├── ProjectForm.tsx
│   ├── ProjectItemList.tsx
│   └── ProfitSummary.tsx
├── partners/
│   ├── PartnerList.tsx
│   ├── DistributionTrigger.tsx
│   └── DistributionResult.tsx
├── reports/
│   ├── SalesReport.tsx
│   ├── ProfitReport.tsx
│   └── InventoryReport.tsx
└── shared/
    ├── DataTable.tsx
    ├── Modal.tsx
    ├── StatusBadge.tsx
    └── DateRangePicker.tsx
```

---

## 11. Data Flow Rules

1. Frontend sends **raw input** (product IDs, quantities, fee values)
2. Backend **calculates everything** (totals, VAT, profit)
3. Backend returns **complete breakdown** (subtotal, fees, VAT, total)
4. Frontend **displays** the breakdown — never computes financial values
5. WebSocket pushes **stock updates** and **sale confirmations** in
   real-time to connected POS clients

---

## 12. Testing Strategy

After **each phase**, create real scenarios and verify:

| Phase | Test Focus |
|-------|-----------|
| 1 | Add products → sell → verify stock → verify totals → reverse → verify restore |
| 2 | Create project → add items + expenses → complete → verify profit → verify immutability |
| 3 | Create partners → complete projects → distribute → verify shares → verify no double-count |
| 4 | Run all reports → verify numbers match Phase 1–3 data → verify no data mutation |

**Rule:** Do NOT move to next phase if numbers are wrong.

---

## 13. Risk Areas

| # | Risk | Mitigation |
|---|------|------------|
| 1 | Profit calculation mistakes | Centralized calculation engine with unit tests |
| 2 | Percentage vs. fixed confusion | Explicit `value_type` enum on every fee/expense/VAT |
| 3 | Expense application scope | Clear `project_id` nullable FK (null = global) |
| 4 | Stock inconsistency | Atomic transactions + inventory_log audit trail |
| 5 | Double-counting distributed profits | Track which projects are included in each distribution |
| 6 | Floating point errors | DECIMAL everywhere, never float (Constitution I) |
| 7 | Immutability violations | Service-layer guards on status checks before mutations |

---

## 14. Database Schema Summary

```
categories
products ──────────── FK → categories
payment_methods

sales ─────────────── FK → payment_methods
sale_items ─────────── FK → sales, products
sale_fees ──────────── FK → sales
sale_reversals ─────── FK → sales (original + reversal)
inventory_log ──────── FK → products

projects
project_items ──────── FK → projects, products
expenses ───────────── FK → projects (nullable = global)

partners
partner_distributions
partner_distribution_items ── FK → partner_distributions, partners

settings
```

---

## 15. Constitution Compliance Checklist

| Principle | How It's Addressed |
|-----------|-------------------|
| I. Financial Accuracy | Centralized calculation engine, DECIMAL types, pure functions |
| II. Single Source of Truth | PostgreSQL only, backend calculates, frontend displays |
| III. Explicit Over Implicit | `sale_fees` stores type+value+amount; percentages stored at distribution time |
| IV. Immutable Records | Sales immediate + reversal; completed projects locked; distributions locked |
| V. Simplicity of Use | Minimal-click POS, real-time updates, clear breakdowns |
| VI. Data Integrity | DECIMAL columns, timestamps everywhere, stock ≥ 0, inventory_log |
| VII. Backend Authority | All validation + calculation in FastAPI, frontend is display-only |
| VIII. Input Validation | Pydantic schemas, service-layer guards, structured error responses |
| IX. Extensibility | user_id + branch_id on all tables, soft deletes, modular structure |
