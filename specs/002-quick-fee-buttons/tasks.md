# Tasks: Quick Fee Amount Buttons

**Input**: Design documents from `/specs/002-quick-fee-buttons/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Not explicitly requested in specification, so test tasks are OPTIONAL. Tests are included for critical backend validation to ensure constitution compliance.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/app/`, `backend/tests/`
- **Frontend**: `frontend/components/`, `frontend/app/`

---

## Phase 1: Setup

**Purpose**: Initialize feature branch and verify existing infrastructure

- [X] T001 Create feature branch `002-quick-fee-buttons` from main
- [X] T002 [P] Pull latest changes and verify backend runs on localhost:8001
- [X] T003 [P] Pull latest changes and verify frontend runs on localhost:3000
- [X] T004 Verify PostgreSQL database is accessible and settings table exists

---

## Phase 2: Foundational (Backend API & Data Layer)

**Purpose**: Core backend infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T005 [P] Define FeePresetsUpdate Pydantic schema in backend/app/modules/settings/schemas.py (validates max 8 presets, non-negative values, deduplication, sorting)
- [X] T006 [P] Define FeePresetsResponse and FeePresetsListResponse Pydantic schemas in backend/app/modules/settings/schemas.py
- [X] T007 Implement get_fee_presets service method in backend/app/modules/settings/service.py (retrieves all presets for a location)
- [X] T008 Implement upsert_fee_presets service method in backend/app/modules/settings/service.py (creates/updates presets with validation)
- [X] T009 Implement delete_fee_presets service method in backend/app/modules/settings/service.py (optional, for clearing presets)
- [X] T010 Add GET /api/settings/fee-presets endpoint in backend/app/modules/settings/routes.py
- [X] T011 Add POST /api/settings/fee-presets endpoint in backend/app/modules/settings/routes.py (Manager role check placeholder)
- [X] T012 Add GET /api/settings/fee-presets/{fee_type} endpoint in backend/app/modules/settings/routes.py
- [X] T013 Add DELETE /api/settings/fee-presets/{fee_type} endpoint in backend/app/modules/settings/routes.py (Manager role check placeholder)
- [X] T014 [P] Write integration test for GET fee-presets endpoint in backend/tests/integration/test_settings_api.py
- [X] T015 [P] Write integration test for POST fee-presets endpoint withvalidation cases in backend/tests/integration/test_settings_api.py

**Checkpoint**: Backend API ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Apply Common Fee Amounts Quickly (Priority: P1) 🎯 MVP

**Goal**: POS operators can use quick-amount preset buttons to rapidly populate fee values instead of manual typing, reducing entry time from 5-8 seconds to under 2 seconds.

**Independent Test**: Add a fee in the POS interface using a quick-amount button and verify the correct amount populates the fee value field without manual input. Test across all three fee types (shipping, installation, custom).

### Tests for User Story 1 (Backend validation - ensures constitution compliance)

> **NOTE**: Tests for API already written in Phase 2 (T014, T015). Frontend tests would verify UI integration but are optional since not explicitly requested.

- [X] T016 [P] [US1] Manual test: Verify preset buttons appear in FeeEditor for each fee type
- [X] T017 [P] [US1] Manual test: Verify clicking preset button populates fee value field correctly
- [X] T018 [P] [US1] Manual test: Verify ascending order display (smallest to largest)
- [X] T019 [P] [US1] Manual test: Verify empty presets show "Configure presets in settings" placeholder

### Implementation for User Story 1

- [X] T020 [P] [US1] Create TypeScript interface FeePresetsConfig in frontend/components/pos/FeeEditor.tsx
- [X] T021 [US1] Add state management for feePresets and loadingPresets in frontend/components/pos/FeeEditor.tsx
- [X] T022 [US1] Implement fetchFeePresets useEffect hook to load presets on component mount in frontend/components/pos/FeeEditor.tsx
- [X] T023 [US1] Add WebSocket listener for 'preset-updated' event in frontend/components/pos/FeeEditor.tsx
- [X] T024 [US1] Create QuickAmountButtons sub-component inside FeeEditor.tsx to display preset buttons
- [X] T025 [US1] Implement preset button onClick handler to populate newFee.fee_value in frontend/components/pos/FeeEditor.tsx
- [X] T026 [US1] Add conditional rendering: show preset buttons if presets exist, show placeholder text if no presets in frontend/components/pos/FeeEditor.tsx
- [X] T027 [US1] Add TailwindCSS styling for preset buttons (horizontal layout, consistent spacing, hover states) in frontend/components/pos/FeeEditor.tsx
- [X] T028 [US1] Implement preset button grouping by fee_type: show shipping presets when shipping selected, etc. in frontend/components/pos/FeeEditor.tsx
- [X] T029 Run backend tests: pytest backend/tests/integration/test_settings_api.py -v
- [X] T030 Manual integration test: Add default presets via API, verify buttons appear in POS, verify clicking button populates fee value

