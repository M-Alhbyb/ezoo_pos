# Feature Specification: Core POS, Products, and Inventory Management

**Feature Branch**: `001-core-pos-products-inventory`
**Created**: 2026-04-04
**Status**: Draft
**Input**: User description: "Build the core point-of-sale system with product catalog management, real-time inventory tracking, and sale processing including fees, VAT, and reversals — as defined in Phase 1 of the implementation plan."

## Clarifications

### Session 2026-04-04

- Q: Does the system support partial reversals, or only full-sale reversals? → A: Full reversal only. The entire sale is reversed as one atomic operation. Partial returns are handled by reversing the full sale and creating a new sale for the items the customer kept.
- Q: What rounding rule should the system use for decimal financial calculations? → A: ROUND_HALF_UP (standard commercial rounding). All monetary results are rounded to 2 decimal places using this rule (e.g., 3.335 → 3.34, 3.334 → 3.33).
- Q: Are operators allowed to override the unit price of a product during a sale? → A: Yes. Operators can manually edit the unit price for any item added to the cart, overriding the default catalog selling price for that specific transaction.
- Q: How should the system handle attempts to add a zero-stock product to the cart? → A: Prevent adding to cart. The action is blocked entirely if the available quantity is zero. The operator must first restock the item if it is physically available.
- Q: Should the system explicitly require a backend API call to calculate the financial breakdown as the sale is being built? → A: Yes. A dedicated calculation endpoint (e.g., `POST /api/sales/calculate`) is required. The frontend must not compute financial totals; it must call the backend whenever the cart, prices, or fees change to retrieve the authoritative breakdown.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Complete a Sale (Priority: P1)

The shop operator opens the POS screen, searches for products by name or SKU, adds them to the cart with desired quantities, **optionally adjusts the unit price (overriding the catalog default)**, optionally adds extra fees (shipping, installation, or custom), selects a payment method, and confirms the sale. The system instantly calculates the full financial breakdown — subtotal (using overridden prices where applicable), individual fee amounts, VAT (if enabled), and grand total — and presents it before confirmation. On confirmation the sale is recorded permanently and stock is deducted.

**Why this priority**: This is the primary revenue-generating action. Without the ability to complete a sale, the system has no business value. Every other feature depends on sales data existing.

**Independent Test**: Can be fully tested by adding products to the system, performing a sale through the POS, and verifying the resulting sale record, financial breakdown, and stock deduction.

**Acceptance Scenarios**:

1. **Given** products exist with sufficient stock, **When** the operator adds 2 units of "Panel A" (selling price 150) and 1 unit of "Battery B" (selling price 200) plus a fixed shipping fee of 30 to the cart and confirms, **Then** the system records a sale with subtotal = 500, fees = 30, VAT calculated per settings, and total = subtotal + fees + VAT; stock for both products decreases by the purchased quantities.
2. **Given** VAT is enabled at 16% in settings, **When** a sale is confirmed with subtotal 500 and fees 30, **Then** the VAT amount = (500 + 30) × 0.16 = 84.80, and total = 614.80.
3. **Given** VAT is disabled in settings, **When** a sale is confirmed, **Then** no VAT is applied and the total = subtotal + fees.
4. **Given** a product has 0 units in stock, **When** the operator attempts to add it to the cart from the search results, **Then** the system MUST block the action and prevent the item from being added to the cart.
5. **Given** a product has 3 units in stock, **When** the operator attempts to sell 5 units, **Then** the system rejects the sale with a clear error message indicating insufficient stock.
6. **Given** a sale is confirmed, **When** the operator views the sale detail, **Then** the full breakdown is displayed: each line item with product name, quantity, unit price, and line total; each fee with type, value, and calculated amount; VAT rate and amount; grand total; and payment method used.

---

### User Story 2 — Manage Product Catalog (Priority: P2)

The shop operator manages a catalog of solar panels, batteries, and accessories. They can create new products with a name, optional SKU, category, base price (cost), selling price, and initial stock quantity. They can update product details and organize products into categories. Products referenced in past sales cannot be permanently removed.

**Why this priority**: Products are the foundation of both POS sales and project costing. The catalog must exist before any sale can happen. Ranked P2 because it is a prerequisite for P1 but is simpler setup work.

