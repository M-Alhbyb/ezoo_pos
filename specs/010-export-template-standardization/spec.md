# Feature Specification: Export Template Standardization

**Feature Branch**: `010-export-template-standardization`  
**Created**: 2026-04-22  
**Status**: Draft  
**Input**: User description: "Standardize PDF and Excel exports using the provided template with dual logos and stamp."

## Clarifications

### Session 2026-04-22
- Q: How should template fields (Mr., Site, Phone, Operation) be handled for generic reports? → A: Dynamically show/hide fields based on report type data.
- Q: How closely should Excel layout match the PDF? → A: Use a "Branded Data" approach (logos/title in top rows, clean data table below).
- Q: Should footer labels be configurable? → A: Hardcode as per the provided template image ("Sales Manager" and "Signature").
- Q: What visual style should be used for the data table? → A: Match the blue-themed aesthetic from the template (blue borders, blue header, light blue striping).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Standardized PDF Sales Report (Priority: P1)

As an administrator, I want to export sales reports as PDFs that feature a professional header with dual logos and a signed/stamped footer, so that the documents are official and brand-compliant for partners and customers.

**Why this priority**: Core requirement for professional documentation and branding requested by the user.

**Independent Test**: Can be tested by generating any PDF report (e.g., Sales Report) and verifying the visual presence and alignment of both logos in the header and the stamp in the footer.

**Acceptance Scenarios**:

1. **Given** the user is on the reports page, **When** they click "Export PDF" for a sales report, **Then** the generated PDF should display the "New Civilization" logo on the top left and the "Rayon Energy" logo on the top right.
2. **Given** a generated PDF report, **When** scrolling to the bottom of the last page, **Then** there should be placeholders for "Sales Manager" and "Signature" alongside the official circular stamp.

---

### User Story 2 - Standardized Excel Export (Priority: P2)

As an administrator, I want Excel exports to also include the dual logos and basic header information, so that even data-focused exports maintain professional branding.

**Why this priority**: Ensures consistency across all export formats as requested.

**Independent Test**: Can be tested by exporting any report to Excel and verifying the first few rows contain the logo images and report metadata.

**Acceptance Scenarios**:

1. **Given** an Excel export, **When** opened, **Then** the top of the sheet should contain the "New Civilization" and "Rayon Energy" logos as images.
2. **Given** an Excel export, **When** opened, **Then** the report title and date range should be clearly visible in the header rows above the data table.

---

### Edge Cases

- **Empty Data**: How does the system handle exports with zero records? (Should still show header/footer with "No data available" message).
- **Long Tables**: Does the header/footer repeat on every page of a multi-page PDF? (Header should ideally repeat or be on the first page; stamp should be on the final page).
- **Large Logos**: How does the system handle high-resolution logos to prevent huge file sizes or layout breaking? (Images should be scaled to fit predefined header areas).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST include the "New Civilization" logo on the top-left of every PDF and Excel export.
- **FR-002**: System MUST include the "Rayon Energy" logo on the top-right of every PDF and Excel export.
- **FR-003**: System MUST center the report title (e.g., "Sales Invoice", "Inventory Report") in the header area.
- **FR-004**: System MUST include a "Meta" section in the header with Date, Page Number, and dynamically mapped fields (e.g., Customer/Mr., Site, Phone, Operation) only when relevant data is available for the report.
- **FR-005**: System MUST include a footer in PDFs with the fixed Arabic labels "مدير المبيعات" (Sales Manager) and "التوقيع" (Signature).
- **FR-006**: System MUST include the circular "stamp" image in the PDF footer area.
- **FR-007**: System MUST use a blue-themed table style (blue borders, blue header background with white text, and light blue row striping) that aligns with the provided template aesthetics.
- **FR-008**: System MUST support Arabic text rendering correctly within the new template layout.

### Key Entities *(include if feature involves data)*

- **Export Template**: A configuration or service-level layout definition that specifies positions for logos, titles, and stamps.
- **Asset Manager**: Logic to retrieve logo and stamp files from the `frontend/public` directory (or a synced backend directory).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of PDF exports (Sales, Partners, Inventory, Customer Statements) use the new dual-logo header.
- **SC-002**: PDF generation time remains under 3 seconds for datasets up to 1000 rows.
- **SC-003**: Exported files (PDF/Excel) are under 5MB for standard report sizes.
- **SC-004**: Visual layout on exported PDFs matches the provided image template with >90% fidelity in positioning.

## Assumptions

- **Logo Availability**: Assumes `new_civilization.png`, `logo.png` (Rayon Energy), and `stamp.png` are available in a location accessible to the backend (e.g., `frontend/public` is shared or files are copied to `backend/app/static`).
- **Font Support**: Assumes Cairo font is used for Arabic text as per existing implementation.
- **Format Consistency**: Excel exports will use a "Branded Data" approach, placing logos and report titles in the top rows (1-6) while maintaining a standard, sortable data table starting below the header area.
- **Single Stamp**: The stamp is only required at the bottom of the document, not on every page if multi-page.
