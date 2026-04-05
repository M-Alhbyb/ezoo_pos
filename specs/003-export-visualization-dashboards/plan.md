# Implementation Plan: Export Formats and Visualization Dashboards

**Branch**: `003-export-visualization-dashboards` | **Date**: 2026-04-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-export-visualization-dashboards/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add export capabilities (CSV, XLSX, PDF) for all Phase 4 reports and interactive visualization dashboards with charts. Backend provides export endpoints and dashboard data APIs; frontend implements chart rendering with Recharts. All financial data maintains Decimal precision throughout the pipeline. Rate limiting enforces format-specific row limits; charts enforce 1,000 data point maximum with progress indicators and cancellation for long-running operations.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript/Next.js 14 (frontend)  
**Primary Dependencies**: FastAPI 0.109, SQLAlchemy async 2.0, Pydantic 2.5, React 18, TailwindCSS 3.4, pandas (CSV/XLSX), ReportLab 4.0.7 (PDF), Recharts (frontend charts)
**Storage**: PostgreSQL (via existing SQLAlchemy async models)
**Testing**: pytest (backend), jest + @testing-library/react (frontend)
**Target Platform**: Web application (Next.js 14 on frontend, FastAPI backend)
**Project Type**: Web-service + frontend application
**Performance Goals**: Export generation within 30 seconds for 10,000 rows, dashboard render within 3 seconds, filter updates within 2 seconds
**Constraints**: Maximum rows per format (CSV: 100k, XLSX: 50k, PDF: 10k), maximum 1,000 data points per chart, rate limit for large exports (>5,000 rows), progress indicators for operations >5 seconds
**Scale/Scope**: Support 10 concurrent export requests, handle reports up to 100,000 rows (CSV format)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Financial Accuracy First** ✅
- All monetary values use DECIMAL types throughout
- No floating-point calculations in frontend
- Exports preserve exact precision from database to file
- Dashboard tooltips display full decimal values

**II. Single Source of Truth** ✅
- PostgreSQL is sole data source via existing ReportService
- No caching or derived stores for export/dashboard data
- Frontend consumes API responses only (no local financial calculations)

**III. Explicit Over Implicit** ✅
- Export format limits stored in configuration
- Dashboard data point limits enforced explicitly
- Rate limits for large exports tracked
- All query parameters (date range, filters) validated and logged on error

**IV. Immutable Financial Records** ✅
- Export operations are read-only
- No mutations to underlying financial data
- Charts display data from immutable snapshots
- Cancellation cleans up without data corruption

**V. Simplicity of Use** ✅
- Single-click export buttons for each format
- Clear error messages for limit violations
- Progress indicators for long operations
- Intuitive dashboard filters with immediate feedback

**VI. Data Integrity** ✅
- All monetary values remain DECIMAL type
- Timestamps included in export metadata
- Validation prevents exceeding row limits
- Dashboard filtering maintains data consistency

**VII. Backend Authority** ✅
- Export limits and rate limiting enforced in backend
- Dashboard aggregation performed in backend (SQLAlchemy GROUP BY)
- Frontend only renders provided data
- Validation of export requests in API layer

**VIII. Input Validation** ✅
- All export endpoints validate format, date range, row count
- Dashboard endpoints validate filter parameters
- Invalid requests return structured error responses
- Row count validation before export generation

**IX. Extensibility by Design** ✅
- Export service designed for adding new formats
- Dashboard architecture supports additional chart types
- No schema changes required (reuses existing models)
- Format limits and rate limits configurable

**GATE RESULT**: ✅ PASS - No constitution violations

## Project Structure

### Documentation (this feature)

```text
specs/003-export-visualization-dashboards/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
# Web application structure (existing)
backend/
├── src/
│   ├── app/
│   │   ├── modules/
│   │   │   ├── reports/
│   │   │   │   ├── export_service.py        # NEW: CSV/XLSX/PDF generation
│   │   │   │   ├── dashboard_service.py     # NEW: Chart data aggregation
│   │   │   │   ├── report_service.py        # EXISTING: Reuse queries
│   │   │   │   └── ...
│   │   │   └── ...
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── reports.py               # EXISTING: Extend with export endpoints
│   │   │   │   └── dashboard.py             # NEW: Dashboard data endpoints
│   │   │   └── ...
│   │   └── schemas/
│   │       ├── export.py                    # NEW: Export request/response schemas
│   │       └── dashboard.py                 # NEW: Dashboard data schemas
│   └── ...
└── tests/
    ├── unit/
    │   ├── test_export_service.py           # NEW: Unit tests for exports
    │   └── test_dashboard_service.py        # NEW: Unit tests for dashboard aggregation
    └── integration/
        ├── test_export_endpoints.py         # NEW: Integration tests for export API
        └── test_dashboard_endpoints.py      # NEW: Integration tests for dashboard API

frontend/
├── src/
│   ├── app/
│   │   ├── dashboard/                       # NEW: Dashboard pages
│   │   │   ├── sales/
│   │   │   │   └── page.tsx
│   │   │   ├── projects/
│   │   │   │   └── page.tsx
│   │   │   ├── partners/
│   │   │   │   └── page.tsx
│   │   │   └── inventory/
│   │   │       └── page.tsx
│   │   └── reports/                         # EXISTING: Extend with export buttons
│   │       ├── sales/
│   │   │   └── page.tsx                     # ADD: Export buttons
│   │       └── ...
│   ├── components/
│   │   ├── charts/                          # NEW: Reusable chart components
│   │   │   ├── LineChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   ├── PieChart.tsx
│   │   │   └── StackedBarChart.tsx
│   │   ├── dashboard/                       # NEW: Dashboard layout components
│   │   │   ├── DashboardLayout.tsx
│   │   │   ├── DatePicker.tsx
│   │   │   └── ExportButton.tsx
│   │   └── ...
│   ├── lib/
│   │   ├── api/
│   │   │   ├── reports.ts                   # EXTEND: Add export functions
│   │   │   └── dashboard.ts                 # NEW: Dashboard API client
│   │   └── utils/
│   │       ├── export-utils.ts             # NEW: Export download handling
│   │       └── chart-utils.ts              # NEW: Chart data transformation
│   └── ...
└── tests/
    └── components/
        ├── charts/                          # NEW: Chart component tests
        └── dashboard/                       # NEW: Dashboard component tests
```

