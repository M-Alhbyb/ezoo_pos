# Data Model: Partner Profit Tracking

**Feature**: 005-partner-profit-tracking
**Date**: 2026-04-08

## Overview

This document defines the database schema for partner profit tracking, following constitution principles (I, II, IV, VI) and research recommendations.

## Entity Relationship Diagram

```
┌─────────────┐
│   Partner   │
│  (existing) │
└──────┬──────┘
       │
       │ 1:N
       │
       ├──────────────────────┐
       │                      │
       ▼                      ▼
┌──────────────────┐  ┌────────────────────────┐
│ ProductAssignment│  │ PartnerWalletTransaction│
│    (NEW)        │  │         (NEW)           │
└─────┬────────────┘  └────────────────────────┘
      │
      │ N:1
      │
      ▼
┌──────────────┐
│   Product    │
│  (existing)  │
└──────────────┘
```

## New Entities

### 1. ProductAssignment

Assigns specific product quantities to partners forprofit sharing.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, gen_random_uuid() | Primary key |
| `partner_id` | UUID | FK → partners.id, NOT NULL, INDEX | Partner receiving profit share |
| `product_id` | UUID | FK → products.id, NOT NULL, INDEX | Product assigned to partner |
| `assigned_quantity` | INTEGER | NOT NULL, CHECK >=0 | Original quantity assigned |
| `remaining_quantity` | INTEGER | NOT NULL, CHECK >=0 | Quantity remaining unsold |
| `share_percentage` | DECIMAL(5,2) | NOT NULL, CHECK >=0 AND <=100 | Profit share (overrides partner default) |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'active' | 'active' or 'fulfilled' |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation timestamp |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Last update timestamp |
| `fulfilled_at` | TIMESTAMPTZ | NULLABLE | When remaining_quantity hit 0 |
| `created_by` | UUID | FK → users.id (future) | Extensibility: multi-user support |
| `branch_id` | UUID | FK → branches.id (future) | Extensibility: multi-branch support |

**Indexes**:
- `idx_product_assignment_active`: (product_id, status, remaining_quantity) - Fast lookup during sale processing
- `idx_partner_assignments`: (partner_id) - List assignments per partner

**Foreign Keys**:
- `partner_id` → `partners.id` ON DELETE RESTRICT
- `product_id` → `products.id` ON DELETE RESTRICT

**Business Rules**:
- Only one active assignment per product (enforced by application layer or unique partial index)
- `remaining_quantity` decreases on each sale of assigned product
- When `remaining_quantity` reaches 0, `status` → 'fulfilled', `fulfilled_at` set
- `share_percentage` defaults to partner's share_percentage if not specified
- Cannot delete partner or product with existing assignments

**State Transitions**:
```
[NEW] → assigned_quantity set, remaining_quantity = assigned_quantity
     → status = 'active'

[SALE] → remaining_quantity -= quantity_sold
      → if remaining_quantity == 0:
           status = 'fulfilled'
           fulfilled_at = now()
      → update updated_at

[FULFILLED] → No further changes
```

---

### 2. PartnerWalletTransaction

Immutable record of all wallet balance changes for audit trail.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, gen_random_uuid() | Primary key |
| `partner_id` | UUID | FK → partners.id, NOT NULL, INDEX | Partner whose wallet changed |
| `amount` | DECIMAL(12,2) | NOT NULL, CHECK != 0 | Credit (positive) or debit (negative) |
| `transaction_type` | VARCHAR(50) | NOT NULL | 'sale_profit', 'manual_adjustment' |
| `reference_id` | UUID | NULLABLE | FK to sale_id or NULL for manual |
| `reference_type` | VARCHAR(50) | NULLABLE | 'sale', 'manual' |
| `description` | TEXT | NULLABLE | Human-readable description |
| `balance_after` | DECIMAL(12,2) | NOT NULL | Wallet balance after this transaction |
| `created_at` | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Transaction timestamp |
| `created_by` | UUID | FK → users.id (future) | Extensibility: multi-user support |

**Indexes**:
- `idx_partner_transactions`: (partner_id, created_at DESC) - Balance history lookup

**Foreign Keys**:
- `partner_id` → `partners.id` ON DELETE RESTRICT
- `created_by` → `users.id` (future, nullable)

**Business Rules**:
- **IMMUTABLE**: No updates or deletes after creation (Constitution IV)
- `balance_after` computed as previous balance + amount
- First transaction for partner: balance_after = amount
- `amount` cannot be 0 (CHECK constraint)
- `reference_type` required when `reference_id` is set

**Transaction Types**:
| Type | Amount Sign | Reference | Description Format |
|------|-------------|-----------|-------------------|
| `sale_profit` | Positive | sale_id | "Sale profit: {qty} × {price} × {share}% from {product_name}" |
| `manual_adjustment` | +/- | NULL | Admin-provided description |

---

## Existing Entity Extensions

### Partner (existing)

**New Relationships**:
```python
# Add to Partner model
assignments = relationship("ProductAssignment", backref="partner")
wallet_transactions = relationship("PartnerWalletTransaction", backref="partner")
```

**Computed Property** (NOT stored in database):
```python
@property
async def current_balance(self, db: AsyncSession) -> Decimal:
    """
    Compute wallet balance from latest transaction.
    O(1) lookup using balance_after on latest transaction.
    """
    result = await db.execute(
        select(PartnerWalletTransaction)
        .where(PartnerWalletTransaction.partner_id == self.id)
        .order_by(PartnerWalletTransaction.created_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    return latest.balance_after if latest else Decimal("0.00")
```

