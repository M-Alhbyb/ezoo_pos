# API Contracts: Partner Profit System

## Backend API Endpoints

### Assign Product to Partner

**POST** `/api/partners/{partner_id}/products`

Request:
```json
{
  "product_id": "uuid"
}
```

Response (201):
```json
{
  "id": "uuid",
  "product_id": "uuid",
  "partner_id": "uuid", 
  "is_active": true,
  "created_at": "2026-04-11T10:00:00Z"
}
```

Errors:
- 400: Product already assigned to another partner
- 404: Partner or product not found

### Unassign Product from Partner

**DELETE** `/api/partners/{partner_id}/products/{product_id}`

Response (204): No content

### Get Partner Products

**GET** `/api/partners/{partner_id}/products`

Response (200):
```json
[
  {
    "id": "uuid",
    "product_id": "uuid",
    "product_name": "Solar Panel 400W",
    "is_active": true,
    "created_at": "2026-04-11T10:00:00Z"
  }
]
```

### Get Partner Wallet Summary

**GET** `/api/partners/{partner_id}/wallet`

Response (200):
```json
{
  "partner_id": "uuid",
  "total_profit": 1500.00,
  "transaction_count": 25,
  "last_transaction_at": "2026-04-11T10:00:00Z"
}
```

### Get Partner Wallet Transactions

**GET** `/api/partners/{partner_id}/wallet/transactions?start_date={date}&end_date={date}`

Response (200):
```json
[
  {
    "id": "uuid",
    "product_id": "uuid",
    "product_name": "Solar Panel 400W",
    "selling_price": 500.00,
    "base_cost": 350.00,
    "profit_amount": 150.00,
    "transaction_type": "PROFIT",
    "created_at": "2026-04-11T10:00:00Z"
  }
]
```

### Internal: Credit Profit on Sale

**POST** `/internal/wallet/credit-profit`

Called by POS service after sale confirmation. Request:
```json
{
  "sale_id": "uuid",
  "items": [
    {
      "product_id": "uuid",
      "selling_price": 500.00,
      "quantity": 2
    }
  ]
}
```

Response (201):
```json
[
  {
    "partner_id": "uuid",
    "profit_amount": 300.00,
    "product_id": "uuid"
  }
]
```

### Internal: Reverse Profit on Refund

**POST** `/internal/wallet/reverse-profit`

Called by POS service when refund is issued. Request:
```json
{
  "sale_id": "uuid",
  "reason": "customer_request"
}
```

Response (201):
```json
[
  {
    "partner_id": "uuid",
    "reversed_amount": 150.00,
    "product_id": "uuid"
  }
]
```