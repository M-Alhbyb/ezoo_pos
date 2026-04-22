# Feature Specification: Supplier Accounting System

**Feature Branch**: `008-supplier-accounting`  
**Created**: 2026-04-20  
**Status**: Draft  
**Input**: User description: "We are extending EZOO POS with a full supplier accounting system..."

## User Scenarios & Testing *(mandatory)*

**Note on Roles**: All authenticated users can perform all supplier accounting operations (create purchases, record payments, returns, view reports).

### User Story 1 - Purchase Inventory from Supplier (Priority: P1)

As a purchasing staff member, I want to create purchase orders from suppliers so that I can restock inventory on credit.

**Why this priority**: This is the core function of the supplier accounting system. Without purchases, there is no supplier debt to track.

**Independent Test**: Can create a purchase with items, see inventory increase, and verify ledger entry created with correct amount.

**Acceptance Scenarios**:

1. **Given** a supplier exists in the system, **When** I create a purchase with multiple items (product, quantity, unit_cost), **Then** purchase is created, inventory increases by quantity, and ledger shows PURCHASE entry for total_amount.
2. **Given** a supplier with existing purchases, **When** I view supplier details, **Then** I see correct balance derived from all transactions.
3. **Given** product prices change after purchase, **When** I view the original purchase, **Then** original unit_cost is preserved (snapshot).

---

### User Story 2 - Record Supplier Payment (Priority: P1)

As a financial staff member, I want to record payments to suppliers so that I can track debt reduction over time.

**Why this priority**: Payments are essential to reduce supplier debt and maintain good vendor relationships.

**Independent Test**: Can record payment, verify ledger entry created, and see balance correctly reduced.

**Acceptance Scenarios**:

1. **Given** a supplier with outstanding balance, **When** I record a payment amount, **Then** ledger entry created with type PAYMENT and balance reduced accordingly.
2. **Given** a partial payment is made, **When** I view supplier balance, **Then** remaining balance is correctly shown (not zero).
3. **Given** multiple payments over time, **When** I view supplier statement, **Then** all payment entries visible with dates and notes.

---

### User Story 3 - Return Items to Supplier (Priority: P2)

As inventory manager, I want to return items to suppliers so that I can manage defective or excess stock.

**Why this priority**: Returns are common business operations for damaged goods or overstock situations.

**Independent Test**: Can initiate return from existing purchase, verify inventory decreased and ledger shows RETURN entry.

**Acceptance Scenarios**:

1. **Given** a purchase exists with items, **When** I return some items from that purchase, **Then** inventory decreases and RETURN ledger entry created.
2. **Given** I try to return more than purchased, **When** I submit return request, **Then** system rejects with error message.
3. **Given** a return is processed, **When** I view supplier balance, **Then** balance is correctly reduced by return amount.

---

### User Story 4 - View Supplier Reports (Priority: P2)

As business owner/manager, I want to view supplier financial reports so that I can understand outstanding obligations.

**Why this priority**: Financial visibility is critical for cash flow management and vendor relationships.

**Independent Test**: Can view all suppliers with balances or single supplier statement with date filtering.

**Acceptance Scenarios**:

1. **Given** multiple suppliers with transactions, **When** I view supplier summary report, **Then** each supplier shows total_purchases, total_payments, total_returns, and balance.
2. **Given** a supplier with many transactions, **When** I view supplier statement with date range, **Then** only entries within range are shown.
3. **Given** need to print, **When** I request supplier statement, **Then** printable format available with all relevant details.

---

## Scope Boundaries

**Out of Scope:**
- Advanced inventory management (beyond stock take)
- Supplier price catalogs/lists management
- Purchase requisition workflows, approval chains
- Supplier performance analytics beyond basic totals

**In Scope (Explicit):**
- Supplier ledger accounting
- Purchase creation and inventory increase
- Payments recording
- Returns processing with inventory decrease
- Basic stock take functionality

### Edge Cases

- What happens when attempting to return more items than originally purchased?
- How does system handle negative stock after return (should prevent)?
- What occurs when supplier has zero balance and payment is recorded?
- How are ledger entries affected if system crashes mid-transaction (must be atomic)?
- What when product is deleted after being purchased (should still show in historical data)?

## Clarifications

### Session 2026-04-20

- Q: Supplier name uniqueness → A: Allow duplicate names (distinguish by ID)
- Q: Out-of-scope features → A: Supplier purchase orders/GRN only + basic stock take functionality
- Q: User permissions → A: Single role (all can do all operations)
- Q: Performance requirements → A: Standard web response times

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow creation of suppliers with name (required), phone (optional), and notes (optional). Duplicate names allowed; suppliers distinguished by unique ID.
- **FR-002**: System MUST allow creating purchases from suppliers with multiple line items (product, quantity, unit_cost).
- **FR-003**: System MUST calculate total_cost as quantity × unit_cost for each purchase item.
- **FR-004**: System MUST snapshot unit_cost at time of purchase and preserve it in historical records.
- **FR-005**: System MUST create SupplierLedger entry with type = PURCHASE when purchase is created.
- **FR-006**: System MUST increase inventory stock when purchase is created.
- **FR-007**: System MUST create inventory_log entries for all stock changes.
- **FR-008**: System MUST allow recording payments to suppliers.
- **FR-009**: System MUST create SupplierLedger entry with type = PAYMENT when payment is recorded.
- **FR-010**: System MUST allow returning items from a specific purchase.
- **FR-011**: System MUST prevent returning more quantity than originally purchased.
- **FR-012**: System MUST use original unit_cost snapshot when calculating return amount.
- **FR-013**: System MUST decrease inventory stock when return is processed.
- **FR-014**: System MUST create SupplierLedger entry with type = RETURN for returns.
- **FR-015**: System MUST derive supplier balance from ledger: purchases - payments - returns.
- **FR-016**: System MUST NOT store balance directly; it must be derived.
- **FR-017**: System MUST make all ledger entries immutable (append-only, no updates or deletes).
- **FR-018**: System MUST support supplier summary report showing totals per supplier.
- **FR-019**: System MUST support supplier statement with date range filtering.
- **FR-020**: All monetary fields MUST use Decimal type, never floating point.

### Key Entities *(include if feature involves data)*

- **Supplier**: Vendor entity with contact information and created timestamp.
- **Purchase**: Supplier invoice/order, immutable after creation, linked to supplier and items.
- **PurchaseItem**: Individual line item in a purchase with product, quantity, and unit_cost snapshot.
- **SupplierLedger**: Append-only financial transaction record; source of truth for balance calculation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can complete a purchase transaction in under 2 minutes. API responses under 2 seconds for typical operations.
- **SC-002**: Supplier balance is always mathematically correct: balance = total_purchases - total_payments - total_returns.
- **SC-003**: All financial transactions survive system restart (persisted to database).
- **SC-004**: Return requests are rejected if quantity exceeds original purchase. 100% rejection rate on over-return attempts.
- **SC-005**: Historical purchase data remains unchanged even if product prices change later.

## Assumptions

- Users have stable database connectivity during transactions.
- Product catalog exists and products can be selected for purchases.
- Existing inventory_log pattern will be reused for stock changes.
- Decimal utility functions exist in the codebase and will be reused.
- API follows RESTful conventions consistent with existing endpoints.
- Frontend will be Next.js with TypeScript following existing patterns.
