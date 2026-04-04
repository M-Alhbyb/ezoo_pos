# Inventory API Contract

**Version**: 1.0
**Feature**: 001-core-pos-products-inventory
**Base Path**: `/api/inventory`

## Overview

Inventory management API for manual stock adjustments, restocking, and viewing stock movement history. Every stock change creates an audit trail entry.

## Endpoints

### 1. Restock Product

**POST** `/api/inventory/restock`

Adds stock to a product. Creates inventory log entry with reason "restock".

**Request Body**:
```json
{
  "product_id": "uuid",
  "quantity": 50,
  "note": "Shipment received from supplier"
}
```

**Request Schema**:
- `product_id`: required, UUID (must reference existing product)
- `quantity`: required, integer > 0
- `note`: optional, string (1-500 chars)

**Response** `200 OK`:
```json
{
  "product_id": "uuid",
  "product_name": "Panel X",
  "previous_stock": 30,
  "added_quantity": 50,
  "new_stock": 80,
  "log_entry": {
    "id": "uuid",
    "product_id": "uuid",
    "delta": 50,
    "reason": "restock",
    "note": "Shipment received from supplier",
    "balance_after": 80,
    "created_at": "2026-04-04T12:00:00Z"
  }
}
```

**Business Logic**:
1. Validate: product exists
2. Update: `products.stock_quantity += quantity`
3. Create inventory_log entry with reason "restock"
4. Broadcast stock update via WebSocket
5. Return confirmation

**Error Responses**:
- `400 Bad Request`: Validation error (quantity ≤ 0)
- `404 Not Found`: Product not found

---

###2. Manual Stock Adjustment

**POST** `/api/inventory/adjust`

Manually adjusts product stock (increase or decrease) with a required reason. Creates inventory log entry with reason "adjustment".

**Request Body**:
```json
{
  "product_id": "uuid",
  "delta": -5,
  "reason": "damaged",
  "note": "5 units damaged during transport"
}
```

**Request Schema**:
- `product_id`: required, UUID (must reference existing product)
- `delta`: required, integer (positive or negative)
- `reason`: required, string (1-100 chars)
- `note`: optional, string (1-500 chars)

**Validation**:
- `delta` can be positive (increase) or negative (decrease)
- Resulting stock must be ≥ 0 (Constitution VI)

**Response** `200 OK`:
```json
{
  "product_id": "uuid",
  "product_name": "Panel X",
  "previous_stock": 80,
  "delta": -5,
  "new_stock": 75,
  "log_entry": {
    "id": "uuid",
    "product_id": "uuid",
    "delta": -5,
    "reason": "adjustment",
    "note": "damaged",
    "balance_after": 75,
    "created_at": "2026-04-04T12:30:00Z"
  }
}
```

**Business Logic**:
1. Validate: product exists
2. Validate: resulting stock (current + delta) ≥ 0
3. Update: `products.stock_quantity += delta`
4. Create inventory_log entry with reason "adjustment"
5. Broadcast stock update via WebSocket
6. Return confirmation

**Error Responses**:
- `400 Bad Request`: Validation error or resulting stock < 0
  ```json
  {
    "error": {
      "code": "INSUFFICIENT_STOCK",
      "message": "Adjustment would result in negative stock",
      "details": {
        "product_name": "Panel X",
        "current_stock": 3,
        "delta": -5,
        "resulting_stock": -2
      }
    }
  }
  ```
- `404 Not Found`: Product not found

---

### 3. Get Inventory Log

**GET** `/api/inventory/log/{product_id}`

Retrieves paginated stock movement history for a specific product.

**Path Parameters**:
- `product_id`: Product UUID

**Query Parameters**:
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50, max: 100)
- `start_date` (optional): Filter by date range (ISO 8601)
- `end_date` (optional): Filter by date range (ISO 8601)

**Response** `200 OK`:
```json
{
  "product_id": "uuid",
  "product_name": "Panel X",
  "current_stock": 75,
  "items": [
    {
      "id": "uuid",
      "delta": -5,
      "reason": "adjustment",
      "note": "damaged",
      "reference_id": null,
      "balance_after": 75,
      "created_at": "2026-04-04T12:30:00Z"
    },
    {
      "id": "uuid",
      "delta": 50,
      "reason": "restock",
      "note": "Shipment received",
      "reference_id": null,
      "balance_after": 80,
      "created_at": "2026-04-04T12:00:00Z"
    },
    {
      "id": "uuid",
      "delta": -2,
      "reason": "sale",
      "note": null,
      "reference_id": "uuid-sale-id",
      "balance_after": 30,
      "created_at": "2026-04-04T11:00:00Z"
    }
  ],
  "total": 120,
  "page": 1,
  "page_size": 50
}
```

**Log Entry Types**:
- `sale`: Stock deducted from confirmed sale (reference_id = sale.id)
- `reversal`: Stock restored from sale reversal (reference_id = reversal.id)
- `restock`: Manual stock addition (reference_id = null)
- `adjustment`: Manual adjustment increase/decrease (reference_id = null)

---

### 4. Get Low Stock Products

**GET** `/api/inventory/low-stock`

Retrieves products with stock below a threshold.

**Query Parameters**:
- `threshold` (optional): Stock threshold (default: 10)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50, max: 100)

**Response** `200 OK`:
```json
{
  "threshold": 10,
  "items": [
    {
      "product_id": "uuid",
      "product_name": "Battery B",
      "sku": "BAT-002",
      "current_stock": 3,
      "category_name": "Batteries"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 50
}
```

---

## Data Types

### Inventory Log Entry

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Log entry identifier |
| `product_id` | UUID | Product reference |
| `delta` | Integer | Quantity change (+ or -) |
| `reason` | Enum | 'sale', 'reversal', 'restock', 'adjustment' |
| `note` | String | Optional note (nullable) |
| `reference_id` | UUID | Reference to source record (nullable) |
| `balance_after` | Integer | Stock level after change |
| `created_at` | Timestamp | Creation datetime |

### Restock Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_id` | UUID | Yes | Product reference |
| `quantity` | Integer | Yes | Quantity to add (> 0) |
| `note` | String | No | Optional note |

### Adjustment Request

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product_id` | UUID | Yes | Product reference |
| `delta` | Integer | Yes | Quantity change (+ or -) |
| `reason` | String | Yes | Reason for adjustment |
| `note` | String | No | Optional note |

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
- `INSUFFICIENT_STOCK`: Adjustment would cause negative stock
- `NOT_FOUND`: Product not found
- `INTERNAL_ERROR`: Server error

---

## Constitution Compliance

| Principle | Implementation |
|-----------|----------------|
| **VI. Data Integrity** | Stock ≥ 0 enforced at database and API level; inventory_log for every change |
| **IV. Immutable Records** | Log entries are append-only (noUPDATE endpoint) |
| **VII. Backend Authority** | Stock validation in service layer |

---

## WebSocket Integration

**Channel**: `/ws/stock-updates`

All inventory operations (restock, adjust) broadcast stock updates:

```json
{
  "event": "stock_updated",
  "data": {
    "product_id": "uuid",
    "stock_quantity": 75
  }
}
```

---

## Next Steps

1. Implement inventory service with stock validation
2. Create Alembic migration for inventory_log table
3. Add low stock alert functionality
4. Write integration tests for stock adjustment edge cases