# Implementation Plan: Quick Fee Amount Buttons

**Branch**: `002-quick-fee-buttons` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-quick-fee-buttons/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add configurable quick-amount preset buttons to the POS fee entry interface, allowing operators to rapidly select common fee amounts instead of manual typing. Presets are stored per fee type per location, configurable by managers, and displayed in ascending numerical order for intuitive access. Implementation extends the existing settings system (key-value storage) similar to how payment methods are configured.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/Next.js 14 (frontend)  
**Primary Dependencies**: FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5, React 18, TailwindCSS 3.4  
**Storage**: PostgreSQL (sole source of truth per constitution)  
**Testing**: pytest 7.4 (backend), Jest built into Next.js 14 (frontend)  
**Target Platform**: Web application (Linux server backend, browser frontend)  
**Project Type**: Web-service (monolithic FastAPI backend, Next.js frontend)  
**Performance Goals**: 200ms load time for preset buttons in POS interface (per SC-005)  
**Constraints**: Max 8 presets per fee type, Manager role required for configuration  
**Scale/Scope**: Single-user POS, multi-location预设 support

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Implementation Check

**Principle III. Explicit Over Implicit:** ✅ COMPLIANT  
Preset amounts will be stored as explicit configuration values in the database per fee type per location. No hidden calculations.

**Principle V. Simplicity of Use:** ✅ COMPLIANT  
Quick-amount buttons reduce clicks and speed up fee entry. Financial breakdown visible on transaction screen. Clear placeholder when no presets configured.

**Principle VII. Backend Authority:** ✅ COMPLIANT  
Preset configuration validation (max 8, positive values only, Manager role check) enforced in backend. Frontend displays validated presets.

**Principle VIII. Input Validation:** ✅ COMPLIANT  
All preset configuration API endpoints validate request payloads (Pydantic schemas). Invalid input returns structured errors.

### Post-Design Re-Check (after Phase 1)

**Principle II. Single Source of Truth**: ✅ COMPLIANT  
Fee presets stored only in PostgreSQL `settings` table via key-value pairs. No secondary caches or derived stores.

**Principle VI. Data Integrity**: ✅ COMPLIANT  
Preset values use DECIMAL type in JSON arrays, strictly validated. All operations use transactions.

**Principle IX. Extensibility by Design**: ✅ COMPLIANT  
Key format `fee_presets_{location_id}_{fee_type}` supports multi-location and future fee types without schema changes.

### Violations Requiring Justification

None. The feature extends an existing pattern (settings key-value storage) without introducing complexity that violates constitution principles.

## Project Structure

### Documentation (this feature)

```text
specs/002-quick-fee-buttons/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (already exists)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api.md          # API contract definitions
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── models/
│   │   └── settings.py            # Extended: add fee_preset-specific methods
│   ├── modules/
│   │   └── settings/
│   │       ├── routes.py          # Extended: add preset CRUD endpoints
│   │       ├── service.py         # Extended: add preset validation logic
│   │       └── schemas.py         # Extended: add preset request/response schemas
│   └── schemas/
│       └── sale.py                # No changes needed (FeeType enum already exists)
├── alembic/
│   └── versions/
│       └── (no migration needed)  # Uses existing settings table
└── tests/
    └── integration/
        └── test_settings_api.py   # Extended: add preset API tests

frontend/
├── components/
│   ├── pos/
│   │   └── FeeEditor.tsx          # Extended: add quick-amount buttons
│   └── settings/
│       └── FeePresetManager.tsx   # NEW: preset configuration UI
└── app/
    └── settings/
        └── page.tsx               # Extended: integrate FeePresetManager
```

**Structure Decision**: This feature extends existing settings and fee modules rather than creating new top-level directories. The pattern mirrors how payment methods are configured (see `PaymentMethodManager.tsx` and related backend routes).

## Complexity Tracking

> No constitution violations detected. This feature follows existing patterns without introducing complexity that requires justification.
