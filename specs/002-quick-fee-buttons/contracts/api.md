# API Contract: Fee Presets

**Feature**: 002-quick-fee-buttons  
**Date**: 2026-4-05  
**Version**: 1.0

## Overview

This contract defines the REST API endpoints for managing fee preset configurations. Presets are stored in the existing settings table and accessed via dedicated endpoints.

##Base URL

```
/api/settings
```

## Authentication

All endpoints require authentication. Role-based access control:
- **Read Access**: All authenticated operators
- **Write Access**: Users with `manager` role or higher

## Endpoints

### GET /api/settings/fee-presets

Retrieve all fee presets for a location.

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| location_id | integer | Yes | Store location ID |

**Headers**:
```
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "presets_by_fee_type": {
    "shipping": [10, 30, 50, 100],
    "installation": [10, 30, 50, 100],
    "custom": [10, 30, 50, 100]
  }
}
```

**Response Schema**:
```typescript
interface FeePresetsListResponse {
  presets_by_fee_type: {
    [fee_type: string]: number[];
  };
}
```

**Error Responses**:
- `400 Bad Request`: Missing `location_id` parameter
- `401 Unauthorized`: Invalid or missing authentication token
- `500 Internal Server Error`: Database error

**Example Request**:
```http
GET /api/settings/fee-presets?location_id=1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Performance**: Returns within 200ms (per SC-005)

---

### POST /api/settings/fee-presets

Create or update fee presets for a specific fee type at a location.

**Headers**:
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body**:
```json
{
  "location_id": 1,
  "fee_type": "shipping",
  "presets": [10, 30, 50, 100]
}
```

**Request Schema**:
```typescript
interface FeePresetsUpdate {
  location_id: number;
  fee_type: "shipping" | "installation" | "custom";
  presets: number[]; // Max 8 values, all >= 0
}
```

**Response** (200 OK):
```json
{
  "fee_type": "shipping",
  "presets": [10, 30, 50, 100]
}
```

**Response Schema**:
```typescript
interface FeePresetsResponse {
  fee_type: string;
  presets: number[];
}
```

**Validation**:
- `presets` array length ≤ 8
- All values ≥ 0
- Values are automatically deduplicated and sorted
- `fee_type` must be valid enum value

**Error Responses**:
- `400 Bad Request`: Validation error (withdetails)
  ```json
  {
    "detail": "Preset amounts must be non-negative"
  }
  ```
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User lacks manager role
- `422 Unprocessable Entity`: Invalid fee_type value
- `500 Internal Server Error`: Database error

**Side Effects**:
- Updates `settings` table with new preset values
- Broadcasts WebSocket event `preset-updated` to connectedclients
- Sets `updated_at` timestamp

**Example Request**:
```http
POST /api/settings/fee-presets HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
Content-Type: application/json

{
  "location_id": 1,
  "fee_type": "shipping",
  "presets": [15, 25, 75]
}
```

---

### GET /api/settings/fee-presets/{fee_type}

Retrieve presets for a specific fee type at a location.

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| fee_type | string | Yes | One of: `shipping`, `installation`, `custom` |

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| location_id | integer | Yes | Store location ID |

**Headers**:
```
Authorization: Bearer {token}
```

**Response** (200 OK):
```json
{
  "fee_type": "shipping",
  "presets": [10, 30, 50, 100]
}
```

**Response Schema**:
```typescript
interface FeePresetsResponse {
  fee_type: string;
  presets: number[];
}
```

**Error Responses**:
- `400 Bad Request`: Missing `location_id` parameter
- `401 Unauthorized`: Invalid or missing authentication token
- `404 Not Found`: No presets configured for this fee type/location
- `422 Unprocessable Entity`: Invalid `fee_type` value
- `500 Internal Server Error`: Database error

**Example Request**:
```http
GET /api/settings/fee-presets/shipping?location_id=1 HTTP/1.1
Host: localhost:8000
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

---

### DELETE /api/settings/fee-presets/{fee_type}

