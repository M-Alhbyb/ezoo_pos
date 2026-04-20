# Quick Start: Quick Fee Amount Buttons

**Feature**: 002-quick-fee-buttons  
**Date**: 2026-04-05  
**Time Estimate**: 2-3 days

## Overview

This guide helps developers quickly understand and implement the quick fee amount buttons feature. Follow these steps to get the feature up and running.

## Prerequisites

- Backend running on `localhost:8001`
- Frontend running on `localhost:3000`
- PostgreSQL database accessible
- Understanding of existing settings and fee modules

## Architecture Summary

```
POS Operator
  ↓ (clicks preset button)
FeeEditor Component
  ↓ (populates fee value)
Fee Value Input
  ↓ (on fee add)
Sale Transaction

Settings Manager (Manager role)
  ↓ (configures presets)
FeePresetManager Component
  ↓ (saves to backend)
Settings API
  ↓ (stores in DB)
PostgreSQL Settings Table
  ↓ (broadcast update)
WebSocket
  ↓ (notify connected clients)
FeeEditor Component
```

## Implementation Steps

### Phase 1: Backend API (Day 1)

#### Step1.1: Extend Settings Service

File: `backend/app/modules/settings/service.py`

```python
# Add these methods to SettingsService class

async def get_fee_presets(self, location_id: int) -> dict:
    """Get all fee presets for a location."""
    # Implementation details in data-model.md
    
async def upsert_fee_presets(
    self, 
    location_id: int, 
    fee_type: str, 
    presets: List[Decimal]
) -> dict:
    """Create or update fee presets for a fee type."""
    # Implementation details in data-model.md
```

#### Step 1.2: Define Pydantic Schemas

File: `backend/app/modules/settings/schemas.py`

```python
# Add these schemas (see data-model.md for full implementation)

class FeePresetsUpdate(BaseModel):
    location_id: int
    fee_type: FeeType
    presets: List[Decimal] = Field(..., max_length=8)
    # ... validators

class FeePresetsResponse(BaseModel):
    fee_type: FeeType
    presets: List[Decimal]

class FeePresetsListResponse(BaseModel):
    presets_by_fee_type: dict[FeeType, List[Decimal]]
```

#### Step 1.3: Add API Routes

File: `backend/app/modules/settings/routes.py`

```python
# Add these endpoints

@router.get("/fee-presets", response_model=FeePresetsListResponse)
async def get_fee_presets(location_id: int):
    """Get all fee presets for a location."""
    # See contracts/api.md for full implementation

@router.post("/fee-presets", response_model=FeePresetsResponse)
async def upsert_fee_presets(request: FeePresetsUpdate):
    """Create or update fee presets."""
    # See contracts/api.md for full implementation
```

#### Step 1.4: Test Backend

```bash
# Run backend tests
cd backend
pytest tests/integration/test_settings_api.py -v

# Manual test
curl -X POST http://localhost:8001/api/settings/fee-presets \
  -H "Content-Type: application/json" \
  -d '{"location_id": 1, "fee_type": "shipping", "presets": [10, 30, 50, 100]}'
```

### Phase 2: Frontend Components (Day 1-2)

#### Step 2.1: Add Presets State to FeeEditor

File: `frontend/components/pos/FeeEditor.tsx`

```typescript
// Add state for presets
const [feePresets, setFeePresets] = useState<FeePresetsConfig>({});
const [loadingPresets, setLoadingPresets] = useState(true);

// Fetch presets on mount
useEffect(() => {
  async function loadPresets() {
    try {
      const response = await fetch('/api/settings/fee-presets?location_id=1');
      const data = await response.json();
      setFeePresets(data.presets_by_fee_type);
    } catch (error) {
      console.error('Failed to load presets:', error);
    } finally {
      setLoadingPresets(false);
    }
  }
  loadPresets();
}, []);

// WebSocket listener for preset updates
useEffect(() => {
  const socket = getWebSocketConnection();
  socket.on('preset-updated', (data) => {
    setFeePresets(prev => ({
      ...prev,
      [data.fee_type]: data.presets
    }));
  });
  return () => socket.off('preset-updated');
}, []);
```

#### Step 2.2: Create Preset Buttons Component

File: `frontend/components/pos/FeeEditor.tsx`

```typescript
// Add inside FeeEditor component, before the value input

{!loadingPresets && feePresets[newFee.fee_type]?.length > 0 && (
  <div className="mb-2">
    <label className="block text-sm font-medium text-gray-700 mb-1">
      Quick Amounts
    </label>
    <div className="flex flex-wrap gap-2">
      {feePresets[newFee.fee_type].map((amount) => (
        <button
          key={amount}
          type="button"
          onClick={() => setNewFee({ ...newFee, fee_value: amount })}
          className="px-3 py-1.5 rounded-lg text-sm font-medium bg-slate-100 
                     hover:bg-slate-200 text-slate-700 transition-colors"
        >
          {amount}
        </button>
      ))}
    </div>
  </div>
)}

{!loadingPresets && (!feePresets[newFee.fee_type] || feePresets[newFee.fee_type].length === 0) && (
  <div className="text-sm text-gray-500 italic mb-2">
    Configure presets in settings
  </div>
)}
```

