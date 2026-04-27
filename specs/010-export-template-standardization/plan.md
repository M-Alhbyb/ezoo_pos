# Implementation Plan: Export Template Standardization

**Branch**: `010-export-template-standardization` | **Date**: 2026-04-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/010-export-template-standardization/spec.md`

## Summary

This feature standardizes all PDF and Excel exports by applying a professional, branded template. The new layout includes dual logos (New Civilization and Rayon Energy), a centered report title, a metadata section, a blue-themed data table, and a footer with official labels and a circular stamp. Implementation involves enhancing the backend `ExportService` to use custom ReportLab layouts and xlsxwriter formatting.

## Technical Context

**Language/Version**: Python 3.11 (Backend), TypeScript/Next.js 14 (Frontend)  
**Primary Dependencies**: ReportLab (PDF), xlsxwriter/pandas (Excel), arabic-reshaper, python-bidi  
**Storage**: PostgreSQL (settings for extra report fields)  
**Testing**: pytest (unit tests for PDF/Excel structure)  
**Target Platform**: Linux (server-side export generation)
**Project Type**: Web service (POS)  
**Performance Goals**: <3s generation for 1000 rows  
**Constraints**: Absolute image positioning in PDFs, sortable data in Excel  
**Scale/Scope**: All report modules (Sales, Inventory, Partners, Customers)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle VII: Backend Authority**: All export generation logic is confined to the backend. (PASS)
- **Principle I: Financial Accuracy**: Reports are generated purely from stored transaction data. (PASS)
- **Principle IX: Extensibility**: The template logic is decoupled from report data, allowing easy addition of future reports. (PASS)

## Project Structure

### Documentation (this feature)

```text
specs/010-export-template-standardization/
├── spec.md              # Requirement specification
├── plan.md              # This file
├── research.md          # Technical decisions (ReportLab, xlsxwriter)
├── data-model.md        # Export metadata and asset mapping
├── quickstart.md        # How to test the new exports
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── modules/
│   │   └── reports/
│   │       ├── export_service.py   # Main implementation
│   │       └── routes.py           # Endpoint updates
│   └── static/
│       └── images/                 # New location for logos/stamp
└── tests/
    └── modules/
        └── reports/
            └── test_exports.py     # New tests for layout validation
```

**Structure Decision**: Web application structure with backend-heavy logic for document generation.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
