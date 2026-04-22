# Feature Specification: Customer Accounting System

**Feature Branch**: `009-customer-accounting`  
**Created**: 2026-04-21  
**Status**: Draft  
**Input**: User description: "We are implementing a full customer accounting system in EZOO POS. The system must support: Cash sales (no customer), Credit sales (with customer), Partial payments, Customer returns, Full ledger-based tracking. Must follow system constitution: Decimal only (no floats), Immutable financial records, Backend is source of truth. Core Concept: Customer balance is derived: balance = total_sales - total_payments - total_returns. Data Model: Customer (id, name, phone, address, notes, credit_limit, created_at), CustomerLedger (id, customer_id, type (SALE, PAYMENT, RETURN), amount (Decimal), reference_id (sale_id), payment_method (optional, for PAYMENT), created_at, note). Rules: append-only, no updates or deletes. POS Integration: customer_id is optional. If provided: create ledger entry: type = SALE, amount = grand_total. Payment Logic: During POS: partial or full payment allowed, store payment_method. After sale: POST /customers/{id}/payments, creates PAYMENT ledger entry. Return Logic: must be linked to sale, uses existing reversal system, creates: type = RETURN, amount = reversed amount. Credit Rules: enforce credit_limit, prevent sale if exceeded. Reports: Customer Summary (total_sales, total_payments, total_returns, balance), Customer Statement (list ledger entries, filter by date), Global Report (all customers, balances, top customers, overdue customers). Alerts: show warning if: balance > credit_limit. Frontend: /customers (table, balances), /customers/[id] (summary cards, ledger table, actions: add payment), POS (select customer, show balance, show warning if limit exceeded). Printing: customer statement, invoice, payment receipt. Constraints: no direct balance storage, no mutation of financial records, must integrate with reversal system. Acceptance Criteria: balance always correct after any sequence, credit limit enforced, returns reduce balance, partial payments work correctly."

## Clarifications

### Session 2026-04-21

- Q: How should payments be applied to outstanding sales? → A: **On Account (General)**: Payments just reduce the total balance (no specific invoice matching required).
- Q: Should the credit limit block be absolute, or should it allow for an override? → A: **User Confirmation**: The sale is blocked by default, but the user can explicitly confirm to proceed (due to single-role project structure).
- Q: How should the system handle a payment that exceeds the current balance? → A: **Allow (Credit Balance)**: Allow over-payment, resulting in a negative balance (customer credit).
- Q: Which user roles should be authorized to record customer payments? → A: **Any Staff**: The project uses a single-role system; all authenticated users have the same permissions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - POS Credit Sale (Priority: P1)

As a cashier, I want to sell items to a specific customer on credit so that their balance is updated and I can track their debt.

**Why this priority**: Core functionality for customer accounting. Without this, we cannot track customer sales.

**Independent Test**: Can be tested by performing a sale in the POS with a customer selected and verifying that a SALE entry appears in the customer ledger.

**Acceptance Scenarios**:

1. **Given** a customer with a 1000 credit limit and 0 balance, **When** a sale of 200 is made to this customer, **Then** a SALE ledger entry of 200 is created and the derived balance becomes 200.
2. **Given** a customer with a 1000 credit limit and 900 balance, **When** a sale of 200 is attempted, **Then** the system blocks the sale with a warning that the credit limit is exceeded.

---

### User Story 2 - Customer Payment (Priority: P1)

As an accountant, I want to record a payment from a customer so that their outstanding balance is reduced.

**Why this priority**: Essential for balancing the books. Customers need to be able to pay off their debt.

**Independent Test**: Can be tested by adding a payment to a customer and verifying that a PAYMENT entry appears and the derived balance decreases.

**Acceptance Scenarios**:

1. **Given** a customer with a 500 balance, **When** a payment of 300 is recorded, **Then** a PAYMENT ledger entry of 300 is created and the derived balance becomes 200.
2. **Given** a customer with a balance, **When** a partial payment is made during a POS sale, **Then** a SALE entry for the full amount and a PAYMENT entry for the partial amount are created.

---

### User Story 3 - Customer Returns (Priority: P2)

As a cashier, I want to process a return for a customer so that their debt is automatically reduced by the returned amount.

