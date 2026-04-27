# Research: Export Template Standardization

## Decision 1: ReportLab Layout (PDF)
- **Decision**: Use a custom `Canvas` header/footer function with `SimpleDocTemplate.build(onFirstPage=..., onLaterPages=...)`.
- **Rationale**: The dual-logo header and the stamped footer require precise positioning that is difficult to manage with just `Flowables` in a `SimpleDocTemplate`. A canvas-level draw function allows pixel-perfect placement of logos and stamps.
- **Alternatives considered**: 
    - Using a `Table` for the header: Easier but less flexible for absolute positioning of logos on edges.
    - Using `PageTemplate`: Good for repeating headers, but `Canvas` callbacks are simpler for this specific requirement.

## Decision 2: Excel Layout (XLSX)
- **Decision**: Use `xlsxwriter`'s `insert_image` method in the top rows (1-5).
- **Rationale**: This allows us to place logos at the top without interfering with the data table starting at row 7. It satisfies the "Branded Data" requirement.
- **Alternatives considered**:
    - Header/Footer feature of Excel: Images in headers are often invisible until print-preview, which doesn't meet the requirement of being "visible when opened".

## Decision 3: Asset Management
- **Decision**: Copy the logos and stamp from `frontend/public` to a new `backend/app/static/images` directory.
- **Rationale**: The backend needs local file access to these images for ReportLab and xlsxwriter to process them during generation. Relying on the frontend path (especially if running in separate containers or environments) is unreliable.
- **Alternatives considered**:
    - Serving images via URL: Too slow and requires network access during export generation.
    - Symlinks: Fragile in containerized or cross-platform environments.

## Decision 4: Table Styling (ReportLab)
- **Decision**: Use `TableStyle` with specific RGB values for the "Blue" theme.
- **Rationale**: We will define a set of constants (HEADER_COLOR, STRIPE_COLOR, BORDER_COLOR) to ensure consistency across all reports.
