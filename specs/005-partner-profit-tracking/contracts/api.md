# API Contracts: Partner ProfitTracking

**Feature**: 005-partner-profit-tracking
**Date**: 2026-04-08

## Overview

This document defines REST API contracts for partner profit tracking endpoints, following existing patterns from products, sales, and partners modules.

---

## Base URL

All endpoints prefixed with `/api/v1`

---

## Endpoints

### 1. Product Assignment Management

#### Create Product Assignment

**Endpoint**: `POST /api/v1/partners/assignments`

**Description**: Assign a specific quantity of a product to a partner for profit sharing.

**Request Body**:
```json
{
  "partner_id": "UUID",
  "product_id": "UUID",
  "assigned_quantity": 10,
  "share_percentage": 15.00
}
```

**Constraints**:
- `partner_id` must exist in partners table
- `product_id` must exist in products table
- `assigned_quantity` must be > 0
- `share_percentage` must be >=0 and <=100
- If `share_percentage` not provided, use partner's default share_percentage

**Response**: `201 Created`
```json
{
  "id": "UUID",
  "partner_id": "UUID",
  "partner_name": "Partner Name",
  "product_id": "UUID",
  "product_name": "Product Name",
  "assigned_quantity": 10,
  "remaining_quantity": 10,
  "share_percentage": "15.00",
  "status": "active",
  "created_at": "2026-04-08T10:30:00Z",
  "updated_at": "2026-04-08T10:30:00Z"
}
```

**Errors**:
- `400 Bad Request`: Validation error (quantity < 1, share_percentage out of range)
- `404 Not Found`: Partner or product not found
- `409 Conflict`: Product already has an active assignment

---

#### Get All Assignments

**Endpoint**: `GET /api/v1/partners/assignments`

