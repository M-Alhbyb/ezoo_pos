# Sales API Contract

**Version**: 1.0
**Feature**: 001-core-pos-products-inventory
**Base Path**: `/api/sales`

## Overview

Point-of-sale API for creating sales, calculating financial breakdowns, and processing reversals. All financial calculations performed server-side (Constitution II).

## Endpoints

### 1. Calculate Sale Preview

**POST** `/api/sales/calculate`

Calculates the financial breakdown (subtotal, fees, VAT, total) for a proposed sale without creating a record. Frontend MUST call this endpoint to display totals before confirmation.

**Request Body**:
```json
{
  "items": [
    {
      "product_id": "uuid",
      "quantity": 2,
      "unit_price_override": 140.00
    }
  ],
  "fees": [
    {
      "fee_type": "shipping",
      "fee_label": "Standard Shipping",
      "fee_value_type": "fixed",
      "fee_value": 30.00
    },
    {
      "fee_type": "custom",
      "fee_label": "Service Fee",
      "fee_value_type": "percent","fee_value": 5.00
    }
  ]
}
```

**Request Schema**:
- `items`: Array of line items
  - `product_id`: required, UUID
  - `quantity`: required, integer > 0
  - `unit_price_override`: optional, decimal ≥ 0 (if omitted, uses product's selling_price)
- `fees`: Array of extra fees (optional)
  - `fee_type`: required, enum ('shipping', 'installation', 'custom')
  - `fee_label`: required, string (1-100 chars)
  - `fee_value_type`: required, enum ('fixed', 'percent')
  - `fee_value`: required, decimal ≥ 0

**Response** `200 OK`:
```json
{
  "breakdown": {
    "items": [
      {
        "product_id": "uuid",
        "product_name": "Panel X",
        "quantity": 2,
        "unit_price": "140.00",
        "line_total": "280.00"
      }
    ],
    "subtotal": "280.00",
    "fees": [
      {
        "fee_type": "shipping",
        "fee_label": "Standard Shipping",
        "fee_value_type": "fixed",
        "fee_value": "30.00",
        "calculated_amount": "30.00"
      },
      {
        "fee_type": "custom",
        "fee_label": "Service Fee",
        "fee_value_type": "percent",
        "fee_value": "5.00",
        "calculated_amount": "14.00"
      }
    ],
    "fees_total": "44.00",
    "vat_enabled": true,
    "vat_rate": "16.00",
    "vat_amount": "51.84",
    "total": "375.84",
    "warning": null
  }
}
```

**Response Fields**:
- `subtotal`: Sum of all line totals (DECIMAL)
- `fees_total`: Sum of all calculated fee amounts (DECIMAL)
- `vat_enabled`: Whether VAT is enabled in settings (BOOLEAN)
- `vat_rate`: VAT rate from settings (DECIMAL or NULL)
- `vat_amount`: Calculated VAT (DECIMAL or NULL)
- `total`: subtotal + fees_total + vat_amount (DECIMAL)
- `warning`: Optional warning message (STRING or NULL) - e.g., "unit_price below base_price"

**Calculation Rules**:
- VAT = (subtotal + fees_total) × (vat_rate / 100) if VAT enabled
- Percentage fees calculated against subtotal
- All values rounded to 2 decimal places using ROUND_HALF_UP

**Error Responses**:
- `400 Bad Request`: Validation error
- `404 Not Found`: Product not found

---

### 2. Create Sale

**POST** `/api/sales`

Creates a confirmed sale record (immediately immutable). Deducts stock atomically.

**Request Body**:
```json
{
  "items": [
    {
      "product_id": "uuid",
      "quantity": 2,
      "unit_price_override": 140.00
    }
  ],
  "fees": [
    {
      "fee_type": "shipping",
      "fee_label": "Standard Shipping",
      "fee_value_type": "fixed",
      "fee_value": 30.00
    }
  ],
  "payment_method_id": "uuid",
  "note": "Customer requested delivery by Friday"
}
```

**Request Schema**:
- `items`: required, array with ≥ 1 item
  - `product_id`: required, UUID
  - `quantity`: required, integer > 0
  - `unit_price_override`: optional, decimal ≥ 0
- `fees`: optional, array
- `payment_method_id`: required, UUID (must reference active payment method)
- `note`: optional, string

**Response** `201 Created`:
```json
{
  "id":"uuid",
  "payment_method_id": "uuid",
  "payment_method_name": "Cash",
  "items": [
    {
      "product_id": "uuid",
      "product_name": "Panel X",
      "quantity": 2,
      "unit_price": "140.00",
      "line_total": "280.00"
    }
  ],
  "subtotal": "280.00",
  "fees": [
    {
      "fee_type": "shipping",
      "fee_label": "Standard Shipping",
      "fee_value_type": "fixed",
      "fee_value": "30.00",
      "calculated_amount": "30.00"
    }
  ],
  "fees_total": "30.00",
  "vat_enabled": true,
  "vat_rate": "16.00",
  "vat_amount": "49.60",
  "total": "359.60",
  "note": "Customer requested delivery by Friday",
  "created_at": "2026-04-04T12:00:00Z"
}
```

**Business Logic (Atomic Transaction)**:
1. Validate: all products exist and have stock ≥ requested quantity
2. Validate: payment_method exists and is active
3. Calculate financial totals (using calculation engine)
4. Create sale record with breakdown
5. Create sale_items (snapshot: product_name, unit_price, line_total)
6. Create sale_fees (snapshot: all fee details + calculated_amount)
7. Deduct stock for each product
8. Create inventory_log entries (reason = 'sale')
9. Broadcast stock update via WebSocket
10. Return confirmed sale

**Error Responses**:
- `400 Bad Request`: Validation error or insufficient stock
  ```json
  {
    "error": {
      "code": "INSUFFICIENT_STOCK",
      "message": "Insufficient stock for product 'Panel X'",
      "details": {
        "product_name": "Panel X",
        "available": 3,
        "requested": 5
      }
    }
  }
  ```
- `404 Not Found`: Product or payment method not found

---

### 3. List Sales

**GET** `/api/sales`

Retrieves paginated sale history with filters.

**Query Parameters**:
- `start_date` (optional): Filter by date range (ISO 8601)
- `end_date` (optional): Filter by date range (ISO 8601)
- `payment_method_id` (optional): Filter by payment method
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50, max: 100)

