# Data Model: Core POS, Products, and Inventory Management

**Feature**: 001-core-pos-products-inventory
**Date**: 2026-04-04

## Overview

This document defines the database schema for Phase 1 features: product catalog, point-of-sale, sale reversals, and inventory tracking. All tables build upon the Phase 0 foundation (settings, categories, payment_methods).

## Entity Relationship Diagram

```
┌─────────────┐         ┌──────────────┐
│  categories │         │products      │
│             │         │              │
│ id (PK)     │───1:N───│ category_id  │
│ name        │         │ id (PK)      │
│ created_at  │         │ name         │
│ updated_at  │         │ sku (UNIQUE) │
│ user_id     │         │ base_price   │
│ branch_id   │         │ selling_price│
└─────────────┘         │ stock_quantity│
                        │ is_active     │
                        │ created_at    │
                        │ updated_at    │
                        │ user_id       │
                        │ branch_id     │
                        └──────┬────────┘
                               │
                               │
                        ┌──────┴────────┐
                        │inventory_log  │
                        │               │
                        │ id (PK)       │
                        │ product_id(FK)│
                        │ delta         │
                        │ reason        │
                        │ reference_id  │
                        │ balance_after │
                        │ created_at    │
                        │ user_id       │
                        │ branch_id     │
                        └───────────────┘

┌────────────────┐
│payment_methods │
│                │
│ id (PK)        │
│ name           │
│ is_active      │
│ created_at     │
│ updated_at     │
│ user_id        │
│ branch_id      │
└───────┬────────┘
        │
        │1:N
        │
┌───────┴────────┐         ┌──────────────┐
│ sales          │         │ sale_items   │
│                │         │              │
│ id (PK)        │───1:N───│ sale_id (FK) │
│ payment_method │         │ product_id   │
│ subtotal       │         │ product_name │
│ fees_total     │         │ quantity     │
│ vat_rate       │         │ unit_price   │
│ vat_amount     │         │ line_total   │
│ total          │         │ created_at   │
│ note           │         │ user_id      │
│ created_at     │         │ branch_id    │
│ updated_at     │         └──────────────┘
│ user_id        │
│ branch_id      │         ┌──────────────┐
└───────┬────────┘         │ sale_fees   │
        │                  │              │
        │1:N               │ sale_id (FK) │
        │                  │ fee_type     │
        └──────────────────│ fee_label    │
                           │ fee_value_type│
                           │ fee_value    │
                           │ calculated   │
                           │ _amount      │
                           │ created_at   │
                           │ user_id      │
                           │ branch_id    │
                           └──────────────┘

┌─────────────────┐
│ sale_reversals  │
│                 │
│ id (PK)         │
│ original_sale_id│ (FK → sales)
│ reversal_sale_id│ (FK → sales, nullable)
│ reason          │
│ created_at      │
│ user_id         │
│ branch_id       │
└─────────────────┘
```

## Tables

### categories (Phase 0 - Already Exists)

**Purpose**: Group products into named categories (Solar Panels, Batteries, Inverters)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| `name` | VARCHAR(100) | NOT NULL, UNIQUE | Category name |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |
| `user_id` | UUID | NULL | Extensibility: future multi-user support |
| `branch_id` | UUID | NULL | Extensibility: future multi-branch support |

**Indexes**:
- `idx_categories_name` ON (name)

**Business Rules**:
- Cannot delete category with active products (FR-006)

---

### products

**Purpose**: Product catalog with pricing and stock

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| `name` | VARCHAR(200) | NOT NULL | Product name |
| `sku` | VARCHAR(50) | UNIQUE, NULLABLE | Stock Keeping Unit |
| `category_id` | UUID | FK → categories.id, NOT NULL | Category reference |
| `base_price` | DECIMAL(12,2) | NOT NULL, CHECK ≥ 0 | Cost to acquire |
| `selling_price` | DECIMAL(12,2) | NOT NULL, CHECK ≥ base_price | Price charged to customers |
| `stock_quantity` | INTEGER | NOT NULL, CHECK ≥ 0, DEFAULT 0 | Current stock level |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Soft delete flag |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |
| `user_id` | UUID | NULL | Extensibility column |
| `branch_id` | UUID | NULL | Extensibility column |

