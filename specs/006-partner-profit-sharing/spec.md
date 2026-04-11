# Feature Specification: Real-time Partner Profit from Product Sales

**Feature Branch**: `006-partner-profit-sharing`  
**Created**: 2026-04-11  
**Status**: Draft  
**Input**: User description: "The current partner system is based on project profit distribution. This must be redesigned to support real-time profit sharing from product sales. Partners earn profit automatically from product sales. Profit is calculated from net profit only (selling price - base cost). Each product can be linked to: only one partner OR no partner, never multiple partners. Production-grade partner profit system integrated with POS sales."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Partner Profit From Product Sale (Priority: P1)

A partner linked to a product earns profit automatically when that product is sold through the POS system.

**Why this priority**: This is the core business requirement - the fundamental reason for redesigning the partner system. Without this, the feature has no value.

**Independent Test**: A product linked to a partner is sold via POS; partner's profit is calculated and recorded. Profit = selling price minus base cost.

**Acceptance Scenarios**:

1. **Given** a product linked to Partner A with base cost set, **When** the product is sold via POS at selling price X, **Then** Partner A earns profit equal to (X - base cost)
2. **Given** a product with no linked partner, **When** the product is sold via POS, **Then** no partner earns profit from that sale
3. **Given** a product linked to Partner A, **When** a different product (not linked to Partner A) is sold, **Then** Partner A earns no profit from that sale

---

### User Story 2 - Assign Product to Partner (Priority: P2)

A product can be assigned to exactly one partner, enabling that partner to earn profit from each sale of that product.

**Why this priority**: This is the operational mechanism that connects products to partners for profit sharing. Required to operationalize User Story 1.

**Independent Test**: A product is assigned to a partner via product management; subsequent sales of that product credit profit to the assigned partner.

**Acceptance Scenarios**:

1. **Given** a product with no assigned partner, **When** admin assigns the product to Partner A, **Then** the product is now linked to Partner A
2. **Given** a product linked to Partner A, **When** admin attempts to link the product to Partner B as well, **Then** the system prevents this and keeps the product linked to Partner A only (one partner per product)
3. **Given** a product linked to Partner A, **When** admin changes the link to Partner B, **Then** the product is now linked to Partner B only (Partner A no longer receives profit)

---

### User Story 3 - Partner Profit Dashboard (Priority: P3)

Partners can view their accumulated profit earnings from product sales.

**Why this priority**: Partners need visibility into their earnings to verify correct profit distribution and trust the system.

**Independent Test**: Partner logs in and views profit summary showing total earnings from linked product sales.

**Acceptance Scenarios**:

1. **Given** Partner A has linked products that have generated sales, **When** Partner A views their profit dashboard, **Then** Partner A sees total profit earned
2. **Given** Partner A has no linked products or no sales, **When** Partner A views their profit dashboard, **Then** Partner A sees zero profit

---

### Edge Cases

- **Negative profit**: When base cost exceeds selling price, profit is credited as zero (never negative)
- **Refunds**: When a product is refunded, the partner's profit is reversed
- **Partner deactivation**: Existing product links continue generating profit; only new sales require active partner
- **Discounted sales**: Profit calculated based on actual sale price (after discount)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST calculate partner profit as selling price minus base cost for each sold product linked to a partner
- **FR-002**: System MUST credit profit to the linked partner immediately upon POS sale completion
- **FR-003**: System MUST allow assigning a product to exactly one partner at a time
- **FR-004**: System MUST prevent assigning a product to multiple partners simultaneously
- **FR-005**: System MUST allow unlinking a product from a partner (making it have no partner)
- **FR-006**: System MUST display partner profit earnings in a dashboard accessible to the partner
- **FR-007**: System MUST record each profit transaction with product, sale, amount, and timestamp
- **FR-008**: System MUST support querying profit history by date range for partner reporting

### Key Entities

- **Partner**: An entity that earns profit from product sales. Can be linked to multiple products (one-way relationship).
- **Product**: An item sold through POS. Can be linked to exactly one partner or no partner.
- **Profit Transaction**: A record of profit earned from a single sale, including the partner, product, sale amount, base cost, profit calculated, and timestamp.
- **Base Cost**: The cost basis for a product used in profit calculation (selling price - base cost = profit)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Partners linked to products receive profit credit within 10 seconds of sale completion
- **SC-002**: Each sale of a linked product correctly calculates profit as selling price minus base cost
- **SC-003**: 100% of product-to-partner assignments result in exactly one partner (no multi-partner assignments possible)
- **SC-004**: Partners can view their profit earnings with a dashboard load time of under 3 seconds

## Clarifications

### Session 2026-04-11

- Q: In negative profit scenario (base cost > selling price), how should profit be handled? → A: Track as zero - never credit negative profit; credit zero if calculated profit is negative
- Q: When a product is returned or refunded, should the partner's profit be reversed? → A: Reverse profit - reverse the profit when refund is issued
- Q: When a partner account is deactivated, should product links stop generating profit? → A: Keep earning - existing links continue earning; only new sales stopped
- Q: For discounted or promotional sales, how should profit be calculated? → A: Actual price - based on actual sale price (after discount)

## Assumptions

- The existing POS sale flow will trigger profit calculation as part of the transaction completion process
- Base cost for products will be stored as a product attribute, defaulting to zero if not set
- Partner authentication and access controls already exist and can be reused
- The system supports one partner per product; multi-partner profit splitting is out of scope for this redesign