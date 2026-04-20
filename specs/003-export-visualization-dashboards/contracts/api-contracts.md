# API Contracts: Export Formats and Visualization Dashboards

**Date**: 2026-04-05  
**Feature**: 003-export-visualization-dashboards  
**Version**: 1.0.0

## Overview

This document defines the RESTful API contracts for the export and dashboard endpoints. All endpoints extend the existing EZOO POS API structure and follow FastAPI conventions.

---

## Authentication

All endpoints require authentication via JWT bearer token:

```
Authorization: Bearer <jwt_token>
```

Rate limiting applies to export endpoints for large requests (>5,000 rows).

---

## Export Endpoints

### Base Path: `/api/reports`

All export endpoints extend the existing reports API.

---

### Export Sales Report

**Endpoint**: `GET /api/reports/sales/export`

**Description**: Export sales report in CSV, XLSX, or PDF format for a specified date range.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `format` | string | Yes | Export format | Enum: `csv`, `xlsx`, `pdf` |
| `start_date` | string | Yes | Start date (inclusive) | ISO 8601 date (YYYY-MM-DD) |
| `end_date` | string | Yes | End date (inclusive) | ISO 8601 date (YYYY-MM-DD), must be >= start_date |

**Row Limits**:
- CSV: Maximum 100,000 rows
- XLSX: Maximum 50,000 rows
- PDF: Maximum 10,000 rows

**Rate Limiting**: 10 requests/hour for requests >5,000 rows

**Success Response**:

- **Status**: `200 OK`
- **Headers**:
  ```
  Content-Type: text/csv | application/vnd.openxmlformats-officedocument.spreadsheetml.sheet | application/pdf
  Content-Disposition: attachment; filename="sales_{start_date}_{end_date}.{format}"
  ```
- **Body**: File stream

**Error Responses**:

**400 Bad Request - Row Limit Exceeded**:
```json
{
  "error_type": "row_limit_exceeded",
  "message": "Requested dataset exceeds maximum rows for PDF format",
  "details": {
    "format": "pdf",
    "requested_rows": 15000,
    "max_allowed": 10000,
    "suggestion": "Reduce date range or choose CSV/XLSX format"
  }
}
```

**429 Too Many Requests - Rate Limit Exceeded**:
```json
{
  "error_type": "rate_limit_exceeded",
  "message": "Rate limit exceeded for large exports",
  "retry_after": 3600
}
```

**400 Bad Request - Invalid Date Range**:
```json
{
  "error_type": "invalid_date_range",
  "message": "end_date must be on or after start_date",
  "details": {
    "start_date": "2026-03-31",
    "end_date": "2026-01-01"
  }
}
```

**404 Not Found - No Data**:
```json
{
  "error_type": "no_data_available",
  "message": "No sales data found for the specified date range",
  "details": {
    "start_date": "2020-01-01",
    "end_date": "2020-01-31"
  }
}
```

**Example Request**:
```bash
curl -X GET "https://api.ezoopos.com/api/reports/sales/export?format=csv&start_date=2026-01-01&end_date=2026-03-31" \
  -H "Authorization: Bearer <token>" \
  -o sales_report.csv
```

---

### Export Projects Report

**Endpoint**: `GET /api/reports/projects/export`

**Description**: Export completed projects report in CSV, XLSX, or PDF format.

**Authentication**: Required

**Query Parameters**: Same as sales export (format, start_date, end_date)

**Row Limits**: Same as sales export

**Success Response**: Same structure as sales export, with project-specific data

**Columns**:
- Project ID
- Project Name
- Start Date
- End Date
- Total Cost (DECIMAL)
- Selling Price (DECIMAL)
- Profit (DECIMAL)
- Profit Margin (%)

**Error Responses**: Same as sales export

---

### Export Partners Report

**Endpoint**: `GET /api/reports/partners/export`

**Description**: Export partner dividend distribution report in CSV, XLSX, or PDF format.

**Authentication**: Required

**Query Parameters**: Same as sales export (format, start_date, end_date)

**Row Limits**: Same as sales export

**Success Response**: Same structure as sales export, with partner-specific data

**Columns**:
- Partner ID
- Partner Name
- Invested Amount (DECIMAL)
- Profit Percentage (%)
- Distributed Amount (DECIMAL)
- Distribution Date

