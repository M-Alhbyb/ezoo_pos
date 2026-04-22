# API Contract: Customer Accounting

## Customers

### List Customers
`GET /api/v1/customers`
- **Response**: `200 OK`
  ```json
  {
    "customers": [
      {
        "id": "uuid",
        "name": "string",
        "phone": "string",
        "balance": 150.00,
        "credit_limit": 1000.00
      }
    ],
    "total": 1
  }
  ```

### Create Customer
`POST /api/v1/customers`
- **Request**:
  ```json
  {
    "name": "string",
    "phone": "string",
    "address": "string",
    "notes": "string",
    "credit_limit": 1000.00
  }
  ```

### Get Customer Detail
`GET /api/v1/customers/{id}`
- **Response**: `200 OK`
  ```json
  {
    "id": "uuid",
    "name": "string",
    "summary": {
      "total_sales": 1000.00,
      "total_payments": 800.00,
      "total_returns": 50.00,
      "balance": 150.00
    },
    "credit_limit": 1000.00
  }
  ```

### Record Payment
`POST /api/v1/customers/{id}/payments`
- **Request**:
  ```json
  {
    "amount": 200.00,
    "payment_method": "Cash",
    "note": "Payment for previous sales"
  }
  ```

## Ledger

### List Ledger Entries
`GET /api/v1/customers/{id}/ledger`
- **Params**: `page`, `page_size`, `start_date`, `end_date`
- **Response**:
  ```json
  {
    "entries": [
      {
        "id": "uuid",
        "type": "SALE",
        "amount": 500.00,
        "reference_id": "sale-uuid",
        "created_at": "iso-date"
      }
    ],
    "total": 1
  }
  ```

## POS Integration

### Update Sale Creation
`POST /api/v1/pos/sales`
- **Request (Add field)**:
  ```json
  {
    ...
    "customer_id": "uuid (optional)"
  }
  ```
- **Behavior**: If `customer_id` is provided, validate `credit_limit` before processing. Create `SALE` ledger entry.