**Indexes**:
- `idx_products_name` ON (name) USING gin (gin_trgm_ops)
- `idx_products_sku` ON (sku) WHERE sku IS NOT NULL
- `idx_products_category` ON (category_id)
- `idx_products_active` ON (is_active)

**Business Rules**:
- SKU must be unique when provided (FR-002)
- selling_price ≥ base_price (FR-007)
- stock_quantity ≥ 0 (Constitution VI)
- Referenced products cannot be hard-deleted; set is_active = FALSE (FR-005)

**Computed Columns** (application-level):
- `profit_per_unit` = `selling_price` - `base_price`

---

### inventory_log

**Purpose**: Audit trail for every stock change

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| `product_id` | UUID | FK → products.id, NOT NULL | Product reference |
| `delta` | INTEGER | NOT NULL | Quantity change (+/-) |
| `reason` | VARCHAR(20) | NOT NULL | One of: 'sale', 'reversal', 'restock', 'adjustment' |
| `reference_id` | UUID | NULLABLE | FK to source record (sale_id, reversal_id, etc.) |
| `balance_after` | INTEGER | NOT NULL, CHECK ≥ 0 | Stock level after change |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `user_id` | UUID | NULL | Extensibility column |
| `branch_id` | UUID | NULL | Extensibility column |

**Indexes**:
- `idx_inventory_log_product` ON (product_id, created_at DESC)
- `idx_inventory_log_reference` ON (reference_id) WHERE reference_id IS NOT NULL

**Business Rules**:
- Every stock change MUST create a log entry (Constitution VI)
- `balance_after` = previous balance + delta
- Reference ID links to sale or reversal for audit trail

---

### payment_methods (Phase 0 - Already Exists)

**Purpose**: Configurable payment methods (cash, card, bank transfer)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| `name` | VARCHAR(50) | NOT NULL, UNIQUE | Payment method name |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Active flag |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |
| `user_id` | UUID | NULL | Extensibility column |
| `branch_id` | UUID | NULL | Extensibility column |

---

### sales

**Purpose**: Completed transactions (immutable)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| `payment_method_id` | UUID | FK → payment_methods.id, NOT NULL | Payment method |
| `subtotal` | DECIMAL(12,2) | NOT NULL, CHECK ≥ 0 | Sum of line items |
| `fees_total` | DECIMAL(12,2) | NOT NULL, DEFAULT 0, CHECK ≥ 0 | Sum of all fees |
| `vat_rate` | DECIMAL(5,2) | NULLABLE | VAT rate at time of sale (e.g., 16.00) |
| `vat_amount` | DECIMAL(12,2) | NULLABLE | Calculated VAT amount |
| `total` | DECIMAL(12,2) | NOT NULL | subtotal + fees_total + vat_amount |
| `note` | TEXT | NULLABLE | Optional note |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update (effectively immutable) |
| `user_id` | UUID | NULL | Extensibility column |
| `branch_id` | UUID | NULL | Extensibility column |

**Indexes**:
- `idx_sales_created_at` ON (created_at DESC)
- `idx_sales_payment_method` ON (payment_method_id)

**Business Rules**:
- Sale is immediately confirmed (no draft state)
- Immutable after creation (Constitution IV)
- VAT fields NULL if VAT disabled in settings

---

### sale_items

**Purpose**: Line items within a sale

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| `sale_id` | UUID | FK → sales.id, NOT NULL | Sale reference |
| `product_id` | UUID | FK → products.id, NOT NULL | Product reference |
| `product_name` | VARCHAR(200) | NOT NULL | Snapshot: product name at time of sale |
| `quantity` | INTEGER | NOT NULL, CHECK > 0 | Units sold |
| `unit_price` | DECIMAL(12,2) | NOT NULL, CHECK ≥ 0 | Price charged (may differ from selling_price) |
| `line_total` | DECIMAL(12,2) | NOT NULL | quantity × unit_price |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `user_id` | UUID | NULL | Extensibility column |
| `branch_id` | UUID | NULL | Extensibility column |

**Indexes**:
- `idx_sale_items_sale` ON (sale_id)

**Business Rules**:
- `unit_price` is the price actually charged (may include manual override)
- `product_name` snapshot preserves name even if product name changes later
- `line_total` stored explicitly (Constitution III)

