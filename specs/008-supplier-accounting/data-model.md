# Data Model: Supplier Accounting System

## Entities

### Supplier

Represents a vendor/supplier from whom inventory is purchased.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Unique identifier |
| name | String | Required, max 255 | Supplier name |
| phone | String | Optional, max 50 | Contact phone |
| notes | Text | Optional | Additional notes |
| created_at | DateTime | Required, default now | Record creation timestamp |

**Relationships:**
- One-to-Many: Supplier → Purchases
- One-to-Many: Supplier → SupplierLedger entries

---

### Purchase

Represents a supplier invoice/purchase order. Immutable after creation.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Unique identifier |
| supplier_id | UUID | Foreign Key → Supplier.id | Link to supplier |
| total_amount | Decimal(12,2) | Required, >= 0 | Total purchase amount |
| created_at | DateTime | Required, default now | Record creation timestamp |

**Relationships:**
- Many-to-One: Purchase → Supplier
- One-to-Many: Purchase → PurchaseItems

**Rules:**
- Immutable: No updates or deletes allowed
- On create: Automatically creates SupplierLedger entry (type=PURCHASE)

---

### PurchaseItem

Individual line item in a purchase with product snapshot.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Unique identifier |
| purchase_id | UUID | Foreign Key → Purchase.id | Link to purchase |
| product_id | UUID | Foreign Key → Product.id | Link to product |
| quantity | Integer | Required, > 0 | Quantity purchased |
| unit_cost | Decimal(12,2) | Required, >= 0 | Cost per unit at time of purchase |
| total_cost | Decimal(12,2) | Required, >= 0 | quantity × unit_cost |

**Relationships:**
- Many-to-One: PurchaseItem → Purchase
- Many-to-One: PurchaseItem → Product

**Rules:**
- total_cost = quantity × unit_cost (computed, stored)
- unit_cost is snapshot - preserved even if product price changes

---

### SupplierLedger

The source of truth for supplier financial tracking. Append-only.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Unique identifier |
| supplier_id | UUID | Foreign Key → Supplier.id | Link to supplier |
| type | Enum | Required: PURCHASE, PAYMENT, RETURN | Transaction type |
| amount | Decimal(12,2) | Required, > 0 | Always positive |
| reference_id | UUID | Optional | Links to Purchase.id for PURCHASE/RETURN |
| note | Text | Optional | Transaction note |
| created_at | DateTime | Required, default now | Record creation timestamp |

**Relationships:**
- Many-to-One: SupplierLedger → Supplier

**Rules:**
- Append-only: No updates or deletes
- PURCHASE: reference_id = purchase.id
- PAYMENT: reference_id = null
- RETURN: reference_id = purchase.id

---

## Derived Calculations

### Supplier Balance

```
balance = total_purchases - total_payments - total_returns

where:
  total_purchases = SUM(SupplierLedger.amount WHERE type = PURCHASE)
  total_payments = SUM(SupplierLedger.amount WHERE type = PAYMENT)
  total_returns = SUM(SupplierLedger.amount WHERE type = RETURN)
```

**Note:** Balance is NEVER stored - always derived from ledger.

---

## State Transitions

### Purchase Lifecycle

```
DRAFT → CREATED (immutable)
```

Once created, Purchase cannot be modified or deleted. Corrections via new transactions.

### SupplierLedger Lifecycle

```
CREATED (append-only)
```

No updates or deletes allowed.

---

## Inventory Integration

| Action | Inventory Effect | inventory_log Entry |
|--------|-----------------|---------------------|
| Purchase created | +quantity per item | REASON="PURCHASE", delta=+quantity |
| Return processed | -quantity per item | REASON="RETURN", delta=-quantity |
| Payment recorded | No effect | N/A |

All inventory changes MUST go through inventory_log per Constitution.

---

## Constraints Summary

1. All monetary fields use Decimal (not Float)
2. Stock never goes below zero
3. Cannot return more than purchased
4. Ledger entries are immutable
5. Balance derived (not stored)
6. All stock changes logged to inventory_log