**Error Responses**: Same as sales export

---

### Export Inventory Report

**Endpoint**: `GET /api/reports/inventory/export`

**Description**: Export inventory movements report in CSV, XLSX, or PDF format.

**Authentication**: Required

**Query Parameters**: Same as sales export (format, start_date, end_date)

**Row Limits**: Same as sales export

**Success Response**: Same structure as sales export, with inventory-specific data

**Columns**:
- Movement ID
- Product ID
- Product Name
- Movement Type (sale/restock/reversal)
- Quantity Delta
- Reason
- Timestamp

**Error Responses**: Same as sales export

---

## Dashboard Endpoints

### Base Path: `/api/dashboard`

All dashboard endpoints return aggregated chart data for frontend rendering.

---

### Get Sales Dashboard Data

**Endpoint**: `GET /api/dashboard/sales`

**Description**: Retrieve aggregated sales data for line chart visualization showing daily revenue, profit, and VAT trends.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `start_date` | string | Yes | Start date (inclusive) | ISO 8601 date (YYYY-MM-DD) |
| `end_date` | string | Yes | End date (inclusive) | ISO 8601 date (YYYY-MM-DD), must be >= start_date |

**Data Point Limit**: Maximum 1,000 data points per request

**Success Response**:

- **Status**: `200 OK`
- **Body**:
```json
{
  "success": true,
  "data": {
    "dates": ["2026-01-01", "2026-01-02", ...],
    "revenue": [1250.50, 1380.75, ...],
    "profit": [450.25, 520.60, ...],
    "vat": [125.05, 138.08, ...]
  },
  "total_points": 90,
  "filter_applied": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31"
  }
}
```

**Error Responses**:

**400 Bad Request - Date Range Too Large**:
```json
{
  "success": false,
  "error": "Requested date range would result in more than 1000 data points",
  "data": null,
  "total_points": null,
  "filter_applied": null
}
```

**400 Bad Request - Invalid Date Range**:
```json
{
  "success": false,
  "error": "end_date must be on or after start_date",
  "data": null,
  "total_points": null,
  "filter_applied": null
}
```

**Example Request**:
```bash
curl -X GET "https://api.ezoopos.com/api/dashboard/sales?start_date=2026-01-01&end_date=2026-03-31" \
  -H "Authorization: Bearer <token>"
```

---

### Get Projects Dashboard Data

**Endpoint**: `GET /api/dashboard/projects`

**Description**: Retrieve aggregated project profit data for bar chart visualization.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `start_date` | string | Yes | Start date (inclusive) | ISO 8601 date (YYYY-MM-DD) |
| `end_date` | string | Yes | End date (inclusive) | ISO 8601 date (YYYY-MM-DD) |
| `project_id` | integer | No | Filter by specific project ID | Must exist in database |

**Data Point Limit**: Maximum 1,000 projects per request

**Success Response**:

- **Status**: `200 OK`
- **Body**:
```json
{
  "success": true,
  "data": {
    "project_names": ["Project Alpha", "Project Beta", ...],
    "profits": [15000.50, 12800.75, ...],
    "profit_margins": [25.5, 32.1, ...],
    "project_ids": [1, 2, ...]
  },
  "total_points": 15,
  "filter_applied": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31",
    "project_id": null
  }
}
```

**Error Responses**: Same as sales dashboard

---

### Get Partners Dashboard Data

**Endpoint**: `GET /api/dashboard/partners`

**Description**: Retrieve aggregated partner dividend data for pie chart visualization.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `start_date` | string | Yes | Start date (inclusive) | ISO 8601 date (YYYY-MM-DD) |
| `end_date` | string | Yes | End date (inclusive) | ISO 8601 date (YYYY-MM-DD) |
| `partner_id` | integer | No | Filter by specific partner ID | Must exist in database |

**Data Point Limit**: Maximum 1,000 partners per request

**Success Response**:

- **Status**: `200 OK`
- **Body**:
```json
{
  "success": true,
  "data": {
    "partner_names": ["Partner A", "Partner B", ...],
    "dividend_amounts": [7500.25, 5200.75, ...],
    "percentages": [35.5, 24.7, ...],
    "partner_ids": [1, 2, ...]
  },
  "total_points": 8,
  "filter_applied": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31",
    "partner_id": null
  }
}
```

