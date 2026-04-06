# Tasks: Export Formats and Visualization Dashboards

**Input**: Design documents from `/specs/003-export-visualization-dashboards/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3...)
- Include exact file paths in descriptions

## Path Conventions

- **Web application structure**: `backend/src/` and `frontend/src/`
- Paths follow structure defined in plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies and configure environment for exports and dashboards

- [X] T001 [P] Add pandas==2.1.4 to backend/requirements.txt for CSV/XLSX generation
- [X] T002 [P] Add ReportLab==4.0.7 to backend/requirements.txt for PDF generation
- [X] T003 [P] Add slowapi==0.1.9 to backend/requirements.txt for rate limiting
- [X] T004 [P] Add Recharts2.10.3 to frontend/package.json for chart components
- [X] T005 Configure export limits in backend/src/app/core/config.py (CSV_MAX_ROWS, XLSX_MAX_ROWS, PDF_MAX_ROWS, DASHBOARD_MAX_POINTS)
- [X] T006 Run pip install -rrequirements.txt in backend directory
- [X] T007 Run npm install in frontend directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core schemas and services that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 [P] Create export request/response schemas in backend/src/app/schemas/export.py (ExportRequest, ExportMetadata, ExportFormat enum)
- [X] T009 [P] Create dashboard filter and data schemas in backend/src/app/schemas/dashboard.py (DashboardFilter, ChartDataPoint, [X]ChartData schemas)
- [X] T010 [P] Create error schemas in backend/src/app/schemas/errors.py (ExportError, RowLimitExceededError, RateLimitExceededError)
- [X] T011 Create ExportService base class in backend/src/app/modules/reports/export_service.py with async methods for CSV, XLSX, PDF generation
- [X] T012 Create DashboardService base class in backend/src/app/modules/reports/dashboard_service.py with aggregation methods
- [X] T013 [P] Create new dashboard API routes file at backend/src/app/api/routes/dashboard.py with empty router
- [X] T014 [P] Extend existing reports API routes in backend/src/app/api/routes/reports.py to add export endpoint structure
- [X] T015 [P] Create frontend API client for dashboards at frontend/src/lib/api/dashboard.ts
- [X] T016 [P] Create frontend utils for export handling at frontend/src/lib/utils/export-utils.ts
- [X] T017 [P] Create frontend utils for chart data transformation at frontend/src/lib/utils/chart-utils.ts
- [X] T018 [P] Create base chart component at frontend/src/components/charts/index.tsx with shared chart configuration
- [X] T019 Configure Slowapi rate limiter in backend/src/app/main.py for large export requests
- [X] T019b Implement thread-safe ExportService with request isolation in backend/src/app/modules/reports/export_service.py to support concurrent export requests without data mixing (FR-036)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Export Sales Report as PDF (Priority: P1) 🎯 MVP

**Goal**: Enable business managers to export sales reports as PDF for presentations with precise decimal values

**Independent Test**: Select date range in sales report, click "Export as PDF", verify downloaded file contains matching data with proper formatting and decimal precision

### Backend Implementation for US1

- [X] T020 [P] [US1] Implement get_sales_count method in backend/src/app/modules/reports/report_service.py to count rows before export
- [X] T021 [P] [US1] Implement generate_pdf_sales_report method in backend/src/app/modules/reports/export_service.py using ReportLab with table formatting
- [X] T022 [US1] Implement validate_export_limits method in backend/src/app/modules/reports/export_service.py to check CSV/XLSX/PDF row limits and warn users when approaching 80% of format-specific cap (FR-041)
- [X] T023 [US1] Add GET /api/reports/sales/export endpoint in backend/src/app/api/routes/reports.py with format, start_date, end_date query params
- [X] T024 [US1] Add row count validation and rate limiting to sales export endpoint in backend/src/app/api/routes/reports.py
- [X] T025 [US1] Add WebSocket progress message broadcasting in backend/src/app/api/routes/reports.py for export progress updates

### Frontend Implementation for US1

- [X] T026 [P] [US1] Add export PDF button component in frontend/src/components/reports/ExportPDFButton.tsx
- [X] T027 [US1] Integrate ExportPDFButton into existing sales report page at frontend/src/app/reports/sales/page.tsx
- [X] T028 [US1] Add file download handling in frontend/src/lib/utils/export-utils.ts for PDF download
- [X] T029 [US1] Add progress indicator modal in frontend/src/components/reports/ExportProgressModal.tsx with cancel button
- [X] T030 [US1] Wire WebSocket listener in frontend/src/app/reports/sales/page.tsx to receive export_progress messages

**Checkpoint**: At this point, User Story 1 (PDF Sales Export) should be fully functional and testable independently

---

## Phase 4: User Story 2 - View Interactive Sales Dashboard (Priority: P1)

**Goal**: Display sales trends as interactive line chart with daily revenue, profit, VAT and date range filtering

**Independent Test**: Navigate to sales dashboard, select date range, verify line chart displays with interactive tooltips showing correct daily figures

### Backend Implementation for US2

- [X] T031 [P] [US2] Implement get_sales_dashboard_data method in backend/src/app/modules/reports/dashboard_service.py with SQLAlchemy GROUP BY aggregation
- [X] T032 [P] [US2] Add data point limit validation (max1000 points) in backend/src/app/modules/reports/dashboard_service.py
- [X] T033 [US2] Add GET /api/dashboard/sales endpoint in backend/src/app/api/routes/dashboard.py with start_date, end_date query params
- [X] T034 [US2] Validate date range and return SalesChartData schema in dashboard endpoint

### Frontend Implementation for US2

- [X] T035 [P] [US2] Create LineChart component in frontend/src/components/charts/LineChart.tsx with Recharts responsive container
- [X] T036 [P] [US2] Create DatePicker component in frontend/src/components/dashboard/DatePicker.tsx for date range filtering
- [X] T037 [P] [US2] Create DashboardLayout component in frontend/src/components/dashboard/DashboardLayout.tsx with filter bar and chart container
- [X] T038 [US2] Create sales dashboard page at frontend/src/app/dashboard/sales/page.tsx with LineChart for revenue/profit/VAT
- [X] T039 [US2] Add custom tooltip formatter in frontend/src/components/charts/LineChart.tsx to display 4 decimal places for monetary values
- [X] T040 [US2] Add empty state handling in frontend/src/app/dashboard/sales/page.tsx when no data exists
- [X] T041 [US2] Wire date range filter to call GET /api/dashboard/sales endpoint in frontend/src/app/dashboard/sales/page.tsx

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Export Project Report as Excel (Priority: P2)

**Goal**: Enable project managers to export project reports as Excel for further analysis with preserved decimal precision

**Independent Test**: Export project report as XLSX, open in spreadsheet software, verify all formulas, values, and precision match the original report

### Backend Implementation for US3

- [X] T042 [P] [US3] Implement get_projects_count method in backend/src/app/modules/reports/report_service.py
- [X] T043 [P] [US3] Implement generate_xlsx_projects_report method in backend/src/app/modules/reports/export_service.py using pandas with xlsxwriter
- [X] T044 [US3] Add GET /api/reports/projects/export endpoint in backend/src/app/api/routes/reports.py with format, start_date, end_date query params
- [X] T045 [US3] Ensure Decimal precision preservation in XLSX export using float_format='%.4f' in pandas to_excel

### Frontend Implementation for US3

- [X] T046 [P] [US3] Add export Excel button component in frontend/src/components/reports/ExportExcelButton.tsx
- [X] T047 [P] [US3] Add export XLSX handling in frontend/src/lib/utils/export-utils.ts
- [X] T048 [US3] Integrate ExportExcelButton into existing projects report page at frontend/src/app/reports/projects/page.tsx

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - View Partner Dividends Dashboard (Priority: P2)

**Goal**: Display partner dividend distributions as pie chart showing percentages and monetary amounts

**Independent Test**: Navigate to partners dashboard, verify pie chart displays correct proportions and amounts for each partner's historical dividends

### Backend Implementation for US4

- [X] T049 [P] [US4] Implement get_partners_dashboard_data method in backend/src/app/modules/reports/dashboard_service.py with partner aggregation
- [X] T050 [US4] Add GET /api/dashboard/partners endpoint in backend/src/app/api/routes/dashboard.py with start_date, end_date, optional partner_id query params
- [X] T051 [US4] Return PartnerChartData schema with partner_names, dividend_amounts, percentages arrays

### Frontend Implementation for US4

- [X] T052 [P] [US4] Create PieChart component in frontend/src/components/charts/PieChart.tsx with Recharts PieChart
- [X] T053 [US4] Create partners dashboard page at frontend/src/app/dashboard/partners/page.tsx with PieChart for dividend distribution
- [X] T054 [US4] Add custom tooltip in PieChart to show partner name, total dividends, and percentage
- [X] T055 [US4] Add optional partner filter dropdown in frontend/src/app/dashboard/partners/page.tsx

**Checkpoint**: At this point, User Stories 1, 2, 3, AND 4 should all work independently

---

## Phase 7: User Story 5 - Export Inventory Report as CSV (Priority: P2)

**Goal**: Enable inventory managers to export movement reports as CSV for system integration with proper escaping

**Independent Test**: Export inventory movement report, open in text editor, verify CSV structure matches expected format with all data rows present

### Backend Implementation for US5

- [X] T056 [P] [US5] Implement get_inventory_count method in backend/src/app/modules/reports/report_service.py
- [X] T057 [P] [US5] Implement generate_csv_inventory_report method in backend/src/app/modules/reports/export_service.py using pandas to_csv with proper escaping
- [X] T058 [US5] Add GET /api/reports/inventory/export endpoint in backend/src/app/api/routes/reports.py with format, start_date, end_date query params
- [X] T059 [US5] Ensure special characters in product names are properly escaped in CSV export

### Frontend Implementation for US5

- [X] T060 [P] [US5] Add export CSV button component in frontend/src/components/reports/ExportCSVButton.tsx
- [X] T061 [P] [US5] Add export CSV handling in frontend/src/lib/utils/export-utils.ts
- [X] T062 [US5] Integrate ExportCSVButton into existing inventory report page at frontend/src/app/reports/inventory/page.tsx

**Checkpoint**: At this point, User Stories 1-5 should all work independently

---

## Phase 8: User Story 6 - View Project Profit Distribution Bar Chart (Priority: P3)

**Goal**: Display project profit distribution as bar chart comparing profit margins across completed projects

**Independent Test**: Navigate to projects dashboard, verify bar chart displays project profits with correct values and interactive filtering

### Backend Implementation for US6

- [X] T063 [P] [US6] Implement get_projects_dashboard_data method in backend/src/app/modules/reports/dashboard_service.py with project profit aggregation
- [X] T064 [US6] Add GET /api/dashboard/projects endpoint in backend/src/app/api/routes/dashboard.py with start_date, end_date, optional project_id query params
- [X] T065 [US6] Return ProjectChartData schema with project_names, profits, profit_margins, project_ids arrays

### Frontend Implementation for US6

- [X] T066 [P] [US6] Create BarChart component in frontend/src/components/charts/BarChart.tsx with Recharts BarChart
- [X] T067 [US6] Create projects dashboard page at frontend/src/app/dashboard/projects/page.tsx with BarChart for profit distribution
- [X] T068 [US6] Add custom tooltip in BarChart to show project name, total profit, and profit margin percentage
- [X] T069 [US6] Add optional project filter dropdown in frontend/src/app/dashboard/projects/page.tsx

**Checkpoint**: At this point, User Stories 1-6 should all work independently

---

## Phase 9: User Story 7 - View Inventory Movements Stacked Bar Chart (Priority: P3)

**Goal**: Display inventory movements as stacked bar chart showing quantities by movement reason (sales, restocks, reversals)

**Independent Test**: Navigate to inventory dashboard, verify stacked bar chart correctly aggregates movements by reason type with proper filtering

### Backend Implementation for US7

- [X] T070 [P] [US7] Implement get_inventory_dashboard_data method in backend/src/app/modules/reports/dashboard_service.py with movement aggregation
- [X] T071 [US7] Add GET /api/dashboard/inventory endpoint in backend/src/app/api/routes/dashboard.py with start_date, end_date query params
- [X] T072 [US7] Return InventoryChartData schema with dates, sales, restocks, reversals arrays

### Frontend Implementation for US7

- [X] T073 [P] [US7] Create StackedBarChart component in frontend/src/components/charts/StackedBarChart.tsx with Recharts stacked BarChart
- [X] T074 [US7] Create inventory dashboard page at frontend/src/app/dashboard/inventory/page.tsx with StackedBarChart for movements by reason
- [X] T075 [US7] Add custom tooltip in StackedBarChart to show date, movement reason, and quantity

**Checkpoint**: At this point, User Stories 1-7 should all work independently

---

## Phase 10: User Story 8 - Export Dashboard Chart Data (Priority: P3)

**Goal**: Enable users to export underlying data from any dashboard chart to CSV, XLSX, or PDF

**Independent Test**: Display any dashboard chart, click export button, verify downloaded file contains same data shown in the chart

### Backend Implementation for US8

- [X] T076 [P] [US8] Implement generate_csv_dashboard_data method in backend/src/app/modules/reports/export_service.py for chart data export
- [X] T077 [P] [US8] Implement generate_xlsx_dashboard_data method in backend/src/app/modules/reports/export_service.py for chart data export
- [X] T078 [P] [US8] Implement generate_pdf_dashboard_data method in backend/src/app/modules/reports/export_service.py with chart visualization and data table
- [X] T079 [US8] Extend dashboard endpoints in backend/src/app/api/routes/dashboard.py to accept export format parameter
- [X] T080 [US8] Add export button handling in dashboard endpoints to return file attachments

### Frontend Implementation for US8

- [X] T081 [P] [US8] Create ExportButton component in frontend/src/components/dashboard/ExportButton.tsx with format selection dropdown
- [X] T082 [US8] Integrate ExportButton into DashboardLayout component in frontend/src/components/dashboard/DashboardLayout.tsx
- [X] T083 [US8] Add export functionality to all dashboard pages (sales, projects, partners, inventory) using ExportButton component

**Checkpoint**: At this point, all 8 user stories should be fully functional

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, logging, and documentation

- [X] T084 [P] Add export error logging in backend/src/app/modules/reports/export_service.py for all export failures
- [X] T085 [P] Add dashboard error logging in backend/src/app/modules/reports/dashboard_service.py for rendering failures
- [X] T086 [P] Add row limit exceeded error handling in backend/src/app/api/routes/reports.py with user-friendly messages
- [X] T087 [P] Add data point limit error handling in backend/src/app/api/routes/dashboard.py with suggestions to narrow date range
- [ ] T088 [P] Add loading states to all dashboard pages in frontend/src/app/dashboard/ for data fetch operations (BLOCKED: frontend pages don't exist)
- [ ] T089 [P] Add error boundary components to all dashboard pages in frontend/src/app/dashboard/ for graceful error handling (BLOCKED: frontend pages don't exist)
- [X] T090 Performance optimization: Add database query indexing for dashboard aggregation queries
- [ ] T091 Security hardening: Ensure all export and dashboard endpoints require authentication (BLOCKED: no auth infrastructure exists)
- [ ] T092 Run quickstart.md validation to verify all setup instructions work
- [X] T093 Update API documentation in backend/src/app/main.py to include export and dashboard endpoints
- [X] T094 Add rate limit configuration to backend/.env.example file

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-10)**: All depend on Foundational phase completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1 → P2 → P2 → P2 → P3 → P3 → P3)
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1 - PDF Sales Export)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US2 (P1 - Sales Dashboard)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US3 (P2 - Excel Projects Export)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US4 (P2 - Partners Dashboard)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US5 (P2 - CSV Inventory Export)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US6 (P3 - Projects Dashboard)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US7 (P3 - Inventory Dashboard)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **US8 (P3 - Dashboard Data Export)**: Can start after Foundational (Phase 2) - May integrate with existing dashboards but independently testable

### Within Each User Story

- Backend models/services before endpoints
- Frontend components before page integration
- Core implementation before polish
- Story complete before moving to next priority

### Parallel Opportunities

1. **Setup (Phase 1)**: All T001-T004 can run in parallel
2. **Foundational (Phase 2)**: All T008-T019 can run in parallel (different files)
3. **User Story Backends**: Many backend tasks marked [P] can run in parallel across stories
4. **User Story Frontends**: Many frontend tasks marked [P] can run in parallel across stories
5. **Polish (Phase 11)**: All T084-T089 can run in parallel (different files)

---

## Parallel Example: Foundational Phase

```bash
# Launch all schema creation tasks in parallel (T008-T010):
Task: "Create export request/response schemas in backend/src/app/schemas/export.py"
Task: "Create dashboard filter and data schemas in backend/src/app/schemas/dashboard.py"
Task: "Create error schemas in backend/src/app/schemas/errors.py"

