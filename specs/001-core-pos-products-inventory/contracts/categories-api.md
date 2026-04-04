# Categories API Contract

**Version**: 1.0
**Feature**: 001-core-pos-products-inventory (Phase 0 Foundation)
**Base Path**: `/api/categories`

## Overview

Category management API for organizing products. This is part of the Phase 0 foundation but documented here for completeness.

## Endpoints

### 1. Create Category

**POST** `/api/categories`

Creates a new product category.

**Request Body**:
```json
{
  "name": "Solar Panels"
}
```

**Request Schema**:
- `name`: required, string (1-100 chars), must be unique

**Response** `201 Created`:
```json
{
  "id": "uuid",
  "name": "Solar Panels",
  "created_at": "2026-04-04T12:00:00Z",
  "updated_at": "2026-04-04T12:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error
- `409 Conflict`: Duplicate category name

---

###2. List Categories

**GET** `/api/categories`

Retrieves all categories.

**Response** `200 OK`:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Solar Panels",
      "product_count": 15,
      "created_at": "2026-04-04T12:00:00Z",
      "updated_at": "2026-04-04T12:00:00Z"
    }
  ]
}
```

**Field: `product_count`**:
- Number of active products in the category
- Useful for UI display (e.g., "Solar Panels (15)")

---

### 3. Update Category

**PUT** `/api/categories/{id}`

Updates category name.

**Path Parameters**:
- `id`: Category UUID

**Request Body**:
```json
{
  "name": "Solar Panels & Inverters"
}
```

**Response** `200 OK`:
```json
{
  "id": "uuid",
  "name": "Solar Panels & Inverters",
  "created_at": "2026-04-04T12:00:00Z",
  "updated_at": "2026-04-04T13:00:00Z"
}
```

**Error Responses**:
- `400 Bad Request`: Validation error
- `404 Not Found`: Category not found
- `409 Conflict`: Duplicate category name

---

### 4. Delete Category

**DELETE** `/api/categories/{id}`

Deletes a category. Only allowed if no active products reference it.

**Path Parameters**:
- `id`: Category UUID

**Response** `200 OK`:
```json
{
  "message": "Category deleted successfully"
}
```

**Error Responses**:
- `404 Not Found`: Category not found
- `409 Conflict`: Category has active products
  ```json
  {
    "error": {
      "code": "CATEGORY_HAS_PRODUCTS",
      "message": "Cannot delete category with active products",
      "details": {
        "category_name": "Solar Panels",
        "product_count": 15
      }
    }
  }
  ```

---

## Data Types

### Category Response

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique identifier |
| `name` | String(100) | Category name |
| `product_count` | Integer | Number of active products (computed) |
| `created_at` | Timestamp | Creation datetime |
| `updated_at` | Timestamp | Last update datetime |

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
- `NOT_FOUND`: Category not found
- `CONFLICT`: Duplicate name or category has products
- `INTERNAL_ERROR`: Server error

---

## Constitution Compliance

| Principle | Implementation |
|-----------|----------------|
| **VI. Data Integrity** | Foreign key constraint prevents deleting categories with products |
| **VII. Backend Authority** | All validation in backend |
| **VIII. Input Validation** | Pydantic schemas validate all inputs |

---

## Implementation Notes

- Categories endpoint created in Phase 0
- Used by Products module for filtering and organization
- Category deletion blocked by database FK constraint (ON DELETE RESTRICT)

---

## Next Steps

1. Category endpoints should already exist from Phase 0
2. Verify FK constraint on products.category_id
3. Add product_count computed field to list endpoint