**Query Parameters**:
- `partner_id` (optional): Filter by partner
- `product_id` (optional): Filter by product
- `status` (optional): Filter by status ('active' or 'fulfilled')
- `limit` (optional): Max results (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response**: `200 OK`
```json
{
  "assignments": [
    {
      "id": "UUID",
      "partner_id": "UUID",
      "partner_name": "Partner Name",
      "product_id": "UUID",
      "product_name": "Product Name",
      "assigned_quantity": 10,
      "remaining_quantity": 7,
      "share_percentage": "15.00",
      "status": "active",
      "created_at": "2026-04-08T10:30:00Z",
      "updated_at": "2026-04-08T12:15:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

---

#### Get Assignment by ID

**Endpoint**: `GET /api/v1/partners/assignments/{assignment_id}`

**Response**: `200 OK`
```json
{
  "id": "UUID",
  "partner_id": "UUID",
  "partner_name": "Partner Name",
  "product_id": "UUID",
  "product_name": "Product Name",
  "assigned_quantity": 10,
  "remaining_quantity": 7,
  "share_percentage": "15.00",
  "status": "active",
  "created_at": "2026-04-08T10:30:00Z",
  "updated_at": "2026-04-08T12:15:00Z",
  "fulfilled_at": null
}
```

**Errors**:
- `404 Not Found`: Assignment not found

---

#### Update Assignment

**Endpoint**: `PATCH /api/v1/partners/assignments/{assignment_id}`

**Request Body**:
```json
{
  "assigned_quantity": 15,
  "share_percentage": 20.00
}
```

**Notes**:
- Can only update `assigned_quantity` and `share_percentage`
- Increasing `assigned_quantity` increases `remaining_quantity` by delta
- Decreasing `assigned_quantity` decreases `remaining_quantity` by delta (must not go below 0)
- Cannot update fulfilled assignments (status = 'fulfilled')

**Response**: `200 OK`
```json
{
  "id": "UUID",
  "partner_id": "UUID",
  "product_id": "UUID",
  "assigned_quantity": 15,
  "remaining_quantity": 12,
  "share_percentage": "20.00",
  "status": "active",
  "updated_at": "2026-04-08T14:00:00Z"
}
```

**Errors**:
- `400 Bad Request`: Validation error (quantity < 1, share_percentage out of range)
- `404 Not Found`: Assignment not found
- `409 Conflict`: Cannot update fulfilled assignment

---

#### Delete Assignment

**Endpoint**: `DELETE /api/v1/partners/assignments/{assignment_id}`

**Notes**:
- Can only delete assignments with status = 'active' and remaining_quantity = assigned_quantity (no sales yet)
- Otherwise, assignment must remain for audit trail

**Response**: `204 No Content`

**Errors**:
- `404 Not Found`: Assignment not found
- `409 Conflict`: Cannot delete assignment with sales (has remaining_quantity < assigned_quantity)

---

### 2. Partner Wallet Management

#### Get Partner Wallet Balance

**Endpoint**: `GET /api/v1/partners/{partner_id}/wallet`

**Description**: Get current wallet balance for a partner.

**Response**: `200 OK`
```json
{
  "partner_id": "UUID",
  "partner_name": "Partner Name",
  "current_balance": "1523.45",
  "last_transaction_at": "2026-04-08T14:30:00Z"
}
```

**Errors**:
- `404 Not Found`: Partner not found

---

#### Get Partner Transaction History

**Endpoint**: `GET /api/v1/partners/{partner_id}/wallet/transactions`

**Query Parameters**:
- `limit` (optional): Max results (default: 100)
- `offset` (optional): Pagination offset (default: 0)
- `transaction_type` (optional): Filter by type ('sale_profit' or 'manual_adjustment')
- `start_date` (optional): Filter from date (ISO 8601)
- `end_date` (optional): Filter to date (ISO 8601)

**Response**: `200 OK`
```json
{
  "transactions": [
    {
      "id": "UUID",
      "partner_id": "UUID",
      "amount": "45.50",
      "transaction_type": "sale_profit",
      "reference_id": "UUID",
      "reference_type": "sale",
      "description": "Sale profit: 5 × 100.00 × 15.00% from Solar Panel",
      "balance_after": "1523.45",
      "created_at": "2026-04-08T14:30:00Z"
    },
    {
      "id": "UUID",
      "partner_id": "UUID",
      "amount": "-100.00",
      "transaction_type": "manual_adjustment",
      "reference_id": null,
      "reference_type": null,
      "description": "Payout for April 2026",
      "balance_after": "1423.45",
      "created_at": "2026-04-08T12:00:00Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

---

#### Manual Wallet Adjustment

**Endpoint**: `POST /api/v1/partners/{partner_id}/wallet/adjust`

**Description**: Admin manually adjusts partner wallet balance.

**Request Body**:
```json
{
  "amount": -50.00,
  "description": "Payout for March 2026"
}
```

**Notes**:
- Negative `amount` decreases balance
- Positive `amount` increases balance
- `amount` cannot be 0

**Response**: `201 Created`
```json
{
  "id": "UUID",
  "partner_id": "UUID",
  "amount": "-50.00",
  "transaction_type": "manual_adjustment",
  "description": "Payout for March 2026",
  "balance_after": "1473.45",
  "created_at": "2026-04-08T15:00:00Z"
}
```

**Errors**:
- `400 Bad Request`: Validation error (amount = 0)
- `404 Not Found`: Partner not found

---

### 3. Product Inventory View (Extended)

#### Get Product Inventory with Assignment Info

**Endpoint**: `GET /api/v1/products`

**Note**: Extend existing endpoint to include assignment information.

**Response** (existing fields + new):
```json
{
  "products": [
    {
      "id": "UUID",
      "name": "Solar Panel",
      "sku": "SP-001",
      "stock_quantity": 50,
      "base_price": "200.00",
      "selling_price": "350.00",
      "is_active": true,
      "assignment": {
        "id": "UUID",
        "partner_id": "UUID",
        "partner_name": "Partner Name",
        "assigned_quantity": 10,
        "remaining_quantity": 7,
        "share_percentage": "15.00",
        "status": "active"
      }
    },
    {
      "id": "UUID",
      "name": "Battery",
      "sku": "BAT-001",
      "stock_quantity": 30,
      "base_price": "80.00",
      "selling_price": "120.00",
      "is_active": true,
      "assignment": null
    }
  ]
}
```

---

## Error Response Format

All errors follow this format:

```json
{
  "detail": "Error message",
  "errors": [
    {
      "field": "assigned_quantity",
      "message": "Quantity must be greater than 0"
    }
  ]
}
```

---

## Authentication & Authorization

All endpoints require authentication. Authorization:

| Endpoint | Role Required |
|----------|---------------|
| Product Assignment CRUD | Admin |
| Partner Wallet View | Admin |
| Partner Wallet Adjust | Admin |
| Product Inventory View | Admin |

**Note**: Partners do NOT have direct system access (per spec clarification).

---

## Rate Limiting

Standard rate limits apply:
- Read endpoints: 100 requests per minute
- Write endpoints: 30 requests per minute

---

## Pagination

List endpoints support cursor-based pagination:

```json
{
  "items": [...],
  "total": 100,
  "limit": 50,
  "offset": 0,
  "next_cursor": "base64encodedcursor"
}
```

---

## WebSocket Events (Future Enhancement)

Optional real-time updates via WebSocket:

### Wallet Updated Event

```json
{
  "event": "partner_wallet_updated",
  "partner_id": "UUID",
  "new_balance": "1523.45",
  "transaction_id": "UUID",
  "timestamp": "2026-04-08T14:30:00Z"
}
```

---

## Constitution Compliance

| Principle | Implementation |
|-----------|----------------|
| **I. Financial Accuracy** | All monetary values as DECIMAL strings in JSON |
| **II. Single Source of Truth** | Backend computes balance; frontend displays only |
| **III. Explicit Over Implicit** | share_percentage stored per assignment |
| **VII. Backend Authority** | All validation in Pydantic schemas + service layer |
| **VIII. Input Validation** | All endpoints validate request bodies |

---

## Testing Contract

### Test Scenarios

1. **Create Assignment**:
   - Valid assignment created
   - Partner not found → 404
   - Product not found → 404
   - Duplicate active assignment → 409

2. **Sale with Assignment**:
   - Partner wallet credited correctly
   - Assignment remaining_quantity decreased
   - Assignment fulfilled when remaining_quantity = 0

3. **Manual Wallet Adjustment**:
   - Positive amount increases balance
   - Negative amount decreases balance
   - Amount = 0 → 400

4. **Concurrent Sales**:
   - Multiple sales for same partner → no race condition
   - Wallet balance consistent
   

5. **Immutable Transactions**:
   - Cannot update/delete PartnerWalletTransaction
   - Only CREATE operations allowed