**Structure Decision**: Using existing web application structure with backend FastAPI + frontend Next.js. No new database models required (reuses existing ReportService queries). Adds export_service.py and dashboard_service.py for new functionality. Frontend adds /dashboard route for visualization pages and extends existing /reports pages with export buttons.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected. Table not needed.

## Phase 0: Research & Technology Decisions

### Research Questions

1. **PDF Generation Library**: WeasyPrint vs ReportLab for PDF export generation
   - Decision needed: Which library best fits FastAPI async pattern and preserves Decimal precision
   - Criteria: Async compatibility, Decimal support, table rendering quality, performance

2. **Frontend Charting Library**: Recharts vs Chart.js for interactive dashboards
   - Decision needed: Best fit for React 18 + Next.js 14 app with decimal precision requirements
   - Criteria: TypeScript support, tooltip customization, performance with 1,000 data points

3. **Async File Generation**: Best practices for async CSV/XLSX generation in FastAPI
   - Decision needed: How to handle large file generation without blocking
   - Criteria: Streaming response vs file buffer, memory management, cancellation support

4. **Progress Indicator Implementation**: Frontend-backend coordination pattern
   - Decision needed: SignalR/WebSocket vs polling vs Server-Sent Events for progress updates
   - Criteria: Existing WebSocket infrastructure compatibility, cancellation support

5. **Rate Limiting Strategy**: Best approach for large export rate limiting
   - Decision needed: In-memory vs Redis-backed rate limiting for export requests
   - Criteria: Multi-user preparation (Constitution IX), configurability, integration with existing auth

### Research Artifacts to Generate

- `research.md` with technology selection rationales
- Integration patterns with existing EZOO POS architecture
- Performance benchmarks for library choices
- Alternative approaches evaluated

## Phase 1: Design & Contracts

### Data Model

**No new database models required**. Feature reuses existing:
- Financial snapshots (immutable, already DECIMAL)
- Report queries from existing ReportService
- Partner, Project, Sale, Inventory models

**New Non-Persisted Entities**:
- ExportRequest (Pydantic schema): format, date_range, report_type, row_limits
- DashboardFilter (Pydantic schema): date_range, optional filters
- ChartDataPoint (Pydantic schema): labels, values, timestamps
- ExportMetadata (Pydantic schema): generated_at, format, row_count, duration

**Output**: `data-model.md` documenting schema additions and existing model reuse

### API Contracts

**New Endpoints**:

**Export Endpoints** (extend existing `/api/reports` routes):
- `GET /api/reports/sales/export?format=csv|xlsx|pdf&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/reports/projects/export?format=csv|xlsx|pdf&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/reports/partners/export?format=csv|xlsx|pdf&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/reports/inventory/export?format=csv|xlsx|pdf&start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

**Dashboard Endpoints** (new `/api/dashboard` routes):
- `GET /api/dashboard/sales?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/dashboard/projects?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/dashboard/partners?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`
- `GET /api/dashboard/inventory?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD`

**Output**: `/contracts/` with OpenAPI schemas for all new endpoints

### Agent Context Update

Run `.specify/scripts/bash/update-agent-context.sh opencode` to add:
- pandas to Python dependencies
- WeasyPrint or ReportLab to Python dependencies
- Recharts to frontend dependencies
- Export service architecture pattern
- Dashboard service aggregation pattern

## Phase 2: Implementation Planning

*Phase 2 output created by `/speckit.tasks` command - not included in this plan*

---

## Post-Design Constitution Re-Check

*Re-evaluate after Phase 1 design complete*

✅ **I. Financial Accuracy First**: All Pydantic schemas use Decimal; pandas preserves Decimal through float conversion with precision control
✅ **II. Single Source of Truth**: Dashboard and export services query PostgreSQL via existing ReportService
✅ **III. Explicit Over Implicit**: Export limits and chartlimits stored in configuration, validated in schemas
✅ **IV. Immutable Financial Records**: Exports read from immutable snapshots; no mutations
✅ **V. Simplicity of Use**: Single-click exports; clear error messages; progress indicators
✅ **VI. Data Integrity**: DECIMAL types throughout; timestamp tracking; validation prevents overflow
✅ **VII. Backend Authority**: Limits enforced in backend; aggregation in backend; frontend only renders
✅ **VIII. Input Validation**: All endpoints validate via Pydantic schemas; structured error responses
✅ **IX. Extensibility by Design**: Export service extensible for new formats; dashboard service supports new chart types

**GATE RESULT**: ✅ PASS - All principles satisfied in design