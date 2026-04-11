# Feature Specification: Partner Profit Tracking

**Feature Branch**: `005-partner-profit-tracking`  
**Created**: 2026-04-08  
**Status**: Draft  
**Input**: User description: "we want the partners logic to be like this:
i have an option to set  a product or product count to custom partner, e.g. if i have 10 solar panel and i added 5 panels but set these 5 panels to specified partner. and i added 10 batteries specified to a partener, so i sell if i sell 15 panel and 10 batteries the subtract the partner profit and add it to his wallet and store the profit after substractio to me "

## Clarifications

### Session 2026-04-08

- Q: Can partners directly access and view their own wallet balance and transaction history, or is this restricted to administrators only? → A: No partner portal access - partners must contact administrators for balance information
- Q: When profit calculation fails during a sale, should the entire transaction be blocked (fail), or should the sale proceed with profit calculation marked pending for later resolution? → A: Fail the transaction - sale is blocked until profit calculation succeeds
- Q: Is the partner profit calculated as a percentage of the total sale revenue, or as a percentage of the profit margin after costs? → A: Percentage of revenue - partner gets X% of total sale amount (quantity × unit price × percentage)
- Q: When all quantities assigned to a partner for a specific product are sold, what happens to the product assignment record? → A: Keep assignment record as fulfilled/closed, with zero remaining quantity
- Q: When two sales occur at the same time for products assigned to the same partner, how should the system handle concurrent updates to the partner's wallet balance and assigned inventory? → A: Process sequentially using database transactions with record locking to prevent conflicts

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Assign Products to Partners (Priority: P1)

As a business owner, I want to assign products or specific quantities of products to partners so that partners receive their designated profit share when those products are sold.

**Why this priority**: This is the foundational capability that enables the entire partner profit tracking system. Without the ability to assign products to partners, no profit distribution can occur. This can be tested independently by assigning products to partners and verifying the assignment is recorded.

**Independent Test**: Can be fully tested by creating a partner, assigning products/product quantities to them, and verifying the assignment persists correctly. Delivers the core value of establishing the partner-product relationship.

**Acceptance Scenarios**:

1. **Given** a product inventory with 10 solar panels, **When** I assign 5 panels to a specific partner, **Then** the system records that 5 panels belong to that partner and 5 panels remain unassigned
2. **Given** a new product (e.g., batteries), **When** I assign all quantities to a specific partner, **Then** all units of that product are tracked for that partner
3. **Given** a product already assigned to a partner, **When** I view the product inventory, **Then** I can see which quantities are assigned to which partner

---

### User Story 2 - Calculate and Track Partner Profits (Priority: P2)

As a business owner, when I sell products assigned to partners, I want the system to automatically calculate the partner's profit, add it to their wallet, and record my remaining profit.

**Why this priority**: This enables the core business value of profit sharing. It depends on P1 (product assignments must exist) but delivers the critical financial workflow. Can be tested independently once assignments exist.

**Independent Test**: Can be fully tested by selling products that are assigned to partners and verifying: (1) partner profit is calculated correctly, (2) partner wallet is updated, (3) system profit reflects the subtraction. Delivers the value of automated profit distribution.

**Acceptance Scenarios**:

1. **Given** 5 solar panels assigned to Partner A, **When** I sell 3 of those panels, **Then** Partner A's profit share is calculated, added to their wallet, and the system records the remaining profit
2. **Given** 10 batteries assigned to Partner B, **When** I sell all 10 batteries, **Then** Partner B receives their full profit share and the transaction is recorded
3. **Given** mixed inventory (some products assigned, some not), **When** I make a sale, **Then** only assigned products trigger profit distribution

---

### User Story 3 - Maintain Partner Wallet Balance (Priority: P2)

As a business owner, I want to view each partner's wallet balance and transaction history so that I can manage partner relationships and financial obligations. Partners do not have direct system access and must contact administrators for balance information.

**Why this priority**: Essential for business operations and financial tracking. Administrators need to track amounts owed to partners and respond to partner inquiries. Depends on P1 and P2 but delivers ongoing operational value.

**Independent Test**: Can be tested by administrators viewing partner wallet balances after sales occur, verifying balance updates correctly, and reviewing transaction history. Partners can request balance information from administrators.

**Acceptance Scenarios**:

1. **Given** a partner with prior transactions, **When** I view their wallet, **Then** I see current balance and complete transaction history
2. **Given** a new partner with no sales, **When** I view their wallet, **Then** the balance shows zero with no transactions
3. **Given** multiple sales occurred, **When** I view partner wallet, **Then** each sale shows as separate transaction entries with amounts and dates

---

### User Story 4 - Handle Partial Sales from Assigned Inventory (Priority: P3)

As a business owner, I want to sell partial quantities from partner-assigned inventory and have the profit calculated proportionally.

