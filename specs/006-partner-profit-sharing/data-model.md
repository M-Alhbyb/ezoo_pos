# Data Model: Real-time Partner Profit from Product Sales

## Entities

### ProductAssignment

Links a product to a partner for profit sharing.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| product_id | UUID | NOT NULL, FK → products.id | Reference to product |
| partner_id | UUID | NOT NULL, FK → partners.id | Reference to partner |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Assignment timestamp |
| updated_at | TIMESTAMP | NULL | Last modification |
| is_active | BOOLEAN | NOT NULL, DEFAULT TRUE | Whether assignment is active |

**Relationships**: 
- product_id → Product (many-to-one)
- partner_id → Partner (many-to-one)

**Constraints**:
- UNIQUE(product_id) - one partner per product
- is_active determines if new sales credit profit

### PartnerWalletTransaction

Records each profit credit to a partner's wallet.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| partner_id | UUID | NOT NULL, FK → partners.id | Reference to partner |
| product_id | UUID | NOT NULL, FK → products.id | Product sold |
| sale_id | UUID | NOT NULL, FK → sales.id | Sale that triggered profit |
| selling_price | DECIMAL(12,2) | NOT NULL | Sale price at time of transaction |
| base_cost | DECIMAL(12,2) | NOT NULL | Product base cost |
| profit_amount | DECIMAL(12,2) | NOT NULL | Calculated profit (selling_price - base_cost), minimum 0 |
| transaction_type | VARCHAR(20) | NOT NULL | PROFIT or REVERSAL |
| parent_transaction_id | UUID | NULL, FK → id | Reversal source if REVERSAL |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Transaction timestamp |

**Relationships**:
- partner_id → Partner (many-to-one)
- sale_id → Sale (many-to-one)

**Constraints**:
- profit_amount >= 0 (never negative per spec clarification)
- transaction_type in (PROFIT, REVERSAL)
- parent_transaction_id required for REVERSAL type

### Product (Extension)

Add to existing product model:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| base_cost | DECIMAL(12,2) | NOT NULL, DEFAULT 0 | Cost basis for profit calculation |

## State Transitions

### ProductAssignment States

- **Active**: is_active = TRUE → sales credit profit to partner
- **Inactive**: is_active = FALSE → no new profit credits, historical preserved

### PartnerWalletTransaction States

- **Created**: Initial PROFIT transaction
- **Reversed**: Created via REVERSAL with parent_transaction_id reference

## Validation Rules

From functional requirements:
- FR-003: One active assignment per product - enforced by unique index on product_id where is_active = TRUE
- FR-004: Prevent multi-partner - same as above
- FR-007: Record all fields per transaction - all fields NOT NULL