# Products API Contract

**Version**: 1.0
**Feature**: 001-core-pos-products-inventory
**Base Path**: `/api/products`

## Overview

Product catalog management API. Supports CRUD operations, search, and category-based filtering.

## Endpoints

### 1. Create Product

**POST** `/api/products`

Creates a new product in the catalog.

**Request Body**:
```json
{
  "name": "Panel X",
  "sku": "PNL-001",
  "category_id": "uuid",
  "base_price": 100.00,
  "selling_price": 150.00,
  "stock_quantity": 50
}
```

**Validation**:
- `name`: required, string,1-200 chars
- `sku`: optional, string, max 50 chars, must be unique if provided
- `category_id`: required, UUID, must reference existing category
- `base_price`: required, decimal ≥ 0
- `selling_price`: required, decimal ≥ `base_price`
- `stock_quantity`: optional, integer ≥ 0, defaults to 0

**Response** `201 Created`:
```json
{
  "id": "uuid",
  "name": "Panel X",
  "sku": "PNL-001",
  "category_id": "uuid",
  "category_name": "Solar Panels",
  "base_price": "100.00",
  "selling_price": "150.00",
  "stock_quantity": 50,
  "is_active": true,
  "created_at": "2026-04-04T12:00:00Z",
  "updated_at": "2026-04-04T12:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error (e.g., `selling_price < base_price`)
- `409 Conflict`: Duplicate SKU
- `404 Not Found`: Category not found

---

### 2. List Products

**GET** `/api/products`

Retrieves a paginated list of products with optional filters.

**Query Parameters**:
- `category_id` (optional): Filter by category UUID
- `search` (optional): Search by name (partial, case-insensitive) or SKU (exact match)
- `active_only` (optional): If true, only return active products (default: true)
- `page` (optional): Page number (default: 1)
- `page_size` (optional): Items per page (default: 50, max: 100)

**Response** `200 OK`:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Panel X",
      "sku": "PNL-001",
      "category_id": "uuid",
      "category_name": "Solar Panels",
      "base_price": "100.00",
      "selling_price": "150.00",
      "stock_quantity": 50,
      "is_active": true,
      "created_at": "2026-04-04T12:00:00Z",
      "updated_at": "2026-04-04T12:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 50
}
```

---

### 3. Get Product Detail

**GET** `/api/products/{id}`

Retrieves a single product by ID.

**Path Parameters**:
- `id`: Product UUID

**Response** `200 OK`:
```json
{
  "id": "uuid",
  "name": "Panel X",
  "sku": "PNL-001",
  "category_id": "uuid",
  "category_name": "Solar Panels",
  "base_price": "100.00",
  "selling_price": "150.00",
  "stock_quantity": 50,
  "is_active": true,
  "created_at": "2026-04-04T12:00:00Z",
  "updated_at": "2026-04-04T12:00:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Product not found

---

### 4. Update Product

**PUT** `/api/products/{id}`

Updates product details. Cannot update `stock_quantity` directly (use inventory endpoints).

**Path Parameters**:
- `id`: Product UUID

**Request Body**:
```json
{
  "name": "Panel X Updated",
  "sku": "PNL-001-NEW",
  "category_id": "uuid",
  "base_price": 120.00,
  "selling_price": 180.00
}
```

**Validation**:
- All fields optional
- If `sku` is provided, must be unique
- If both `base_price` and `selling_price` provided, must satisfy `selling_price ≥ base_price`

**Response** `200 OK`:
```json
{
  "id": "uuid",
  "name": "Panel X Updated",
  "sku": "PNL-001-NEW",
  "category_id": "uuid",
  "category_name": "Solar Panels",
  "base_price": "120.00",
  "selling_price": "180.00",
  "stock_quantity": 50,
  "is_active": true,
  "created_at": "2026-04-04T12:00:00Z",
  "updated_at": "2026-04-04T13:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error
- `404 Not Found`: Product not found
- `409 Conflict`: Duplicate SKU

---

### 5. Soft Delete Product

**DELETE** `/api/products/{id}`

Soft deletes a product (sets `is_active = false`). Hard deletion is not allowed for products referenced in sales.

**Path Parameters**:
- `id`: Product UUID

**Response** `200 OK`:
```json
{
  "message": "Product deactivated successfully"
}
```

**Error Responses**:
- `404 Not Found`: Product not found

**Business Logic**:
- If product is referenced in any sale: set `is_active = false` (FR-005)
- If product has no sales: hard delete is allowed (but API only performs soft delete for consistency)

---

### 6. Search Products by SKU

**GET** `/api/products/search/by-sku?sku={sku}`

Exact SKU lookup for fast product identification (e.g., barcode scanner).

**Query Parameters**:
- `sku` (required): SKU string

**Response** `200 OK`:
```json
{
  "id": "uuid",
  "name": "Panel X",
  "sku": "PNL-001",
  "category_name": "Solar Panels",
  "selling_price": "150.00",
  "stock_quantity": 50,
  "is_active": true
}
```

**Error Responses**:
- `404 Not Found`: SKU not found

---

## Data Types

### Product Response

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `name` | String(200) | Product name |
| `sku` | String(50) | Stock Keeping Unit (optional) |
| `category_id` | UUID | Foreign key to categories |
| `category_name` | String(100) | Category name (joined) |
| `base_price` | Decimal(12,2) | Cost to acquire |
| `selling_price` | Decimal(12,2) | Price to customers |
| `stock_quantity` | Integer | Current stock level |
| `is_active` | Boolean | Soft delete flag |
| `created_at` | Timestamp | Creation datetime |
| `updated_at` | Timestamp | Last update datetime |

---

## Error Handling

All errors follow this structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "selling_price must be greater than or equal to base_price",
    "details": {
      "field": "selling_price",
      "value": 50.00,
      "constraint": "selling_price >= base_price"
    }
  }
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Requestvalidation failed
- `NOT_FOUND`: Resource not found
- `CONFLICT`: Unique constraint violation
- `INTERNAL_ERROR`: Server error

---

## Constitution Compliance

| Principle | Implementation |
|-----------|----------------|
| **VI. Data Integrity** | All monetary values as Decimal; CHECK constraints in DB |
| **VII. Backend Authority** | All validation in backend (Pydantic + service layer) |
| **VIII. Input Validation** | Request schemas validate all inputs |
| **IX. Extensibility** | All tables have user_id, branch_id |

---

## Next Steps

1. Implement Pydantic schemas (request/response)
2. Create SQLAlchemy models
3. Build service layer with business logic
4. Implement FastAPI routes