**Response** `200 OK`:
```json
{
  "items": [
    {
      "id": "uuid",
      "payment_method_name": "Cash",
      "total": "359.60",
      "created_at": "2026-04-04T12:00:00Z",
      "reversed": false
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 50
}
```

---

### 4. Get Sale Detail

**GET** `/api/sales/{id}`

Retrieves complete sale breakdown.

**Path Parameters**:
- `id`: Sale UUID

**Response** `200 OK`:
```json
{
  "id": "uuid",
  "payment_method_id": "uuid",
  "payment_method_name": "Cash",
  "items": [
    {
      "product_id": "uuid",
      "product_name": "Panel X",
      "quantity": 2,
      "unit_price": "140.00",
      "line_total": "280.00"
    }
  ],
  "subtotal": "280.00",
  "fees": [
    {
      "fee_type": "shipping",
      "fee_label": "Standard Shipping",
      "fee_value_type": "fixed",
      "fee_value": "30.00",
      "calculated_amount": "30.00"
    }
  ],
  "fees_total": "30.00",
  "vat_enabled": true,
  "vat_rate": "16.00",
  "vat_amount": "49.60",
  "total": "359.60",
  "note": "Customer requested delivery by Friday",
  "reversed": false,
  "reversal": null,
  "created_at": "2026-04-04T12:00:00Z"
}
```

**Field: `reversal`**:
- If sale has been reversed: contains reversal record details
- If sale has NOT been reversed: `null`

**Response for Reversed Sale**:
```json
{
  "id": "uuid","reversed": true,
  "reversal": {
    "id": "uuid",
    "reason": "Customer return",
    "created_at": "2026-04-04T14:00:00Z"
  },
  ...
}
```

**Error Responses**:
- `404 Not Found`: Sale not found

---

### 5. Reverse Sale

**POST** `/api/sales/{id}/reverse`

Creates a reversal for a confirmed sale. Restores stock atomically.

**Path Parameters**:
- `id`: Sale UUID

**Request Body**:
```json
{
  "reason": "Customer return - items damaged"
}
```

**Request Schema**:
- `reason`: required, string (1-500 chars)

**Response** `201 Created`:
```json
{
  "id": "uuid",
  "original_sale_id": "uuid",
  "reason": "Customer return - items damaged",
  "created_at": "2026-04-04T14:00:00Z"
}
```