#### Step 2.3: Create FeePresetManager Component

File: `frontend/components/settings/FeePresetManager.tsx`

```typescript
// New component for settings page
// See full implementation in contracts/api.md
// Allows managers to configure presets per fee type per location
```

#### Step 2.4: Integrate into Settings Page

File: `frontend/app/settings/page.tsx`

```typescript
// Import and render FeePresetManager
import FeePresetManager from '@/components/settings/FeePresetManager';

// Inside settings page JSX
<FeePresetManager locationId={currentLocationId} />
```

### Phase 3: Testing & Polish (Day 2-3)

#### Step 3.1: Add Integration Tests

File: `backend/tests/integration/test_settings_api.py`

```python
# Add tests for fee preset endpoints
# See contracts/api.md for test checklist

async def test_get_fee_presets():
    """Test retrieving fee presets."""
    
async def test_upsert_fee_presets():
    """Test creating/updating fee presets."""
    
async def test_preset_validation():
    """Test preset validation rules."""
```

#### Step 3.2: Add E2E Tests

Run manual E2E tests:
1. Manager configures presets in settings
2. POS operator sees updated presets
3. Preset button populates fee value
4. Validation errors display correctly

#### Step 3.3: Performance Check

- Verify preset loading < 200ms (SC-005)
- Check WebSocket broadcast latency
- Test with maximum 8 presets

## Key Files to Modify

### Backend (New/Modified)
- `backend/app/modules/settings/service.py` - Add preset methods
- `backend/app/modules/settings/routes.py` - Add preset endpoints
- `backend/app/modules/settings/schemas.py` - Add preset schemas
- `backend/tests/integration/test_settings_api.py` - Add preset tests

### Frontend (New/Modified)
- `frontend/components/pos/FeeEditor.tsx` - Add preset buttons (MODIFIED)
- `frontend/components/settings/FeePresetManager.tsx` - New config UI (NEW)
- `frontend/app/settings/page.tsx` - Integrate preset manager (MODIFIED)

### Database
- No migrations required
- Optional: Add seed migration for default presets

## Common Patterns to Follow

### Pattern 1: Settings Key Format

```python
key = f"fee_presets_{location_id}_{fee_type}"
value = json.dumps([10, 30, 50, 100])
```

### Pattern 2: Preset Validation

```python
# Always validate and normalize
presets = sorted(set(presets))  # Deduplicate and sort
if len(presets) > 8:
    raise ValueError("Maximum 8 presets allowed")
if any(p < 0 for p in presets):
    raise ValueError("Presets must be non-negative")
```

### Pattern 3: WebSocket Broadcast

```python
# Broadcast update to connected clients
await broadcast({
    "event": "preset-updated",
    "data": {
        "fee_type": fee_type,
        "location_id": location_id,
        "presets": presets
    }
})
```

## Testing Checklist

Run these tests before considering the feature complete:

- [ ] Backend: GET `/api/settings/fee-presets` returns correct data
- [ ] Backend: POST `/api/settings/fee-presets` validates input
- [ ] Backend: POST rejects > 8 presets
- [ ] Backend: POST rejects negative values
- [ ] Backend: Presets are sorted and deduplicated
- [ ] Frontend: Preset buttons appear for configured fee types
- [ ] Frontend: Clicking preset populates fee value
- [ ] Frontend: Placeholder shown when no presets configured
- [ ] Frontend: Settings UI allows preset configuration
- [ ] Frontend: Role-based access prevents non-managers from configuring
- [ ] WebSocket: Preset updates broadcast to POS clients
- [ ] Performance: Presets load within 200ms

## Troubleshooting

### Issue: Presets not loading

**Check**:
1. Backend API is running on port 8001
2. Database has settings table with fee_preset keys
3. Network request reaches `/api/settings/fee-presets`

**Fix**: Verify backend logs for errors

### Issue: Preset buttons not appearing

**Check**:
1. `feePresets` state is populated
2. `newFee.fee_type` matches preset keys
3. Component is mounted

**Fix**: Add console.log to see fetched data

### Issue: Presets not persisting

**Check**:
1. User has manager role
2. POST request sends correct payload
3. Backend validationpasses

**Fix**: Check backend response for errors

## Next Steps After Implementation

1. Run full test suite
2. Manual QA on staging environment
3. Update documentation
4. Deploy to production
5. Monitor for errors via logs

## References

- Specification: `specs/002-quick-fee-buttons/spec.md`
- Data Model: `specs/002-quick-fee-buttons/data-model.md`
- API Contract: `specs/002-quick-fee-buttons/contracts/api.md`
- Research: `specs/002-quick-fee-buttons/research.md`

## Questions?

Refer to the main specification document or reach out to the team for clarification on requirements or implementation details.