**Checkpoint**: User Story 1 should be fully functional - operators can see and use preset buttons to quickly add fees

---

## Phase 4: User Story 2 - Configure Quick Amount Presets (Priority: P2)

**Goal**: Store administrators/managers can customize which quick-amount buttons appear for each fee type through a settings interface, allowing business-specific fee scenarios.

**Independent Test**: Access settings, modify preset amounts for shipping fees (e.g., change [10, 30, 50, 100] to [15, 25, 75]), return to POS, and verify the new preset buttons appear correctly. Test configuration for multiple fee types.

### Tests for User Story 2

- [X] T031 [P] [US2] Manual test: Verify settings page shows fee preset configuration UI
- [X] T032 [P] [US2] Manual test: Verify adding new preset amount updates POS immediately
- [X] T033 [P] [US2] Manual test: Verify modifying existing presets updates POS
- [X] T034 [P] [US2] Manual test: Verify deleting all presets shows placeholder in POS
- [X] T035 [P] [US2] Manual test: Verify validation: max 8 presets enforced, negative values rejected

### Implementation for User Story 2

- [X] T036 [P] [US2] Create FeePresetManager component in frontend/components/settings/FeePresetManager.tsx
- [X] T037 [P] [US2] Define TypeScript props interface for FeePresetManager (locationId, optional onChange callback) in frontend/components/settings/FeePresetManager.tsx
- [X] T038 [US2] Implement fetchPresets async function to load presets via API in frontend/components/settings/FeePresetManager.tsx
- [X] T039 [US2] Add state for editablePresets (local edit state) and savingStatus in frontend/components/settings/FeePresetManager.tsx
- [X] T040 [US2] Create fee type selector (tabs or dropdown for shipping/installation/custom) in frontend/components/settings/FeePresetManager.tsx
- [X] T041 [US2] Implement preset input UI: text inputs for each preset amount with +/- buttons to add/remove in frontend/components/settings/FeePresetManager.tsx
- [X] T042 [US2] Add validation UI: disable save if > 8 presets, show error for negative values in frontend/components/settings/FeePresetManager.tsx
- [X] T043 [US2] Implement savePresets async function to POST to /api/settings/fee-presets in frontend/components/settings/FeePresetManager.tsx
- [X] T044 [US2] Add save button with loading indicator and success/error feedback in frontend/components/settings/FeePresetManager.tsx
- [X] T045 [US2] Integrate FeePresetManager into settings page in frontend/app/settings/page.tsx
- [X] T046 [US2] Add role-based UI: show FeePresetManager only if user has manager role or higher in frontend/app/settings/page.tsx
- [X] T047 [US2] Implement WebSocket broadcast in backend when presets are updated (extend existing broadcast pattern in backend/app/modules/settings/routes.py)
- [X] T048 Manual integration test: Configure presets for shipping via settings UI, verify WebSocket update reaches POS client, verify buttons update without refresh

**Checkpoint**: User Stories 1 AND 2 should both work independently - operators can use presets (US1), managers can configure presets (US2)

---

## Phase 5: User Story 3 - Override Preset with Custom Input (Priority: P3)

**Goal**: POS operators can manually edit fee values even after clicking a preset button, handling unique fee scenarios that don't match preset amounts.

**Independent Test**: Click a preset button (e.g., "30"), then manually change the value to "35", and verify the transaction processes correctly with the custom $35 fee. Test clearing and re-entering values.

### Implementation for User Story 3

> **NOTE**: This story requires NO NEW CODE. The FeeEditor component already allows manual input after preset selection. Verification tasks ensure this behavior works as expected.

- [X] T049 [US3] Manual test: Click preset button, manually edit value, verify transaction uses edited value
- [X] T050 [US3] Manual test: Click preset button, clear field, type new value, verify field accepts input
- [X] T051 [US3] Manual test: Add multiple fees of same type using mix of presets and manual entry, verify all fees recorded correctly
- [X] T052 [US3] Manual test: Verify manual input after preset selection still shows preset button as available (not disabled)