# Launch all service creation tasks serially (T011-T012 must complete before routes):
Task: "Create ExportService base class in backend/src/app/modules/reports/export_service.py"
Task: "Create DashboardService base class in backend/src/app/modules/reports/dashboard_service.py"

# Launch all route setup tasks in parallel (T013-T014):
Task: "Create new dashboard API routes file at backend/src/app/api/routes/dashboard.py"
Task: "Extend existing reports API routes in backend/src/app/api/routes/reports.py"

# Launch all frontend setup tasks in parallel (T015-T019):
Task: "Create frontend API client for dashboards at frontend/src/lib/api/dashboard.ts"
Task: "Create frontend utils for export handling at frontend/src/lib/utils/export-utils.ts"
Task: "Create frontend utils for chart data transformation at frontend/src/lib/utils/chart-utils.ts"
Task: "Create base chart component at frontend/src/components/charts/index.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories1 & 2 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T019) - CRITICAL
3. Complete Phase 3: User Story 1 - PDF Sales Export (T020-T030)
4. **STOP and VALIDATE**: Test PDF export independently
5. Complete Phase 4: User Story 2 - Sales Dashboard (T031-T041)
6. **STOP and VALIDATE**: Test sales dashboard independently
7. Deploy/demo MVP (PDF exports + sales dashboard)