---

## Data Flow

### Sale Creation Flow

```
1. Customer initiates sale
   ↓
2. SaleService.create_sale() begins transaction
   ↓
3. InventoryService deducts stock (existing)
   ↓
4. PartnerProfitService.process_sale_partner_profits() NEW
   │
   ├→ For each sale_item:
   │   ├→ Query ProductAssignment WHERE product_id = item.product_id AND status = 'active'
   │   ├→ If assignment found:
   │   │   ├→ Lock assignment row (FOR UPDATE)
   │   │   ├→ Validate remaining_quantity >= item.quantity
   │   │   ├→ Calculate profit: item.quantity × item.unit_price × assignment.share_percentage
   │   │   ├→ Deduct from remaining_quantity
   │   │   ├→ If remaining_quantity == 0: status = 'fulfilled'
   │   │   └→ Create PartnerWalletTransaction with balance_after
   │   └→ Else: No partner assignment (system keeps full profit)
   │
   └→ Commit transaction (atomic)
```

### Manual Wallet Adjustment Flow

```
1. Admin adjusts partner wallet (add/remove amount)
   ↓
2. PartnerService.adjust_wallet() begins transaction
   ↓
3. Lock partner row (FOR UPDATE)
   ↓
4. Query latest PartnerWalletTransaction for partner
   ↓
5. Compute new_balance = latest.balance_after + adjustment_amount
   ↓
6. Create PartnerWalletTransaction:
   - amount = adjustment_amount
   - transaction_type = 'manual_adjustment'
   - balance_after = new_balance
   - description = admin_reason
   ↓
7. Commit transaction
```

---

## Migration Strategy

### Alembic Migration

**File**: `alembic/versions/xxxx_add_partner_profit_tracking.py`

```python
def upgrade():
    # 1. Create product_assignments table
    op.create_table(
        'product_assignments',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partners.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('products.id', ondelete='RESTRICT'),nullable=False),
        sa.Column('assigned_quantity', sa.Integer, nullable=False),
        sa.Column('remaining_quantity', sa.Integer, nullable=False, server_default='0'),
        sa.Column('share_percentage', sa.Numeric(5, 2), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('fulfilled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('branch_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('branches.id'), nullable=True),
        sa.CheckConstraint('remaining_quantity >= 0', name='check_remaining_nonnegative'),
        sa.CheckConstraint('share_percentage >= 0 AND share_percentage <= 100', name='check_share_percentage_range'),
    )
    
    # Indexes
    op.create_index('idx_product_assignment_active', 'product_assignments', ['product_id', 'status', 'remaining_quantity'])
    op.create_index('idx_partner_assignments', 'product_assignments', ['partner_id'])
    
    # 2. Create partner_wallet_transactions table
    op.create_table(
        'partner_wallet_transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('partner_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('partners.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('amount', sa.Numeric(12, 2), nullable=False),
        sa.Column('transaction_type', sa.String(50), nullable=False),
        sa.Column('reference_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reference_type', sa.String(50), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('balance_after', sa.Numeric(12, 2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.CheckConstraint('amount != 0', name='check_amount_nonzero'),
    )
    
    # Indexes
    op.create_index('idx_partner_transactions', 'partner_wallet_transactions', ['partner_id', sa.text('created_at DESC')])

def downgrade():
    op.drop_index('idx_partner_transactions', 'partner_wallet_transactions')
    op.drop_table('partner_wallet_transactions')
    op.drop_index('idx_partner_assignments', 'product_assignments')
    op.drop_index('idx_product_assignment_active', 'product_assignments')
    op.drop_table('product_assignments')
```

---

## Performance Considerations

### Query Patterns

| Query | Index Used | Performance |
|-------|-----------|-------------|
| Find active assignment for product during sale | `idx_product_assignment_active` | O(1) index scan |
| List all assignments for partner | `idx_partner_assignments` | O(n) where n = assignments per partner |
| Get partner wallet balance | `idx_partner_transactions` | O(1) single row fetch |
| Transaction history for partner | `idx_partner_transactions` | O(k) where k = transactions per partner |

### Concurrency Safety

- `SELECT FOR UPDATE` on both ProductAssignment and Partner rows during sale processing (Research §3)
- Sorted lock ordering prevents deadlocks when multiple partners involved
- Atomic transaction ensures all-or-nothing semantics

---

## Constitution Compliance

| Principle | Implementation |
|-----------|----------------|
| **I. Financial Accuracy** | All calculations use persisted values (quantity, unit_price, share_percentage) |
| **II. Single Source of Truth** | No derived columns; balance computed from transactions |
| **III. Explicit Over Implicit** | share_percentage stored per assignment; description stored per transaction |
| **IV. Immutable Financial Records** | PartnerWalletTransaction has no UPDATE endpoints |
| **VI. Data Integrity** | DECIMAL for all monetary columns; CHECK constraints on quantities |
| **IX. Extensibility** | created_by, branch_id columns ready for multi-user/branch |

---

## Rollback Strategy

If rollback needed after deployment:
1. Verify no active assignments exist (status = 'active')
2. Verify wallet transactions are historical reference only
3. Drop tables in reverse order: partner_wallet_transactions → product_assignments
4. No data loss risk for existing entities (Partner, Product unchanged)