**Business Logic (Atomic Transaction)**:
1. Validate: sale exists and has NOT been reversed
2. Validate: reason provided
3. Create reversal record linking to original sale
4. Restore stock for each item in original sale
5. Create inventory_log entries (reason = 'reversal')
6. Broadcast stock update via WebSocket
7. Return reversal record

**Error Responses**:
- `400 Bad Request`: Sale already reversed
  ```json
  {
    "error": {
      "code": "ALREADY_REVERSED",
      "message": "This sale has already been reversed",
      "details": {
        "sale_id": "uuid",
        "reversal_id": "uuid"
      }
    }
  }
  ```
- `404 Not Found`: Sale not found

---

## Data Types

###Sale Item Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_id` | UUID | Yes | Product reference |
| `quantity` | Integer | Yes | Quantity > 0 |
| `unit_price_override` | Decimal | No | Override price (uses selling_price if omitted) |

### Sale Item Response

| Field | Type | Description |
|-------|------|-------------|
| `product_id` | UUID | Product reference |
| `product_name` | String | Snapshot of product name |
| `quantity` | Integer | Quantity sold |
| `unit_price` | Decimal | Price charged (may differ from selling_price) |
| `line_total` | Decimal | quantity × unit_price |

### Fee Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `fee_type` | Enum | Yes | 'shipping', 'installation', 'custom' |
| `fee_label` | String | Yes | Display label (1-100 chars) |
| `fee_value_type` | Enum | Yes | 'fixed' or 'percent' |
| `fee_value` | Decimal | Yes |Amount or percentage |

### Fee Response

| Field | Type | Description |
|-------|------|-------------|
| `fee_type` | Enum | Type of fee |
| `fee_label` | String | Display label |
| `fee_value_type` | Enum | 'fixed' or 'percent' |
| `fee_value` | Decimal | Input value |
| `calculated_amount` | Decimal | Final calculated amount |

### Sale Response

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Sale identifier |
| `payment_method_id` | UUID | Payment method reference |
| `payment_method_name` | String | Payment method name |
| `items` | Array | Line items |
| `subtotal` | Decimal | Sum of line totals |
| `fees` | Array | Fee breakdown |
| `fees_total` | Decimal | Sum of fee amounts |
| `vat_enabled` | Boolean | Whether VAT was applied |
| `vat_rate` | Decimal | VAT rate at time of sale |
| `vat_amount` | Decimal | Calculated VAT |
| `total` | Decimal | subtotal + fees_total + vat_amount |
| `note` | String | Optional note |
| `reversed` | Boolean | Whether sale was reversed |
| `reversal` | Object | Reversal details (nullable) |
| `created_at` | Timestamp | Creation datetime |

---

## Error Handling

All errors follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {
      "field": "value"
    }
  }
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Request validation failed
- `INSUFFICIENT_STOCK`: Not enough stock for sale
- `ALREADY_REVERSED`: Sale has already been reversed
- `NOT_FOUND`: Resource not found
- `INTERNAL_ERROR`: Server error

---

## Constitution Compliance

| Principle | Implementation |
|-----------|----------------|
| **I. Financial Accuracy** | All calculations via calculation engine in`app/core/calculations.py`, DECIMAL types |
| **II. Single Source of Truth** | Frontend calls `/calculate` to get breakdown; frontend does not compute financial totals |
| **III. Explicit Over Implicit** | All fees store type + value + calculated_amount; VAT stored per sale |
| **IV. Immutable Records** | Sales immediately confirmed; no UPDATE endpoint; reversals create new records |
| **VI. Data Integrity** | Stock deduction atomic; CHECK constraints; inventory_log for every change |
| **VII. Backend Authority** | All validation and calculation in backend service layer |

---

## WebSocket Integration

**Channel**: `/ws/stock-updates`

**Broadcast Event** (after sale creation):
```json
{
  "event": "stock_updated",
  "data": {
    "product_id": "uuid",
    "stock_quantity": 48
  }
}
```

**Broadcast Event** (afterreversal):
```json
{
  "event": "stock_updated",
  "data": {
    "product_id": "uuid",
    "stock_quantity": 50
  }
}
```

Frontend POS screen subscribes to this channel and updates product search results in real-time.

---

## Next Steps

1. Implement calculation engine (`app/core/calculations.py`)
2. Implement Pydantic schemas for request/response
3. Build sale service with atomic transaction
4. Integrate WebSocket manager for stock broadcasts
5. Write unit tests for calculation edge cases