Remove all presets for a specific fee type at a location.

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| fee_type | string | Yes | One of: `shipping`, `installation`, `custom` |

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| location_id | integer | Yes | Store location ID |

**Headers**:
```
Authorization: Bearer {token}
```

**Response** (204 No Content):
Empty body

**Error Responses**:
- `400 Bad Request`: Missing `location_id` parameter
- `401 Unauthorized`: Invalid or missing authentication token
- `403 Forbidden`: User lacks manager role
- `404 Not Found`: No presets configured for this fee type/location
- `422 Unprocessable Entity`: Invalid `fee_type` value
- `500 Internal Server Error`: Database error

**Side Effects**:
- Removes preset entry from `settings` table
- Broadcasts WebSocket event `preset-deleted` to connected clients

---

## WebSocket Events

### Event: `preset-updated`

Broadcast when presets are created or modified.

**Payload**:
```json
{
  "event": "preset-updated",
  "data": {
    "fee_type": "shipping",
    "location_id": 1,
    "presets": [10, 30, 50, 100]
  }
}
```

**Client Action**: Invalidate cached presets and re-fetch

---

### Event: `preset-deleted`

Broadcast when presets are removed.

**Payload**:
```json
{
  "event": "preset-deleted",
  "data": {
    "fee_type": "shipping",
    "location_id": 1
  }
}
```

**Client Action**: Remove cached presets for this fee type

---

## Error Response Format

All error responses follow this structure:

```json
{
  "detail": "Human-readable error message"
}
```

For validation errors, additional context may be provided:

```json
{
  "detail": [
    {
      "loc": ["body", "presets"],
      "msg": "Preset amounts must be non-negative",
      "type": "value_error"
    }
  ]
}
```

---

## Rate Limiting

Not applicable (single-user system per constitution)

---

## Backward Compatibility

This API extends the existing settings module. No breaking changes to existing endpoints.

---

## Implementation Notes

### Backend Implementation

Located in: `backend/app/modules/settings/routes.py`

**Dependencies**:
- `FastAPI` for routing
- `Pydantic` for schema validation
- `SQLAlchemy async` for database operations
- `WebSocket manager` for broadcasting updates

**Database Operations**:
- Use `INSERT ... ON CONFLICT` for upsert (create or update)
- Query with `LIKE` pattern: `fee_presets_{location_id}_{fee_type}`
- Parse JSON value column to extract preset array

### Frontend Implementation

Located in: `frontend/components/pos/FeeEditor.tsx`

**Fetch Strategy**:
```typescript
// On component mount
useEffect(() => {
  fetchFeePresets(location_id);
}, [location_id]);

// WebSocket listener
useEffect(() => {
  socket.on('preset-updated', handlePresetUpdate);
  return () => socket.off('preset-updated');
}, []);
```

**Error Handling**:
- Display inline error messages for validation failures
- Show retry button for network errors
- Fallback to empty presets if API unavailable (with warning)

---

## Testing Checklist

### Unit Tests
- [ ] Schema validation: max 8 presets constraint
- [ ] Schema validation: negative value rejection
- [ ] Schema validation: invalid fee_type rejection
- [ ] Preset deduplication and sorting
- [ ] Service layer: preset retrieval
- [ ] Service layer: preset upsert

### Integration Tests
- [ ] GET `/api/settings/fee-presets` returns correct data
- [ ] GET `/api/settings/fee-presets/{fee_type}` returns specific presets
- [ ] POST `/api/settings/fee-presets` creates new presets
- [ ] POST `/api/settings/fee-presets` updates existing presets
- [ ] POST `/api/settings/fee-presets` validates input
- [ ] POST `/api/settings/fee-presets` rejects unauthorized users
- [ ] DELETE `/api/settings/fee-presets/{fee_type}` removes presets
- [ ] WebSocket broadcast on preset update
- [ ] WebSocket broadcast on preset deletion

### End-to-End Tests
- [ ] Manager configures presets via settings UI
- [ ] POS operator sees updated presets immediately
- [ ] Preset buttons populate fee value field correctly
- [ ] Validation errors display appropriately in UI
- [ ] Role-based access control enforced