**Independent Test**: Can be fully tested by creating, updating, and organizing products with categories, then verifying data persists correctly and search works.

**Acceptance Scenarios**:

1. **Given** a category "Solar Panels" exists, **When** the operator creates a product with name "Panel X", SKU "PNL-001", category "Solar Panels", base price 100, selling price 150, and initial stock 50, **Then** the product is stored and appears in the product list under its category.
2. **Given** a product exists, **When** the operator updates its selling price from 150 to 170, **Then** the new price is persisted and used in future sales (past sale records retain the original price).
3. **Given** a product has been referenced in at least one sale, **When** the operator attempts to delete it, **Then** the product is deactivated (hidden from POS search) but its historical data remains intact.
4. **Given** multiple products exist, **When** the operator searches by partial name or SKU on the POS screen, **Then** matching products are returned with their current stock levels.
5. **Given** the operator creates a new category "Inverters", **When** they view the category list, **Then** "Inverters" appears and products can be assigned to it.

---

### User Story 3 — Reverse a Sale (Priority: P3)

When a mistake is made or a customer returns items, the operator can perform a **full reversal** of a confirmed sale. The reversal creates a separate correction record that negates the entire sale's financial impact and restores stock for all items. The original sale record remains untouched for audit purposes. Partial reversals are not supported; if a customer returns only some items, the operator reverses the full sale and creates a new sale for the items the customer kept.

**Why this priority**: Corrections are essential for financial accuracy but happen less frequently than normal sales. The system must support them to comply with the immutable-records principle, but they are not needed for day-one operation.

**Independent Test**: Can be fully tested by completing a sale, reversing it, and verifying that stock is restored, the original sale is unchanged, and a linked reversal record exists.

**Acceptance Scenarios**:

1. **Given** a confirmed sale exists for 3 units of "Panel A", **When** the operator reverses the sale with reason "Customer return", **Then** a reversal record is created, stock for "Panel A" increases by 3, and the original sale record is unchanged.
2. **Given** a sale has been reversed, **When** the operator views the original sale, **Then** it shows a link to the reversal record and its status indicates it has been reversed.
3. **Given** a sale has already been reversed, **When** the operator attempts to reverse it again, **Then** the system rejects the action with a clear error.

---

### User Story 4 — Track Inventory Changes (Priority: P4)

Every change to product stock — whether from a sale, a reversal, a manual restock, or an adjustment — is logged with the quantity change, reason, and resulting balance. The operator can view the full stock movement history for any product and manually add stock via restock or adjustment entries.

**Why this priority**: Inventory logging is critical for accountability and debugging stock discrepancies, but it operates behind the scenes of the core POS flow. It enhances trust in the system.

**Independent Test**: Can be fully tested by performing various stock-changing actions (sale, reversal, restock, manual adjustment) and verifying each one creates a corresponding log entry with correct data.

**Acceptance Scenarios**:

1. **Given** a product has 20 units in stock, **When** a sale of 3 units is confirmed, **Then** the inventory log records: delta = −3, reason = "sale", balance after = 17.
2. **Given** a sale reversal restores 3 units, **Then** the inventory log records: delta = +3, reason = "reversal", balance after = 20.
3. **Given** the operator restocks "Panel A" by 50 units, **Then** the inventory log records: delta = +50, reason = "restock", balance after = 70.
4. **Given** the operator makes a manual adjustment of −5 with reason "damaged", **Then** the inventory log records: delta = −5, reason = "adjustment", balance after = 65.
5. **Given** the operator views the inventory log for "Panel A", **Then** all entries appear in chronological order showing delta, reason, reference, and running balance.

---

### User Story 5 — Real-Time Stock Updates on POS (Priority: P5)

While the POS screen is open, stock levels update in real time without requiring a page refresh. If stock changes due to a sale, reversal, or restock happening elsewhere, the product search results reflect the updated availability immediately.

**Why this priority**: Real-time updates improve operator confidence and prevent selling out-of-stock items, but the POS functions correctly without them (stock is validated at confirmation time regardless).