**Why this priority**: Necessary for accurate accounting when goods are returned.

**Independent Test**: Can be tested by initiating a reversal of a sale linked to a customer and verifying a RETURN entry in the ledger.

**Acceptance Scenarios**:

1. **Given** a customer has a sale of 100 recorded in the ledger, **When** that sale is returned/reversed for 50, **Then** a RETURN ledger entry of 50 is created and the balance decreases by 50.

---

### User Story 4 - Customer Statement & Reporting (Priority: P2)

As a manager, I want to view a customer's statement and a global report of all customer balances so that I can monitor debt levels and identify overdue accounts.

**Why this priority**: Important for business visibility and debt collection.

**Independent Test**: Can be tested by generating a statement for a customer and a global report and verifying the totals match the ledger entries.

**Acceptance Scenarios**:

1. **Given** a customer has multiple sales and payments, **When** I view their statement filtered by date, **Then** I see only the transactions within that date range.
2. **Given** multiple customers with varying balances, **When** I view the Global Report, **Then** I see a list of all customers, their total sales, total payments, total returns, and current balances.

---

### Edge Cases

- **What happens when a sale is partially paid?**: The system creates a SALE entry for the total amount and a separate PAYMENT entry for the amount paid. The balance correctly reflects the remaining debt.
- **How does the system handle a return if the sale was already fully paid?**: A RETURN entry is still created, which may result in a negative balance (credit) for the customer, which can be applied to future sales or refunded.
- **What happens if a customer pays more than their outstanding balance?**: The system allows the payment, which results in a negative (credit) balance that will be applied to future sales.
- **What happens if a customer is deleted?**: Financial records must be immutable. Deletion should be prevented if ledger entries exist, or handled via "archiving" while keeping ledger records.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support creating and managing Customer records with fields: id, name, phone, address, notes, credit_limit, and created_at.
- **FR-002**: System MUST implement an append-only CustomerLedger for all financial interactions (SALE, PAYMENT, RETURN).
- **FR-003**: System MUST calculate customer balance dynamically: `balance = total_sales - total_payments - total_returns`.
- **FR-004**: System MUST NOT allow updates or deletes of existing ledger entries.
- **FR-005**: System MUST enforce credit limits during POS checkout (using `remaining_amount` only), preventing sales that would exceed the limit unless explicitly confirmed by the user.
- **FR-006**: System MUST allow recording payments both during POS checkout (partial/full) and via a dedicated customer management interface; payments are applied "on account" to the general balance rather than linked to specific invoices.
- **FR-007**: System MUST integrate with the existing reversal system to automatically create RETURN ledger entries (amount = reversed financial amount) when a sale is reversed.
- **FR-008**: System MUST generate Customer Statements (ledger entries filtered by date) and Global Reports (all customers with balances).
- **FR-009**: System MUST display customer balance and credit limit warnings in the POS interface.
- **FR-010**: System MUST support printing customer statements, invoices, and payment receipts.
- **FR-011**: System MUST treat the backend as the sole source of truth for all financial data.
- **FR-012**: System MUST NOT store calculated balances in the database; they must always be derived from the ledger.

### Key Entities *(include if feature involves data)*

- **Customer**: Represents a person or entity with whom the business conducts credit transactions.
- **CustomerLedger**: An immutable log of all financial events related to a customer, serving as the source of truth for their balance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Derived customer balance is 100% accurate and reflects all ledger entries without exception.
- **SC-002**: POS checkout for credit sales is blocked within 100ms if the credit limit is exceeded.
- **SC-003**: Users can generate and view a full customer statement in under 2 seconds.
- **SC-004**: 100% of sale reversals for customer-linked sales result in a corresponding RETURN entry in the ledger.

## Assumptions

- **A-001**: The existing "reversal system" provides hooks or events that can be listened to for creating RETURN entries.
- **A-002**: PDF generation for printing will reuse existing system infrastructure.
- **A-003**: All monetary calculations use Decimal types to avoid floating-point errors, as per the system constitution.
- **A-004**: "Cash sales" without a customer do not create CustomerLedger entries.
- **A-005**: The system operates with a single user role; all accounting actions (payments, credit overrides) are accessible to any authenticated user.