---

### sale_fees

**Purpose**: Extra fees on a sale (shipping, installation, custom)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| `sale_id` | UUID | FK → sales.id, NOT NULL | Sale reference |
| `fee_type` | VARCHAR(20) | NOT NULL | 'shipping', 'installation', or 'custom' |
| `fee_label` | VARCHAR(100) | NOT NULL | Display label (e.g., "Express Shipping") |
| `fee_value_type` | VARCHAR(10) | NOT NULL | 'fixed' or 'percent' |
| `fee_value` | DECIMAL(12,2) | NOT NULL, CHECK ≥ 0 | Input value (amount or percentage) |
| `calculated_amount` | DECIMAL(12,2) | NOT NULL, CHECK ≥ 0 | Final calculated amount |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `user_id` | UUID | NULL | Extensibility column |
| `branch_id` | UUID | NULL | Extensibility column |

**Indexes**:
- `idx_sale_fees_sale` ON (sale_id)

**Business Rules**:
- If `fee_value_type = 'fixed'`, then `calculated_amount = fee_value`
- If `fee_value_type = 'percent'`, then `calculated_amount = subtotal × (fee_value / 100)`
- All fields stored explicitly (Constitution III)

---

### sale_reversals

**Purpose**: Links original sale to its reversal record

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| `original_sale_id` | UUID | FK → sales.id, NOT NULL | The reversed sale |
| `reversal_sale_id` | UUID | FK → sales.id, NULLABLE | The reversal sale (null until reversal created) |
| `reason` | TEXT | NOT NULL | Reason for reversal |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `user_id` | UUID | NULL | Extensibility column |
| `branch_id` | UUID | NULL | Extensibility column |

**Indexes**:
- `idx_sale_reversals_original` ON (original_sale_id)

**Business Rules**:
- One-to-one: a sale can be reversed only once (FR-023)
- Creates a separate reversal sale with negative quantities
- Original sale remains untouched (Constitution IV)

---

### settings (Phase 0 - Already Exists)

**Purpose**: Global system configuration

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, DEFAULT gen_random_uuid() | Primary key |
| `key` | VARCHAR(50) | NOT NULL, UNIQUE | Setting key |
| `value` | JSONB | NOT NULL | Setting value (typed JSON) |
| `created_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Creation timestamp |
| `updated_at` | TIMESTAMP WITH TIME ZONE | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Relevant Keys for Phase 1**:
- `vat_enabled` → `{ "type": "boolean", "value": true }`
- `vat_type` → `{ "type": "enum", "value": "percent" }`
- `vat_value` → `{ "type": "decimal", "value": "16.00" }`

---

## Database Constraints

###CHECK Constraints

```sql
-- Products
ALTER TABLE products ADD CONSTRAINT chk_base_price_positive CHECK (base_price >= 0);
ALTER TABLE products ADD CONSTRAINT chk_selling_price_gte_base CHECK (selling_price >= base_price);
ALTER TABLE products ADD CONSTRAINT chk_stock_non_negative CHECK (stock_quantity >= 0);

-- Sales
ALTER TABLE sales ADD CONSTRAINT chk_subtotal_positive CHECK (subtotal >= 0);
ALTER TABLE sales ADD CONSTRAINT chk_fees_positive CHECK (fees_total >= 0);
ALTER TABLE sales ADD CONSTRAINT chk_total_positive CHECK (total >= 0);

-- Sale Items
ALTER TABLE sale_items ADD CONSTRAINT chk_quantity_positive CHECK (quantity > 0);
ALTER TABLE sale_items ADD CONSTRAINT chk_unit_price_positive CHECK (unit_price >= 0);
ALTER TABLE sale_items ADD CONSTRAINT chk_line_total_positive CHECK (line_total >= 0);

-- Sale Fees
ALTER TABLE sale_fees ADD CONSTRAINT chk_fee_value_positive CHECK (fee_value >= 0);
ALTER TABLE sale_fees ADD CONSTRAINT chk_calculated_amount_positive CHECK (calculated_amount >= 0);

