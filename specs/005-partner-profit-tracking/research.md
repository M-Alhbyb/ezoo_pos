# Research: Partner Profit Tracking

**Date**: 2026-04-08
**Feature**: 005-partner-profit-tracking

## Overview

This document resolves technical unknowns for implementing partner profit tracking in EZOO POS, following established patterns from existing features (sales, inventory, partner distributions).

---

## 1. Integration Pattern with Sales

### Recommended Approach
**Within sale service with async-style logic after stock deduction but before commit**

### Rationale
- **Atomic guarantee**: Partner profit calculation runs within the same database transaction as the sale, ensuring all-or-nothing semantics (Constitution VI)
- **Failure handling**: If partner profit calculation fails, the entire sale is rolled back per spec FR-014 ("sale is blocked until calculation issue is resolved")
- **Existing pattern**: Current `SaleService.create_sale()` already follows this pattern with stock deduction via `InventoryService` within the same transaction
- **Clean separation**: Profit calculation service can be injected into `SaleService` similar to how `InventoryService` is injected

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| Post-sale webhook/hook | Decoupled, fire-and-forget | Race conditions with reversals; violates atomicity requirement | Rejected |
| Separate service after commit | Clean separation | Cannot guarantee all-or-nothing; reversal handling complexity | Rejected |
| Event queue (async) | Scalable | Over-engineering for single-user POS; eventual consistency issues | Rejected |

### Implementation Notes

```python
# In SaleService.create_sale()
async def create_sale(self, sale_data: SaleCreate) -> Sale:
    async with self.db.begin():
        # 1. Idempotency check (existing)
        # 2. Lock products (existing)
        # 3. Validate stock (existing)
        # 4. Calculate breakdown (existing)
        # 5. Create sale record (existing)
        # 6. Create sale items (existing)
        # 7. Deduct stock via InventoryService (existing)
        
        # 8. NEW: Calculate and distribute partner profits
        await self.partner_profit_service.process_sale_partner_profits(
            sale=sale,
            sale_items=sale_data.items
        )
        
        # 9. Commit (existing)
```

**Constraints**:
- Must happen after stock deduction to ensure inventory is consumed
- Must happen before commit to maintain atomicity
- Query product assignments BEFORE processing to detect which items have partner assignments
- Lock partner records with `SELECT FOR UPDATE` during profit calculation

---

## 2. Wallet Balance Strategy

### Recommended Approach
**Hybrid: Computed from transaction sum with checkpoint snapshots**

### Rationale
- **Constitution compliance**: No derived columns in Partner table (follows existing PartnerDistribution pattern)
- **Audit trail**: Every transaction is immutable and reconstructable
- **Performance**: Checkpoint snapshots allow historical queries without summing millions of transactions
- **Existing pattern**: `PartnerDistribution` already uses snapshot pattern for recording state at time of distribution

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Materialized balance column** | O(1) read performance | Race conditions on concurrent updates; drift risk; violates Constitution VI (no denormalized financial state) | Rejected |
| **Pure computed (sum all transactions)** | Zero drift, fully auditable | Performance degradation over time (O(n) balance calculation) | Rejected for production scale |
| **Hybrid with checkpoints** | Balance from latest checkpoint + recent transactions; bounded query time | Slightly more complex migration | **Selected** |

### Implementation Notes

**Schema Design**:
```python
class PartnerWalletTransaction(Base):
    __tablename__ = "partner_wallet_transactions"
    
    id = Column(UUID, primary_key=True)
    partner_id = Column(UUID, ForeignKey("partners.id"), nullable=False, index=True)
    amount = Column(DECIMAL(12, 2), nullable=False)  # Positive = credit, Negative = debit
    transaction_type = Column(String(50), nullable=False)  # 'sale_profit', 'manual_adjustment', 'payout'
    reference_id = Column(UUID, nullable=True)  # sale_id or payout_id
    reference_type = Column(String(50), nullable=True)  # 'sale', 'manual', 'payout'
    description = Column(Text, nullable=True)
    balance_after = Column(DECIMAL(12, 2), nullable=False)  # Snapshot for audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**Balance Calculation**:
```python
async def get_partner_balance(partner_id: UUID) -> Decimal:
    # Fast path: Latest transaction has balance_after
    result = await db.execute(
        select(PartnerWalletTransaction)
        .where(PartnerWalletTransaction.partner_id == partner_id)
        .order_by(PartnerWalletTransaction.created_at.desc())
        .limit(1)
    )
    latest = result.scalar_one_or_none()
    return latest.balance_after if latest else Decimal("0")
