# Research: Quick Fee Amount Buttons

**Date**: 2026-04-05  
**Feature**: 002-quick-fee-buttons

## Overview

This document captures the research findings for implementing configurable quick-amount preset buttons for fee entry in the POS interface.

## Research Questions

### Q1: How are existing fee presets stored and managed in the system?

**Context**: The feature requires storing configurable preset amounts per fee type per location. Need to understand the current settings architecture.

**Findings**:

1. **SettingsTable Structure** (from `backend/app/models/settings.py`):
   - Simple key-value storage: `key` (String,unique), `value` (String), `description` (String, nullable)
   - Already used for system-wide settings like VAT configuration

2. **Existing Pattern - Payment Methods**:
   - Payment methods are NOT stored in the settings table
   - They have a dedicated `payment_methods` table with structured fields
   - This is because payment methods are entities with multiple attributes (name, is_active, etc.)

3. **Decision**: Store fee presets in the existing `settings` table using composite keys
   - Key format: `fee_presets_{location_id}_{fee_type}` (e.g., `fee_presets_1_shipping`)
   - Value format: JSON array of amounts (e.g., `[10, 30, 50, 100]`)
   - Rationale: Presets are configuration, not entities; JSON array is sufficient for storing simple numeric values
   - Alternative rejected: Creating a dedicated `fee_presets` table would add unnecessary complexity for a simple configuration feature

**Code Evidence**:
```python
# backend/app/models/settings.py:15-51
class Settings(BaseModel):
    __tablename__ = "settings"
    key = Column(String(100), nullable=False, unique=True, index=True)
    value = Column(String, nullable=False)
    description = Column(String, nullable=True)
```

### Q2: How is the FeeEditor component structured and where should preset buttons be added?

**Context**: Need to understand the current UI layout to integrate quick-amount buttons seamlessly.

**Findings**:

1. **Current FeeEditor Structure** (from `frontend/components/pos/FeeEditor.tsx`):
   - Props: `fees` array, `onFeesChange` callback
   - State: `newFee` object (type, label, value_type, value)
   - Fee types defined as constant: shipping, installation, custom
   - UI: Dropdown for fee type, radio buttons for fixed/percent, number input for value

2. **UI Integration Point**:
   - Add preset buttons above or beside the value input field
   - Group buttons by fee type (show shipping presets when shipping is selected, etc.)
   - Pattern借鉴: ProductGrid.tsx uses category tab buttons with consistent styling

3. **Decision**: Add preset button group before the value input field
   - Rationale: Visual hierarchy places quick actions before manual input
   - Buttons should be horizontally laid out with consistent spacing
   - Show placeholder "Configure presets in settings" when no presets exist for selected fee type

**Code Pattern** (from `frontend/components/pos/ProductGrid.tsx:109-131`):
```tsx
<button 
  className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all`}
>
  All Items
</button>
```

### Q3: How should presets be validated and constrained?

**Context**: Requirements specify max 8 presets, positive values only, ordering.

**Findings**:

1. **Backend Validation** (Pydantic in `backend/app/modules/settings/schemas.py`):
   - Create new schema: `FeePresetUpdate(BaseModel)`
   - Fields: `fee_type`, `presets` (list of Decimal)
   - Validators: 
     - `len(presets) <= 8` (max limit)
     - `all(p >= 0 for p in presets)` (no negative values)
     - Automatic sorting on save: `sorted(set(presets))` (deduplicate and order)

2. **Frontend Validation**:
   - Display validation errors from backend
   - Prevent form submission ifvalidation fails
   - Optimistic UI: Sort presets immediately after user input

3. **Decision**: Validate on both frontend (UX) and backend (security)
   - Frontend: Immediate feedback, sort on blur
   - Backend: Authoritative validation per constitution principle VII
   - Sorting: Store sorted in database, display sorted in UI

### Q4: How should role-based access control be implemented for preset configuration?

**Context**: Only users with Manager role or higher should configure presets.

**Findings**:

1. **Current Auth Status**: No authentication/authorization system detected in codebase exploration
   - No user management module
   - No role-based access control (RBAC) implementation
   - Single-user system per constitution principle IX

2. **Decision**: Implement role checking as a placeholder for future RBAC
   - Add `user_role` field to settings API endpoint (passed from frontend context)
   - Backend validates `user_role in ["manager", "admin", "owner"]`
   - Frontend checks local storage or session for user role
   - If role system not implemented yet, default to allowing configuration (single-user system)

**Rationale**: Constitution principle IX states "Schema design MUST anticipate multi-user support (user ID foreign keys, even if only one user exists today)". This placeholder allows future RBAC implementation without breaking current functionality.

### Q5: What is the data flow for preset retrieval and display?

**Context**: Need to ensure 200ms load time performance (SC-005).

**Findings**:

1. **API Flow**:
   - GET `/api/settings/fee-presets?location_id={id}&fee_type={type}`
   - Response: `{ "fee_type": "shipping", "presets": [10, 30, 50, 100] }`
   - Backend joins settings table, filters by key pattern

2. **Caching Strategy**:
   - Frontend: Store presets in React state, fetched on FeeEditor mount
   - No need for aggressive caching (settings change infrequently)
   - WebSocket updates: Broadcast preset changes to connected POS terminals (similar to product updates pattern)

3. **Decision**: Fetch presets on component mount, cache in component state
   - 200ms goal achievable with simple database query
   - invalidate cache on settings update via WebSocket broadcast

## Technology Decisions Summary

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Storage | Settings table with JSON values | Simple configuration, follows existing pattern |
| Key Format | `fee_presets_{location_id}_{fee_type}` | Hierarchical, supports multi-location |
| UI Pattern | Horizontal button group before value input | Visual hierarchy, matches ProductGrid pattern |
| Validation | Pydantic schema + frontend UI | Backend authoritative per constitution VII |
| Sorting | Automatic on save and display | Consistent UX, required by FR-009 |
| Role Check | Placeholder for future RBAC | Constitution IX compliance, future-proof |
| Data Flow | REST API + WebSocket broadcast | Consistent with existing real-time updates |

## Alternatives Considered

### Alternative 1: Dedicated `fee_presets` table
- **Why Rejected**: Overkill for simple numeric configuration
- **Complexity**: Would require migration, foreign keys, JOINs for simple feature
- **Settings table advantage**: Already exists, minimal overhead

### Alternative 2: Store presets per user
- **Why Rejected**: Constitution explicitly states presets are per location, not per user
- **Clarification**: FR-003 specifies administrators configure for business/location

### Alternative 3: Client-side only configuration
- **Why Rejected**: Violates constitution principle II (Single Source of Truth)
- **Requirement**: Presets must persist across sessions and users

## Dependencies

1. **Backend**:
   - Settings module_extension (new routes, service methods, schemas)
   - No new database migrations needed

2. **Frontend**:
   - FeeEditor component extension
   - New FeePresetManager component for settings page
   - WebSocket integration for real-time updates

3. **Testing**:
   - Integration tests for preset API endpoints
   - Unit tests for validation logic
   - E2E tests for preset button functionality

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Large preset arrays (user tries to save > 8) | Backend validation rejects, frontend shows error |
| Negative values | Backend validation rejects, frontend shows error |
| Invalid fee type | Backend validates against FeeType enum |
| Presets not loaded within 200ms | Index on settings.key, optimize query |
| Concurrent configuration edits | Last-write-wins acceptable (single-user system) |

## Next Steps

1. Create data-model.md defining preset configuration entity
2. Define API contracts in contracts/api.md
3. Update agent context with new technology decisions
4. Proceed to task decomposition_PHASE