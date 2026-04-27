# Tasks: Export Template Standardization

**Feature**: Export Template Standardization
**Branch**: `010-export-template-standardization`
**Implementation Strategy**: MVP focused on P1 (PDF exports) first, followed by P2 (Excel exports). Sequential implementation in `ExportService`.

## Phase 1: Setup

- [x] T001 [P] Create backend static images directory `backend/app/static/images`
- [x] T002 [P] Copy `new_civilization.png`, `logo.png` (as `rayon_energy.png`), and `stamp.png` from `frontend/public` to `backend/app/static/images`

## Phase 2: Foundational

- [x] T003 [P] Define styling constants (HEADER_COLOR, STRIPE_COLOR, etc.) in `backend/app/modules/reports/export_service.py`
- [x] T004 [P] Implement asset path resolver utility in `backend/app/modules/reports/export_service.py`

## Phase 3: [US1] Standardized PDF Layout (Priority: P1)

**Goal**: Apply dual-logo header and stamped footer to all PDF exports.
**Independent Test**: Generate any PDF report and verify logos, title centering, and footer stamp on the last page.

- [x] T005 [US1] Create canvas header function with dual logos and centered title in `backend/app/modules/reports/export_service.py`
- [x] T006 [US1] Create canvas footer function with "Sales Manager", "Signature", and stamp image in `backend/app/modules/reports/export_service.py`
- [x] T007 [US1] Implement dynamic field mapping (Mr, Site, Phone, Operation) for the header in `backend/app/modules/reports/export_service.py`
- [x] T008 [US1] Update `_generate_pdf_sync` to use `doc.build(onFirstPage=header, onLaterPages=header, canvasmaker=footer_logic)` pattern
- [x] T009 [US1] Apply blue-themed `TableStyle` (borders, header bg, striped rows) to `generate_pdf` in `backend/app/modules/reports/export_service.py`
- [x] T010 [US1] Verify PDF layout fidelity for Sales and Inventory reports

## Phase 4: [US2] Standardized Excel Layout (Priority: P2)

**Goal**: Include branding in Excel exports without breaking data functionality.
**Independent Test**: Export a report to Excel and verify logos in top rows and data table starting below.

- [x] T011 [US2] Update `_generate_xlsx_sync` to insert header logos using `worksheet.insert_image` in `backend/app/modules/reports/export_service.py`
- [x] T012 [US2] Update `_generate_xlsx_sync` to include report title and metadata in rows 1-6 of `backend/app/modules/reports/export_service.py`
- [x] T013 [US2] Offset the main data table to start at row 7 in `backend/app/modules/reports/export_service.py`
- [x] T014 [US2] Verify Excel exports for sorting and branding consistency

## Phase 5: Polish & Cross-Cutting

- [x] T015 [P] Optimize image scaling and resolution for both PDF and Excel exports
- [x] T016 [P] Finalize Arabic text alignment across all new template elements in `backend/app/modules/reports/export_service.py`

## Dependencies

1. US1 depends on Phase 1 & 2.
2. US2 depends on Phase 1 & 2.
3. Polish depends on US1 & US2.

## Parallel Execution Examples

- **Setup & Foundational**: T001, T002, T003 can be done in parallel.
- **US1 & US2 Development**: PDF (US1) and Excel (US2) logic are mostly independent and can be developed in parallel once the assets (Phase 1) are ready.