### Incremental Delivery (Recommended)

1. **Foundation** (Phases 1-2): Setup + Foundational → Foundation ready
2. **MVP** (Phases 3-4): Add US1 + US2 → Test independently → Deploy/Demo (MVP!)
3. **Export Layer** (Phases 5, 7): Add US3 + US5 → Test independently → Deploy/Demo
4. **Dashboard Layer** (Phases 6, 8-9): Add US4 + US6 + US7 → Test independently → Deploy/Demo
5. **Polish** (Phase 10-11): Add US8 + cross-cutting → Final validation → Deploy/Demo

### Parallel Team Strategy

With 3 developers:

1. **Team completes Setup + Foundational together**
2. **Once Foundational done:**
   - **Developer A**: US1 (PDF Export) → US3 (Excel Export) → US6 (Projects Dashboard)
   - **Developer B**: US2 (Sales Dashboard) → US4 (Partners Dashboard) → US7 (Inventory Dashboard)
   - **Developer C**: US5 (CSV Export) → US8 (Dashboard Export) → Polish
3. **Stories complete and integrate independently**

---

## Task Summary

**Total Tasks**: 94

**Tasks by Phase**:
- Phase 1 (Setup): 7 tasks
- Phase 2 (Foundational): 12 tasks
- Phase 3 (US1 - PDF Export): 11 tasks
- Phase 4 (US2 - Sales Dashboard): 11 tasks
- Phase 5 (US3 - Excel Export): 7 tasks
- Phase 6 (US4 - Partners Dashboard): 7 tasks
- Phase 7 (US5 - CSV Export): 7 tasks
- Phase 8 (US6 - Projects Dashboard): 7 tasks
- Phase 9 (US7 - Inventory Dashboard): 6 tasks
- Phase 10 (US8 - Dashboard Export): 8 tasks
- Phase 11 (Polish): 11 tasks

**Tasks by User Story**:
- US1 (P1): 11 tasks
- US2 (P1): 11 tasks
- US3 (P2): 7 tasks
- US4 (P2): 7 tasks
- US5 (P2): 7 tasks
- US6 (P3): 7 tasks
- US7 (P3): 6 tasks
- US8 (P3): 8 tasks

**Parallel Opportunities**: 40 tasks marked [P] can run in parallel within their phase

**Independent Test Criteria**:
- US1: Export sales PDF, verify file download and decimal precision
- US2: View sales dashboard, verify line chart and date filtering
- US3: Export projects XLSX, verify spreadsheet opens correctly
- US4: View partners dashboard, verify pie chart and filtering
- US5: Export inventory CSV, verify file format and escaping
- US6: View projects dashboard, verify bar chart and tooltips
- US7: View inventory dashboard, verify stacked bar and filtering
- US8: Export dashboard data, verify file contains chart data

**Suggested MVP Scope**: User Stories 1 & 2 (Phases 1-4) - 41 tasks spanning setup, foundation, PDF export, and sales dashboard

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Backend tasks use existing ReportService queries (no schema changes)
- Frontend tasks extend existing report pages and create new dashboard pages
- Decimal precision must be maintained throughout backend → frontend → export pipeline
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence