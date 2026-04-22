# API Contracts: Supplier Accounting System

## Suppliers

### Create Supplier

**POST** `/api/suppliers`

Request:
```json
{
  "name": "string (required)",
  "phone": "string (optional)",
  "notes": "string (optional)"
}
```

Response (201):
```json
{
  "id": "uuid",
  "name": "string",
  "phone": "string | null",
  "notes": "string | null",
  "created_at": "datetime"
}
```

### List Suppliers

**GET** `/api/suppliers`

Response (200):
```json
{
  "suppliers": [
    {
      "id": "uuid",
      "name": "string",
      "phone": "string | null",
      "created_at": "datetime",
      "balance": "decimal"
    }
  ]
}
```

### Get Supplier

**GET** `/api/suppliers/{id}`

Response (200):
```json
{
  "id": "uuid",
  "name": "string",
  "phone": "string | null",
  "notes": "string | null",
  "created_at": "datetime",
  "summary": {
    "total_purchases": "decimal",
    "total_payments": "decimal",
    "total_returns": "decimal",
    "balance": "decimal"
  }
}
```

## Purchases

### Create Purchase

**POST** `/api/purchases`

Request:
```json
{
  "supplier_id": "uuid (required)",
  "items": [
    {
      "product_id": "uuid (required)",
      "quantity": "integer > 0 (required)",
      "unit_cost": "decimal >= 0 (required)"
    }
  ]
}
```

Response (201):
```json
{
  "id": "uuid",
  "supplier_id": "uuid",
  "total_amount": "decimal",
  "created_at": "datetime",
  "items": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "quantity": "integer",
      "unit_cost": "decimal",
      "total_cost": "decimal"
    }
  ]
}
```

### List Purchases

**GET** `/api/purchases`

Query params: `supplier_id`, `limit`, `offset`

Response (200):
```json
{
  "purchases": [
    {
      "id": "uuid",
      "supplier_id": "uuid",
      "supplier_name": "string",
      "total_amount": "decimal",
      "created_at": "datetime"
    }
  ]
}
```

### Get Purchase

**GET** `/api/purchases/{id}`

Response (200):
```json
{
  "id": "uuid",
  "supplier_id": "uuid",
  "total_amount": "decimal",
  "created_at": "datetime",
  "items": [
    {
      "id": "uuid",
      "product_id": "uuid",
      "product_name": "string",
      "quantity": "integer",
      "unit_cost": "decimal",
      "total_cost": "decimal"
    }
  ]
}
```

## Payments

### Record Payment

**POST** `/api/suppliers/{id}/payments`

Request:
```json
{
  "amount": "decimal > 0 (required)",
  "note": "string (optional)"
}
```

Response (201):
```json
{
  "id": "uuid",
  "supplier_id": "uuid",
  "type": "PAYMENT",
  "amount": "decimal",
  "note": "string | null",
  "created_at": "datetime"
}
```

## Returns

### Return Items

**POST** `/api/purchases/{id}/return`

Request:
```json
{
  "items": [
    {
      "product_id": "uuid (required)",
      "quantity": "integer > 0 (required)"
    }
  ],
  "note": "string (optional)"
}
```

Response (201):
```json
{
  "id": "uuid",
  "purchase_id": "uuid",
  "total_returned": "decimal",
  "created_at": "datetime",
  "items": [
    {
      "product_id": "uuid",
      "quantity": "integer",
      "unit_cost": "decimal",
      "total_cost": "decimal"
    }
  ]
}
```

## Reports

### Supplier Summary Report

**GET** `/api/reports/suppliers`

Response (200):
```json
{
  "suppliers": [
    {
      "id": "uuid",
      "name": "string",
      "total_purchases": "decimal",
      "total_payments": "decimal",
      "total_returns": "decimal",
      "balance": "decimal"
    }
  ]
}
```

### Supplier Statement

**GET** `/api/reports/suppliers/{id}`

Query params: `start_date`, `end_date`

Response (200):
```json
{
  "supplier": {
    "id": "uuid",
    "name": "string"
  },
  "summary": {
    "total_purchases": "decimal",
    "total_payments": "decimal",
    "total_returns": "decimal",
    "balance": "decimal"
  },
  "ledger": [
    {
      "id": "uuid",
      "type": "PURCHASE | PAYMENT | RETURN",
      "amount": "decimal",
      "reference_id": "uuid | null",
      "note": "string | null",
      "created_at": "datetime"
    }
  ]
}
```

## Error Responses

All endpoints may return:

**400** - Validation error
```json
{
  "detail": "Error message"
}
```

**404** - Not found
```json
{
  "detail": "Resource not found"
}
```

**422** - Business logic error
```json
{
  "detail": "Cannot return more than purchased"
}
```