**Independent Test**: Can be tested by opening the POS screen, triggering a stock change from a separate action (e.g., restock via inventory management), and verifying the POS product list updates automatically.

**Acceptance Scenarios**:

1. **Given** the POS screen is open showing "Panel A" with stock = 20, **When** a restock of 10 units is performed, **Then** the POS screen updates to show stock = 30 without a page refresh.
2. **Given** the POS screen is open, **When** the connection to the server is temporarily lost, **Then** the system indicates the connection status and automatically reconnects.

---

### Edge Cases

- **Zero-quantity sale attempt**: The system MUST reject a sale with no items.
- **Product with zero stock**: Products at zero stock MUST still appear in search results but MUST be clearly marked as out of stock; adding them to the cart MUST be prevented.
- **Simultaneous stock depletion**: If stock drops to zero between adding an item to the cart and confirming the sale, the confirmation MUST fail with a clear insufficient-stock error.
- **Very large quantities**: The system MUST handle sales of up to 10,000 units of a single product without errors.
- **Negative prices**: The system MUST reject products with negative base price or selling price.
- **Duplicate SKU**: The system MUST reject creating a product with an SKU that already exists.
- **Category deletion with products**: The system MUST prevent deleting a category that still has active products assigned to it.
- **Fee with percentage type**: A percentage-based shipping fee of 5% on a subtotal of 1,000 MUST calculate to exactly 50.00.
- **Rounding edge**: 10% VAT on a subtotal of 33.33 MUST produce 3.33 (ROUND_HALF_UP to 2 decimal places: 3.333 → 3.33).
- **Sale reversal stock overflow**: If reversing a sale would cause stock to exceed a maximum limit (if defined), the system MUST handle this gracefully.
- **Partial return workaround**: When a customer returns only some items, the operator MUST reverse the full sale and create a new sale for the retained items; the system MUST NOT support selecting individual items for reversal.
- **Price override impact**: If an operator overrides a price to be lower than the product's base price (cost), the system MUST allow the sale but SHOULD display a visual warning or indicator to the operator before confirmation.

## Requirements *(mandatory)*

### Functional Requirements

**Product Catalog**

- **FR-001**: System MUST allow creating products with name, optional SKU, category, base price, selling price, and initial stock quantity
- **FR-002**: System MUST enforce SKU uniqueness across all products when a SKU is provided
- **FR-003**: System MUST allow organizing products into named categories
- **FR-004**: System MUST support searching products by name (partial match) and by SKU
- **FR-005**: System MUST soft-delete products that are referenced in existing sales (deactivate, not remove)
- **FR-006**: System MUST prevent deleting a category that has active products assigned to it
- **FR-007**: System MUST reject products where selling price is less than base price or where either price is negative

**Point of Sale**

- **FR-008**: System MUST allow building a sale from one or more products with specified quantities and MUST allow manually overriding the unit price for each item in the cart
- **FR-008a**: System MUST prevent adding a product to the cart if its current available quantity is 0; the UI MUST disable the "Add" button and display an "Out of Stock" indicator.
- **FR-009**: System MUST support adding extra fees to a sale — with types: shipping, installation, and custom
- **FR-010**: System MUST support each fee as either a fixed amount or a percentage of the subtotal
- **FR-011**: System MUST store each fee's type, input value, value type (fixed/percent), and final calculated amount
- **FR-012**: System MUST apply VAT when enabled in settings, calculating it as either a fixed amount or percentage depending on the configuration
- **FR-013**: System MUST store the VAT rate and VAT amount with each sale
- **FR-013a**: System MUST round all monetary calculation results to 2 decimal places using ROUND_HALF_UP (standard commercial rounding)
- **FR-014**: System MUST validate stock availability for all items before confirming a sale
- **FR-015**: System MUST record a sale as immediately confirmed and immutable upon submission
- **FR-016**: System MUST provide a dedicated calculation endpoint (e.g., `/calculate`) that computes the full financial breakdown (subtotal, fees, VAT, total) based on current cart items, quantities, and prices; the frontend MUST use this endpoint to display totals before confirmation.
- **FR-017**: System MUST deduct stock and create inventory log entries atomically as part of sale confirmation
- **FR-018**: System MUST require a payment method selection for every sale
- **FR-019**: System MUST support listing and filtering past sales by date range

