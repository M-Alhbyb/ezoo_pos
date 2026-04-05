# Data Model: Quick Fee Amount Buttons

**Date**: 2026-04-05  
**Feature**: 002-quick-fee-buttons

## Overview

This feature uses the existing settings table to store configurable fee preset amounts. No new database tables or migrations are required.

## Entity: Fee Preset Configuration

**Storage**: Reuses existing `settings` table

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| key | String(100) | PRIMARY KEY, NOT NULL, UNIQUE | Composite key: `fee_presets_{location_id}_{fee_type}` |
| value | String | NOT NULL | JSON array of Decimal values: `[10, 30, 50]` |
| description | String | NULL | Human-readable description |
| created_at | DateTime | NOT NULL, AUTO | Record creation timestamp |
| updated_at | DateTime | NULL, AUTO-UPDATE | Last modification timestamp |

### Key Format Convention

```
fee_presets_{location_id}_{fee_type}
```

Examples:
- `fee_presets_1_shipping` - Shipping fee presets for location 1
- `fee_presets_1_installation` - Installation fee presets for location 1
- `fee_presets_2_custom` - Custom fee presets for location 2

### Value Format

JSON array of non-negative Decimal values, sorted in ascending order:

```json
[10, 30, 50, 100]
```

### Validation Rules

1. **Maximum Presets**: `len(presets) <= 8`
2. **Minimum Value**: `all(preset >= 0 for preset in presets)`
3. **Automatic Deduplication**: Remove duplicate values before storage
4. **Automatic Sorting**: Sort ascending before storage and display
5. **Fee Type Validation**: `fee_type in ["shipping", "installation", "custom"]`

### Default Values

On first system setup, seed default presets for each fee type per location:

```python
default_presets = {
    "shipping": [10, 30, 50, 100],
    "installation": [10, 30, 50, 100],
    "custom": [10, 30, 50, 100]
}
```

## Database Schema

### Existing Table: `settings`

No migrations required. The table already supports this usage pattern:

```sql
CREATE TABLE settings (
    key VARCHAR(100) PRIMARY KEY NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Indexes

Existing index on `key` column is sufficient for preset lookups:

```sql
CREATE INDEX idx_settings_key ON settings(key);
```

## Pydantic Schemas

### Backend Schemas (NEW)

Located in: `backend/app/modules/settings/schemas.py`

```python
from pydantic import BaseModel, Field, field_validator
from typing import List
from decimal import Decimal
from enum import Enum

class FeeType(str, Enum):
    SHIPPING = "shipping"
    INSTALLATION = "installation"
    CUSTOM = "custom"

class FeePresetsUpdate(BaseModel):
    location_id: int = Field(..., description="Store location ID")
    fee_type: FeeType = Field(..., description="Type of fee")
    presets: List[Decimal] = Field(
        ..., 
        description="Preset amounts",
        max_length=8
    )
    
    @field_validator('presets')
    @classmethod
    def validate_presets(cls, v: List[Decimal]) -> List[Decimal]:
        # Validate no negative values
        if any(p < 0 for p in v):
            raise ValueError('Preset amounts must be non-negative')
        
        # Deduplicate and sort
        unique_sorted = sorted(set(v))
        return unique_sorted

class FeePresetsResponse(BaseModel):
    fee_type: FeeType
    presets: List[Decimal]

class FeePresetsListResponse(BaseModel):
    presets_by_fee_type: dict[FeeType, List[Decimal]]
```

### Frontend Interface (NEW)

Located in: `frontend/components/pos/FeeEditor.tsx` (extended)

```typescript
interface FeePreset {
  fee_type: 'shipping' | 'installation' | 'custom';
  presets: number[];
}