-- Inventory Log
ALTER TABLE inventory_log ADD CONSTRAINT chk_balance_non_negative CHECK (balance_after >= 0);
```

### Foreign Key Cascades

```sql
-- Products
ALTER TABLE products ADD CONSTRAINT fk_products_category
  FOREIGN KEY (category_id) REFERENCES categories(id)
  ON DELETE RESTRICT;

-- Sale Items
ALTER TABLE sale_items ADD CONSTRAINT fk_sale_items_sale
  FOREIGN KEY (sale_id) REFERENCES sales(id)
  ON DELETE CASCADE;

ALTER TABLE sale_items ADD CONSTRAINT fk_sale_items_product
  FOREIGN KEY (product_id) REFERENCES products(id)
  ON DELETE RESTRICT;

-- Sale Fees
ALTER TABLE sale_fees ADD CONSTRAINT fk_sale_fees_sale
  FOREIGN KEY (sale_id) REFERENCES sales(id)
  ON DELETE CASCADE;

-- Sale Reversals
ALTER TABLE sale_reversals ADD CONSTRAINT fk_reversals_original
  FOREIGN KEY (original_sale_id) REFERENCES sales(id)
  ON DELETE RESTRICT;

ALTER TABLE sale_reversals ADD CONSTRAINT fk_reversals_reversal
  FOREIGN KEY (reversal_sale_id) REFERENCES sales(id)
  ON DELETE SET NULL;

-- Inventory Log
ALTER TABLE inventory_log ADD CONSTRAINT fk_inventory_log_product
  FOREIGN KEY (product_id) REFERENCES products(id)
  ON DELETE RESTRICT;
```

---

## Data Flow

### Sale Creation (Atomic Transaction)

```
1. Validate: stock_quantity ≥ requested_quantity for all items
2. Create sale record (subtotal, fees_total, vat_amount, total)
3. Create sale_items (forEach)
4. Create sale_fees (forEach)
5. Update products: stock_quantity -= quantity (forEach)
6. Create inventory_log entries (forEach)
7. Broadcast stock update via WebSocket
```

### Sale Reversal (Atomic Transaction)

```
1. Check: original_sale has no existing reversal (prevent double reversal)
2. Create reversal record with reason
3. Update products: stock_quantity += quantity (forEach item in original)
4. Create inventory_log entries (reason = 'reversal')
5. Link reversal record to original sale
6. Broadcast stock update via WebSocket
```

---

## Indexes Summary

| Table | Index | Purpose |
|-------|-------|---------|
| products | `idx_products_name` | Fast partial name search (GIN trigram) |
| products | `idx_products_sku` | Exact SKU lookup |
| products | `idx_products_category` | Filter by category |
| products | `idx_products_active` | Filter active products |
| inventory_log | `idx_inventory_log_product` | Chronological history per product |
| sales | `idx_sales_created_at` | Date range queries |
| sale_items | `idx_sale_items_sale` | Fetch items for a sale |
| sale_fees | `idx_sale_fees_sale` | Fetch fees for a sale |
| sale_reversals | `idx_sale_reversals_original` | Check if sale reversed |

---

## Migration Notes

### Phase 1 Migrations (Alembic)

1. Create `products` table
2. Create `inventory_log` table
3. Create `sales` table
4. Create `sale_items` table
5. Create `sale_fees` table
6. Create `sale_reversals` table
7. Create all indexes
8. Add all CHECK constraints
9. Enable `pg_trgm` extension for fast name search

---

## Constitution Compliance

| Principle | Implementation |
|-----------|----------------|
| **I. Financial Accuracy** | All monetary columns use DECIMAL(12,2); no float |
| **II. Single Source of Truth** | PostgreSQL is sole source; calculations in backend |
| **III. Explicit Over Implicit** | sale_fees stores type + value + amount; VAT stored per sale |
| **IV. Immutable Records** | sales table has no UPDATE endpoint; reversals create new records |
| **VI. Data Integrity** | CHECK constraints enforce non-negative values; FKs ensure referential integrity |
| **IX. Extensibility** | user_id, branch_id on all tables |

---

## Next Steps

1. Define API contracts (see `contracts/` directory)
2. Implement SQLAlchemy models
3. Create Alembic migrations
4. Build backend services with calculation engine
5. Implement WebSocket manager for real-time updates