**Sale Reversals**

- **FR-020**: System MUST allow reversing a confirmed sale in full (partial reversal is not supported) by creating a separate reversal record
- **FR-021**: System MUST restore stock for all items in the reversed sale (entire sale quantity for each line item)
- **FR-022**: System MUST link the reversal record to the original sale for traceability
- **FR-023**: System MUST prevent reversing a sale that has already been reversed
- **FR-024**: System MUST require a reason when creating a reversal

**Inventory**

- **FR-025**: System MUST log every stock change with quantity delta, reason, and resulting balance
- **FR-026**: System MUST support manual restocking (adding stock to a product)
- **FR-027**: System MUST support manual stock adjustments with a required reason
- **FR-028**: System MUST prevent stock from going below zero on any operation
- **FR-029**: System MUST provide a chronological stock movement history per product

**Real-Time Updates**

- **FR-030**: System MUST push stock level changes to connected POS clients in real time
- **FR-031**: System MUST handle connection loss gracefully and automatically reconnect

**Settings & Configuration**

- **FR-032**: System MUST allow configuring VAT as enabled/disabled, with type (fixed/percent) and value
- **FR-033**: System MUST allow managing payment methods (create, update, delete)

### Key Entities

- **Product**: An item available for sale. Has a name, optional SKU, belongs to a category, has a base price (cost to acquire), a selling price (price charged to customers), and a stock quantity. Cannot be hard-deleted if referenced in sales.
- **Category**: A grouping for products (e.g., "Solar Panels", "Batteries", "Inverters"). A product belongs to exactly one category.
- **Sale**: A completed transaction recording the purchase of one or more products. Contains a financial breakdown (subtotal, fees, VAT, total) and a payment method. Immutable after creation.
- **Sale Item**: A line within a sale, capturing the product, quantity, **the actual unit price charged at time of sale (including any manual override)**, and line total. Preservation of the overridden price is critical for financial audit and profit calculation.
- **Sale Fee**: An additional charge on a sale (shipping, installation, custom). Stores the fee type, input value, value type (fixed or percent), and the final calculated amount.
- **Sale Reversal**: A correction record that negates a previous sale. Links to the original sale, includes a reason, and triggers stock restoration.
- **Inventory Log**: An audit record for every stock change. Tracks the product, quantity delta, reason (sale, reversal, restock, adjustment), an optional reference, and the balance after the change.
- **Payment Method**: A configurable method of payment (e.g., cash, card, bank transfer).
- **Settings**: Global system configuration including VAT toggle, VAT type/value, and default fee templates.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An operator can complete a sale (search product, add to cart, add fees, confirm) in under 30 seconds for a typical 3-item sale
- **SC-002**: All financial totals on a sale are accurate to the cent and match a manual calculation using the same inputs 100% of the time
- **SC-003**: Stock levels never become negative, even under rapid sequential sales
- **SC-004**: Every stock change has a corresponding audit log entry — zero unlogged changes
- **SC-005**: A reversed sale restores stock to exactly the pre-sale quantity
- **SC-006**: Product search returns results within 1 second for a catalog of up to 5,000 products
- **SC-007**: Stock level updates appear on connected POS screens within 2 seconds of the triggering event
- **SC-008**: The operator can view a complete financial breakdown (subtotal, each fee, VAT, total) for any past sale

## Assumptions

- The system is single-user (one operator at a time); no role-based access control is needed
- The operator has a stable local network connection between frontend and backend
- Product catalog size will not exceed 5,000 products in the initial version
- All prices are in a single currency (no multi-currency support)
- The backend and frontend run on the same local network (low latency)
- The frontend MUST NOT compute any financial totals (subtotals, fees, VAT, or grand totals); it must retrieve all calculated values from the backend.
- Phase 0 (Foundation) is complete: the application scaffolding, database, settings engine, categories, and payment methods are already set up
- VAT is applied to the sum of subtotal + fees (not to each line item individually)
- Percentage-based fees are calculated against the subtotal (sum of line item totals), not against the grand total
- All monetary calculations are rounded to 2 decimal places using ROUND_HALF_UP (standard commercial rounding)