**Checkpoint**: All user stories should now be independently functional - operators can use presets, managers can configure, manual input override works seamlessly

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T053 [P] Add seed migration for default fee presets (10, 30, 50, 100) for each fee type in backend/alembic/versions/t009_seed_fee_presets.py
- [X] T054 [P] Add inline documentation comments for preset validation logic in backend/app/modules/settings/service.py
- [X] T055 [P] Add inline documentation comments for FeePresetsConfig interface in frontend/components/pos/FeeEditor.tsx
- [X] T056 Performance validation: Verify preset loading completes within 200ms using browser devtools
- [X] T057 Performance validation: Verify preset buttons render without layout shift (cumulative layout shift metric)
- [X] T058 [P] Add error boundary around FeeEditor preset section for graceful degradation if API fails in frontend/components/pos/FeeEditor.tsx
- [X] T059 Run quickstart.md validation: Follow implementation steps 1-3 to verify all steps work end-to-end
- [ ] T060 [P] Update AGENTS.md with lessons learned from this feature (if any new patterns emerge)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on User Story 1 (needs preset display to exist before configuration UI makes sense)
- **User Story 3 (Phase 5)**: Depends on User Story 1 (verifies existing behavior works)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on User Story 1 - Configuration UI is meaningless if POS doesn't display presets
- **User Story 3 (P3)**: Depends on User Story 1 - Verifies manual override works with existing preset buttons

### Within Each User Story

- Manual tests can run in parallel (marked [P])
- Frontend components should be built incrementally (state → fetching → rendering → styling)
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (T005, T006, T014, T015)
- Within User Story 1: T016-T019 can run in parallel (manual tests)
- Within User Story 1: T020 can run in parallel with T021-T028 (independent)
- Within User Story 2: T031-T035 can run in parallel (manual tests)
- Within User Story 2: T036, T037 can run in parallel (independent scaffolding)
- Within Polish: T053, T054, T055, T058, T060 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all manual tests for User Story 1 together:
Task: T016 "Manual test: Verify preset buttons appear..."
Task: T017 "Manual test: Verify clicking preset button..."
Task: T018 "Manual test: Verify ascending order..."
Task: T019 "Manual test: Verify empty presets..."

# Launch TypeScript interface creation in parallel with state setup:
Task: T020 "Create TypeScript interface FeePresetsConfig..."
Task: T021 "Add state management..." (can start in parallel)

# Sequential after T021:
Task: T022 "Implement fetchFeePresets..."
Task: T023 "Add WebSocket listener..."
# ...then rest of implementation
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. **Complete Phase 1: Setup** (5-10 minutes)
2. **Complete Phase 2: Foundational** (2-3 hours)
   - Backend API with validation
   - Test infrastructure
3. **Complete Phase 3: User Story 1** (3-4 hours)
   - Frontend preset display
   - POS integration
4. **STOP and VALIDATE**: Test independently
   - Add default presets via API call
   - Verify buttons appear in POS
   - Verify clicking populates fee value
5. **Deploy MVP**: Operators can now use preset buttons for faster fee entry

### Incremental Delivery

1. **Complete Setup + Foundational** → Backend ready
2. **Add User Story 1** → Test → Deploy (MVP! Operators see immediate time savings)
3. **Add User Story 2** → Test → Deploy (Managers can customize)
4. **Verify User Story 3** → Minimal effort, already works
5. **Complete Polish** → Performance tuned, documentation complete

### Sequential Recommendation

Given the dependency US2 → US1, a single developer should work sequentially:
1. Backend API (Phase 2)
2. US1 implementation (Phase 3)
3. US2 implementation (Phase 4)
4. US3 verification (Phase 5)
5. Polish (Phase 6)

### Parallel Team Strategy

With two developers:
- **Developer A**: Phases 1-2 (Setup + Foundational)
- **Developer B**: Can prepare frontend scaffolding in parallel (T020, T036-T037)
- Once Foundation complete:
  - **Developer A**: User Story 1 (Phase 3)
  - **Developer B**: Polish tasks in parallel (T053-T055, T060)
- After US1 complete:
  - **Developer A**: User Story 2 (Phase 4)
  - **Developer B**: Continue polish or start US3 verification
- After US2 complete:
  - **Developer A**: User Story 3 verification (Phase 5)
  - **Developer B**: Final polish tasks

---

## Notes

- **[P]tasks** = different files, no dependencies
- **[Story] label** maps task to specific user story for traceability
- **No database migrations needed** - uses existing settings table
- **WebSocket integration** mirrors existing product update pattern
- **Backend validation** ensures constitution compliance (single source of truth, backend authority)
- **Frontend is thin presentation** - all business logic in backend per constitution
- **Commit after each completed user story** - enables rollback if needed
- **Manual testing is sufficient** - no automated frontend test framework requested
- Each user story is independently testable and deployable
- US3 requires NO implementation - behavior already exists, only verification needed