```

**No checkpoint table needed** — `balance_after` on each transaction provides O(1) balance lookup while maintaining full audit trail.

---

## 3. Concurrent Transaction Safety

### Recommended Approach
**SELECT FOR UPDATE on partner records during sale processing, sorted lock ordering**

### Rationale
- **Existing pattern**: `InventoryService._get_product_for_update()` already uses `SELECT FOR UPDATE` 
- **Prevents race conditions**: Multiple simultaneous sales for same partner won't corrupt wallet balance
- **Sorted lock ordering**: Prevents deadlocks when same partner appears in multiple concurrent sales

### Implementation Pattern

```python
class PartnerProfitService:
    async def process_sale_partner_profits(self, sale, sale_items):
        # 1. Collect unique partner IDs from product assignments
        partner_ids = await self._get_assigned_partner_ids(sale_items)
        
        if not partner_ids:
            return  # No partner products in sale
        
        # 2. Sort partner IDs for consistent lock ordering (prevents deadlocks)
        partner_ids = sorted(partner_ids)
        
        # 3. Lock all partner records atomically
        locked_partners = {}
        for pid in partner_ids:
            partner = await self._get_partner_for_update(pid)
            if not partner:
                raise ValueError(f"Partner {pid} not found")
            locked_partners[pid] = partner
        
        # 4. Now process assignments with locks held
        for item in sale_items:
            assignment = await self._get_product_assignment_for_update(
                item.product_id
            )
            if assignment and assignment.remaining_quantity >= item.quantity:
                await self._credit_partner_wallet(
                    partner=locked_partners[assignment.partner_id],
                    sale=sale,
                    assignment=assignment,
                    quantity=item.quantity
                )
    
    async def _get_partner_for_update(self, partner_id: UUID):
        """Lock partner row for update."""
        query = (
            select(Partner)
            .where(Partner.id == partner_id)
            .with_for_update()
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def _get_product_assignment_for_update(self, product_id: UUID):
        """Lock assignment row for update."""
        query = (
            select(ProductAssignment)
            .where(
                ProductAssignment.product_id == product_id,
                ProductAssignment.status == 'active'
            )
            .with_for_update()
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
```

### Deadlock Prevention

| Scenario | Risk | Mitigation |
|----------|------|------------|
| Sale A: Partner X → Sale B: Partner X | Wallet balance corruption | `FOR UPDATE` serializes access |
| Sale A: Partners [X, Y] → Sale B: Partners [Y, X] | Deadlock | Sorted lock ordering |
| Assignment exhausts mid-sale | Inconsistent inventory | Lock assignment row too, check remaining_quantity |

**Constraints**:
- Must use `with_for_update()` for both partner and assignment rows
- Lock order: always sort UUIDs before acquiring locks
- Transaction must include both assignment deduction AND wallet credit atomically

---

## 4. Product Assignment Lifecycle

### Recommended Approach
**Assignment has `remaining_quantity` column with query-based status; auto-close on depletion**

### Rationale
- **Explicit state**: `remaining_quantity` tracks available units without complex queries
- **Audit trail**: Assignment record preserved with status = 'fulfilled' when depleted
- **Performance**: Query by `status = 'active' AND remaining_quantity > 0` for quick lookup
- **Atomicity**: Update `remaining_quantity` and credit wallet in same transaction

### Alternatives Considered

| Alternative | Pros | Cons | Verdict |
|-------------|------|------|---------|
| **Column-based (remaining_quantity)** | O(1) update, explicit state | Requires status maintenance | **Selected** |
| **Pure query-based** | No state drift | O(n) to calculate remaining; complex for concurrent updates | Rejected |
| **Trigger-based** | Database-managed | Harder to debug; violates service-layer logic preference | Rejected |

### Implementation Notes

**Schema**:
```python
class ProductAssignment(Base):
    __tablename__ = "product_assignments"
    
    id = Column(UUID, primary_key=True)
    partner_id = Column(UUID, ForeignKey("partners.id"), nullable=False, index=True)
    product_id = Column(UUID, ForeignKey("products.id"), nullable=False, index=True)
    assigned_quantity = Column(Integer, nullable=False)  # Original quantity
    remaining_quantity = Column(Integer, nullable=False)  # Updated on sale
    share_percentage = Column(DECIMAL(5, 2), nullable=True)  # Override partner default
    status = Column(String(20), nullable=False, default='active')  # 'active' | 'fulfilled'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    fulfilled_at = Column(DateTime(timezone=True), nullable=True)
    
    __table_args__ = (
        CheckConstraint("remaining_quantity >= 0", name="check_remaining_nonnegative"),
        Index('idx_assignment_active', 'product_id', 'status'),  # Fast lookup for active
    )
```

**Status Update Logic**:
```python
async def _credit_partner_wallet(self, partner, sale, assignment, quantity):
    # Deduct from remaining_quantity
    assignment.remaining_quantity -= quantity
    
    # Auto-close if depleted
    if assignment.remaining_quantity == 0:
        assignment.status = 'fulfilled'
        assignment.fulfilled_at = datetime.utcnow()
    
    # Calculate profit
    # On sale: (quantity × unit_price × share_percentage) goes to partner
    
    # Create wallet transaction
    transaction = PartnerWalletTransaction(
        partner_id=partner.id,
        amount=profit_amount,
        transaction_type='sale_profit',
        reference_id=sale.id,
        reference_type='sale',
        description=f"Sale profit: {quantity} × {sale_item.unit_price} × {share_percentage}%",
        balance_after=... # computed
    )
    self.db.add(transaction)
```

**Edge Case Handling** (per spec):
- Selling more than assigned → Only assigned quantity triggers profit (remaining goes to system)
- Assignment not found → Product is unassigned, full profit to system
- Multiple partners for same product → First active assignment wins (or `active` status ensures single active assignment per product)

---

## 5. Foreign Key Patterns for ProductAssignment

### Recommended Approach
**Standard FKs with `ON DELETE RESTRICT` (prevent deletion), indexed for sale processing**

### Rationale
- **Data integrity**: Cannot delete product or partner if assignments exist
- **Constitution IV compliance**: Immutable financial records = can't delete referenced entities
- **Performance**: Composite index on `(product_id, status)` for fast lookup during sale processing
- **Existing pattern**: Follows `SaleItem` FK pattern to products

### Implementation Notes

**Foreign Key Definitions**:
```python
partner_id = Column(
    UUID(as_uuid=True),
    ForeignKey("partners.id", ondelete="RESTRICT"),  # Prevent partner deletion
    nullable=False,
    index=True
)

product_id = Column(
    UUID(as_uuid=True),
    ForeignKey("products.id", ondelete="RESTRICT"),  # Prevent product deletion
    nullable=False,
    index=True
)

# Composite index for active assignment lookup during sale
Index('idx_product_assignment_active', 'product_id', 'status', 'remaining_quantity')
```

**Index Strategy**:

| Query Pattern | Index | Purpose |
|--------------|-------|---------|
| Find active assignment for product during sale | `idx_product_assignment_active` | covering query for `product_id + status = 'active'` |
| List all assignments for partner (admin UI) | `partner_id` index | Standard FK lookup |
| Historial transactions for partner | `partner_id` on `wallet_transactions` | Balance calculation, history |

**Cascade Behavior**:
- `RESTRICT`: Prevent deletion of partner/product if assignments exist
- Error message should guide admin: "Cannot delete product: 5 units assigned to Partner X. Remove assignments first."
- Soft delete not needed — assignments are financial records (Constitution IV)

---

## Summary Table

| Task | Recommendation | Key Pattern |
|------|----------------|--------------|
| Sales Integration | Within transaction, after stock deduction | Atomic with `FOR UPDATE` locks |
| Wallet Balance | Hybrid: `balance_after` on each transaction | O(1) lookup, full audit trail |
| Concurrency | `SELECT FOR UPDATE` with sorted lock ordering | Follows `InventoryService` pattern |
| Assignment Lifecycle | `remaining_quantity` with auto-close | Status = 'fulfilled' on depletion |
| Foreign Keys | `RESTRICT` on delete, composite indexes | Prevent orphaned financial records |

---

## References

- Constitution principles: I (Financial Accuracy), IV (Immutable Records), VI (Data Integrity)
- Existing patterns: `InventoryService._get_product_for_update()`, `SaleService.create_sale()`
- Spec FR-014: "System MUST fail entire transaction if partner profit calculation cannot be completed"
- Spec FR-016: "System MUST use atomic database transactions with appropriate record locking"