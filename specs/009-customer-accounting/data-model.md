# Data Model: Customer Accounting

## Entities

### Customer
Represents a credit-eligible customer.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Generated |
| name | String | Customer full name | Unique, Not Null |
| phone | String | Contact phone | Not Null |
| address | Text | Physical address | Optional |
| notes | Text | Internal notes | Optional |
| credit_limit | Decimal | Maximum debt allowed | Default: 0.00 |
| created_at | DateTime | Record creation time | Generated |
| updated_at | DateTime | Last update time | Generated |

### CustomerLedger
Append-only log of all financial interactions.

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| id | UUID | Primary Key | Generated |
| customer_id | UUID | FK to Customer | Not Null, Index |
| type | Enum | TRANSACTION_TYPE | SALE, PAYMENT, RETURN |
| amount | Decimal | Transaction value | Not Null |
| reference_id | UUID | Link to Sale | Optional (for SALE/RETURN) |
| payment_method | String | Payment method used | Optional (for PAYMENT) |
| created_at | DateTime | Transaction time | Not Null, Index |
| note | Text | Transaction note | Optional |

## Relationships
- **Customer (1) <-> CustomerLedger (N)**: A customer has many ledger entries.
- **Sale (1) <-> CustomerLedger (0..1)**: A sale may create a SALE ledger entry if a customer is selected.
- **Reversal (1) <-> CustomerLedger (0..1)**: A sale reversal may create a RETURN ledger entry.

## Logic / Derived Values
- **Balance**: `SUM(amount WHERE type=SALE) - SUM(amount WHERE type=PAYMENT) - SUM(amount WHERE type=RETURN)`
- **Available Credit**: `credit_limit - balance`