interface FeePresetsConfig {
  [fee_type: string]: number[];
}
```

## State Management

### Backend State

**Storage Location**: `settings` table
**Access Pattern**: Read-heavy (POS displays frequently), write-light (configuration changes rarely)

**Caching**: None required at backend level (PostgreSQL query performance sufficient)

### Frontend State

**Storage**: React component state in `FeeEditor`

```typescript
const [feePresets, setFeePresets] = useState<FeePresetsConfig>({});
const [loadingPresets, setLoadingPresets] = useState<boolean>(false);
```

**Fetch Strategy**:
1. On FeeEditor mount, fetch presets for all fee types
2. Store in component state
3. Re-fetch on settings update (WebSocket broadcast)

## Data Flow

### Write Path (Configuration Update)

```
User (Manager role)
  → FeePresetManager component
  → POST /api/settings/fee-presets
  → Settings service (validation)
  → Settings table (upsert)
  → WebSocket broadcast (preset-updated)
  → All connected POS clients (invalidate cache, re-fetch)
```

### Read Path (POS Display)

```
FeeEditor component mount
  → GET /api/settings/fee-presets?location_id={id}
  → Settings service (query settings table)
  → Response: { presets_by_fee_type: {...} }
  → FeeEditor state (cache)
  → Render preset buttons
```

## Relationships

### Settings Table (Existing)

```
settings
  └── fee_presets_{location_id}_{fee_type}  (NEW usage pattern)
```

No foreign keys needed. Presets are configuration data, not relational entities.

### Integration with Existing Entities

```
FeePresets (settings table)
  ↓ (used by)
FeeEditor component
  ↓ (creates)
SaleFee model (existing)
```

The preset configuration is independent of sale transactions. Presets are templates; actual fees are stored in `sale_fees` table with calculated amounts.

## Migration Strategy

**No migrations required**.

The feature uses the existing `settings` table with a new key naming convention. Default presets will be seeded via Alembic data migration (separate from schema migrations).

### Seed Migration (NEW)

File: `backend/alembic/versions/XXXX_seed_default_fee_presets.py`

```python
def upgrade():
    # Seed default presets for each location
    # This will be implemented during task phase
    pass
```

## Performance Considerations

### Query Optimization

**Get Presets Query**:
```sql
SELECT key, value FROM settings 
WHERE key LIKE 'fee_presets_%';
```

Performance: 
- Index scan on `key` column
- Expected <10ms for single location
- Meets 200ms target (SC-005)

### Write Performance

**Upsert Preset**:
```sql
INSERT INTO settings (key, value, description, created_at)
VALUES ('fee_presets_1_shipping', '[10, 30, 50]', 'Shipping fee presets', NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = NOW();
```

Performance: <50ms for single preset update

## Security Considerations

### Access Control

1. **Read Access**: All authenticated POS operators
2. **Write Access**: Users with role `manager` or higher

Role checking is implemented at API endpoint level (backend routes).

### Input Validation

1. **Type Safety**: Pydantic schema validation ensures Decimal values
2. **Range Checks**: Backend rejects negative values
3. **Length Limits**: Backend enforces max 8 presets
4. **Fee Type Validation**: Backend validates against enum

## Audit Trail

All preset changes are logged via:
1. `created_at` timestamp on initial creation
2. `updated_at` timestamp on modifications
3. Future: Audit log table for compliance (out of scope for v1)

## Constitution Compliance

### Principle II: Single Source of Truth
✅ Presets stored only in PostgreSQL `settings` table

### Principle III: Explicit Over Implicit
✅ Presets are explicit configuration, stored with clear key format

### Principle VI: Data Integrity
✅ Validation ensures non-negative Decimal values
✅ Automatic sorting for consistency

### Principle VIII: Input Validation
✅ Pydantic schema validates all preset updates
✅ Structured error responses for invalid input

## Testing Strategy

### Unit Tests

1. **Schema Validation**:
   - Test max 8 presets constraint
   - Test negative value rejection
   - Test deduplication and sorting

2. **Service Layer**:
   - Test preset retrieval by location and fee type
   - Test preset upsert with validation

### Integration Tests

1. **API Endpoints**:
   - GET `/api/settings/fee-presets` returns correct data
   - POST `/api/settings/fee-presets` validates and stores
   - Role-based access control enforcement

2. **WebSocket Broadcasting**:
   - Preset update triggers broadcast
   - Connected clients receive update notification

### End-to-End Tests

1. **User Flow**:
   - Manager configures presets via settings UI
   - POS operator sees updated presets in FeeEditor
   - Preset buttons populate fee value field correctly