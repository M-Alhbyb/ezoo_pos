# Implementation Plan: Real-time Partner Profit from Product Sales

**Branch**: `006-partner-profit-sharing` | **Date**: 2026-04-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/006-partner-profit-sharing/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Redesign partner system from project-based profit to real-time product-based profit sharing. Partners earn profit automatically from sales of products linked to them. Profit = selling price - base cost (minimum 0). Each product links to either one partner or none. Production-grade integration with existing POS sale flow.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5  
**Storage**: PostgreSQL (sole source of truth per constitution)  
**Testing**: pytest, integration tests  
**Target Platform**: Linux server  
**Project Type**: Web service (FastAPI monolith) + Next.js frontend  
**Performance Goals**: Profit credit within 10 seconds per SC-001  
**Constraints**: None beyond existing stack  
**Scale/Scope**: Single branch, single user (per constitution non-goals)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Financial Accuracy First | PASS | profit_amount stored as DECIMAL, never computed ad-hoc |
| II. Single Source of Truth | PASS | PostgreSQL via SQLAlchemy models |
| III. Explicit Over Implicit | PASS | selling_price and base_cost stored per transaction |
| IV. Immutable Financial Records | PASS | transactions immutable, reversals via new records |
| V. Simplicity of Use | PASS | Profit credited automatically on sale |
| VI. Data Integrity | PASS | DECIMAL types, timestamps, FK constraints |
| VII. Backend Authority | PASS | Business logic in backend service |
| VIII. Input Validation | PASS | Pydantic schemas validate all inputs |
| IX. Extensibility by Design | PASS | branch_id foreign keys reserved for future |

**Post-Phase 1 Re-check**: All gates pass.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: Using existing web application structure (Option 2).

- **Backend**: `backend/app/models/`, `backend/app/modules/partners/`, `backend/app/schemas/`
- **Frontend**: `frontend/app/partners/`, `frontend/components/partners/`
- **Tests**: `backend/tests/unit/`, `backend/tests/integration/`

## Complexity Tracking

No complexity violations. All Constitution gates pass.

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