**Why this priority**: Important for operational flexibility but builds on the core profit calculation flow. Customers may not always buy all available stock. Can be tested once basic profit tracking works.

**Independent Test**: Can be tested by assigning 10 units to a partner, selling 3 units, and verifying the profit for 3 units (not all 10) is distributed correctly. Delivers operational flexibility.

**Acceptance Scenarios**:

1. **Given** 5 solar panels assigned to Partner A, **When** I sell 2 panels, **Then** Partner A receives profit for 2 panels (not all 5), and 3 panels remain in their assigned inventory
2. **Given** mixed sales (assigned and unassigned products), **When** processing the sale, **Then** each assigned product portion is handled independently

---

### Edge Cases

- What happens when a product has no assigned partner? (System keeps full profit)
- What happens when all assigned quantities are sold? (Assignment record is closed/fulfilled with zero remaining quantity, kept for audit trail)
- What happens when selling more units than assigned to a partner? (Only assigned quantity triggers partner profit; excess units are unassigned)
- What happens if a product is assigned to multiple partners in different quantities? (Each partner receives their portion's profit)
- What happens when partner's profit share percentage is changed mid-transaction? (New percentage applies to future sales only)
- What happens when profit calculation fails? (Transaction fails immediately; sale is blocked until calculation issue is resolved)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST allow administrators to assign products to partners with specific quantities (e.g., 5 out of 10 panels)
- **FR-002**: System MUST allow administrators to assign entire product categories to partners (all quantities of a product)
- **FR-003**: System MUST track which quantities of which products are assigned to which partners
- **FR-004**: System MUST define profit share percentages per partner (default percentage can be set at partner level)
- **FR-005**: When a sale occurs, system MUST calculate partner profit based on: (quantity sold × unit price × partner profit share percentage)
- **FR-006**: System MUST add calculated partner profit to partner's wallet balance
- **FR-007**: System MUST record the remaining profit (total sale minus partner profit) as system profit
- **FR-008**: System MUST maintain a transaction log for each partner showing: date, sale reference, quantity, product, profit amount, running balance
- **FR-009**: System MUST prevent sale of quantities not available in inventory (respecting both total inventory and assigned inventory allocations)
- **FR-010**: System MUST allow viewing of product inventory showing assigned vs unassigned quantities
- **FR-011**: System MUST support multiple partners with different profit shares for the same product type (different batches can have different partners)
- **FR-012**: System MUST allow manual wallet adjustments (add/remove amounts with reason tracking)
- **FR-013**: System MUST restrict partner wallet and transaction history access to administrators only; partners must contact administrators for balance information
- **FR-014**: System MUST fail the entire transaction if partner profit calculation cannot be completed; sale is blocked until the calculation issue is resolved
- **FR-015**: When all assigned quantities are sold, the product assignment record MUST be marked as fulfilled/closed with zero remaining quantity and retained for audit trail
- **FR-016**: System MUST use atomic database transactions with appropriate record locking to prevent race conditions when concurrent sales update the same partner's wallet or assigned inventory

### Key Entities *(include if feature involves data)*

- **Partner**: Represents a business partner with attributes including name, contact info, default profit share percentage, and wallet balance
- **Product Assignment**: Links a specific quantity of a product to a partner, tracking how many units are allocated to each partner; includes status (active/fulfilled) and remaining quantity
- **Partner Wallet**: Maintains current balance for each partner, updated automatically on sales or manually by administrators
- **Partner Transaction**: Records each profit distribution event with sale reference, quantity, product, calculated profit, and timestamp
- **Product Inventory**: Existing entity extended to track both total quantity and quantities assigned to partners

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Business owner can assign products to partners in under 30 seconds per product assignment
- **SC-002**: Partner profit is calculated and added to wallet within 2 seconds of sale completion
- **SC-003**: System handles sales of 100+ items across 10+ partners without performance degradation
- **SC-004**: Partner wallet balance accurately reflects sum of all transactions (zero discrepancy on audit)
- **SC-005**: Business owner can view partner profit breakdown for any sale in under 3 seconds
- **SC-006**: System correctly tracks remaining assigned quantities after each sale (no quantity tracking errors)

## Assumptions

- Each product has a defined unit price used to calculate partner's share
- Profit share percentage is defined at the partner level (can override per product assignment if needed)
- Existing inventory management system can be extended to track partner assignments
- Partners receive profit share as a percentage of total sale revenue: quantity sold × unit price × partner share percentage
- Wallet balance represents amount owed to partner, not yet paid out (payout schedule is out of scope for this feature)
- Manual wallet adjustments are single-approver (no multi-step approval required)
- System uses existing authentication and user permission model
- Currency is consistent across all transactions (multi-currency support is out of scope)