**Error Responses**: Same as sales dashboard

---

### Get Inventory Dashboard Data

**Endpoint**: `GET /api/dashboard/inventory`

**Description**: Retrieve aggregated inventory movement data for stacked bar chart visualization.

**Authentication**: Required

**Query Parameters**:

| Parameter | Type | Required | Description | Constraints |
|-----------|------|----------|-------------|-------------|
| `start_date` | string | Yes | Start date (inclusive) | ISO 8601 date (YYYY-MM-DD) |
| `end_date` | string | Yes | End date (inclusive) | ISO 8601 date (YYYY-MM-DD) |

**Data Point Limit**: Maximum 1,000 data points per request

**Success Response**:

- **Status**: `200 OK`
- **Body**:
```json
{
  "success": true,
  "data": {
    "dates": ["2026-01-01", "2026-01-02", ...],
    "sales": [150, 125, ...],
    "restocks": [200, 180, ...],
    "reversals": [5, 3, ...]
  },
  "total_points": 90,
  "filter_applied": {
    "start_date": "2026-01-01",
    "end_date": "2026-03-31"
  }
}
```

**Error Responses**: Same as sales dashboard

---

## Progress WebSocket Messages

### Export Progress Updates

**WebSocket Endpoint**: Existing WebSocket connection (same as POS real-time updates)

**Message Type**: `export_progress`

**Direction**: Server → Client

**Message Structure**:
```json
{
  "type": "export_progress",
  "data": {
    "export_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "processing",
    "progress": 50,
    "stage": "generating"
  }
}
```

**Status Values**:
- `started`: Export request received
- `validating`: Checking parameters
- `processing`: Generating file
- `completed`: File ready for download
- `failed`: Error during generation

---

### Export Cancellation

**WebSocket Message Type**: `export_cancel`

**Direction**: Client → Server

**Message Structure**:
```json
{
  "type": "export_cancel",
  "data": {
    "export_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

**Server Response**:
```json
{
  "type": "export_cancelled",
  "data": {
    "export_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "cancelled"
  }
}
```

---

## Error Handling

### Standard Error Response Format

All error responses follow this structure:

```json
{
  "error_type": "string",
  "message": "string",
  "details": {
    // Additional context (optional)
  }
}
```

### Common Error Codes

| HTTP Status | Error Type | Description |
|-------------|-----------|-------------|
| 400 | `row_limit_exceeded` | Requested dataset exceeds format-specific row limit |
| 400 | `invalid_date_range` | Start date > end date or other validation failure |
| 400 | `data_point_limit_exceeded` | Dashboard query would return >1000 points |
| 404 | `no_data_available` | No data found for specified date range |
| 429 | `rate_limit_exceeded` | Too many large export requests |
| 500 | `generation_failed` | Unexpected error during file generation |

---

## OpenAPI Specification

Full OpenAPI 3.0.3 specification available at:

- **Export Endpoints**: `/api/docs#tag/exports`
- **Dashboard Endpoints**: `/api/docs#tag/dashboards`

Interactive documentation available at `/api/docs` (FastAPI Swagger UI).

---

## Testing Contracts

### Contract Tests

**Location**: `tests/contract/test_export_api_contract.py`

**Coverage**:
- Request schema validation
- Row limit enforcement
- Rate limit enforcement
- Response schema validation
- Error response formats

**Example Contract Test**:
```python
def test_export_sales_csv_contract():
    """Verify CSV export response matches contract"""
    response = client.get(
        "/api/reports/sales/export?format=csv&start_date=2026-01-01&end_date=2026-01-31",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "text/csv"
    assert "Content-Disposition" in response.headers
    assert "attachment" in response.headers["Content-Disposition"]
    
    # Validate CSV structure
    lines = response.text.split("\n")
    assert len(lines) > 1  # Header + data
    assert "date,subtotal,fees_total,vat,total,profit" in lines[0].lower()
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-05 | Initial API contracts for export and dashboard endpoints |

---

## Next Steps

1. ✅ Contracts defined for all new endpoints
2. → Implement Pydantic schemas based on contracts
3. → Implement FastAPI route handlers
4. → Write contract tests
5. → Document in FastAPI Swagger UI