# Feature Specification: Frontend Completion with Arabic RTL

**Feature Branch**: `004-frontend-completion-arabic`
**Created**: 2026-04-06
**Status**: Draft
**Input**: Complete frontend implementation for EZOO POS with Arabic RTL support

---

## User Scenarios & Testing

### User Story 1 - Arabic Dashboard Access (Priority: P1)

An Arabic-speaking business owner opens the EZOO POS web application to view their daily business performance. They see a fully Arabic interface with all labels, buttons, and data displayed in Arabic. The dashboard shows summary cards (إجمالي الإيرادات، المشاريع النشطة، الشركاء، المنتجات المنخفضة) and charts with Arabic labels. The layout flows from right to left, with the navigation sidebar on the right side. All numerical values display with proper Arabic formatting.

**Why this priority**: This is the core user experience - the client requires Arabic-only interface. Without this, the entire system is unusable for the target user.

**Independent Test**: Open the application, navigate to the dashboard, and verify all text elements display in Arabic, layout is RTL, and charts show Arabic labels.

**Acceptance Scenarios**:

1. **Given** the user opens the application, **When** they view the dashboard, **Then** all summary card labels display in Arabic (e.g.,"إجمالي الإيرادات" instead of "Total Revenue")
2. **Given** the user views the dashboard, **When** they see chart data, **Then** all chart axes, legends, and tooltips display in Arabic
3. **Given** the user views any page, **When** they observe the layout, **Then** the sidebar appears on the right, content flows right-to-left, and text is right-aligned
4. **Given** the user views monetary values, **When** they see currency amounts, **Then** values display with ر.س symbol and proper Arabic numerical formatting

---

### User Story 2 - Point of Sale Transaction (Priority: P1)

An Arabic-speaking cashier needs to process a sale. They open the POS page, see products in a grid with Arabic names, add items to the cart, apply fees if needed, select a payment method, and complete the sale. The entire process displays in Arabic, including error messages and success confirmations. After completion, they can view the sale in history.

**Why this priority**: POS is the core business function - processing sales is the primary revenue activity.

**Independent Test**: Complete a full sale transaction from product selection to sale completion, verify all interactions are in Arabic.

**Acceptance Scenarios**:

1. **Given** the user opens the POS page, **When** they view the product grid, **Then** product names and categories display in Arabic
2. **Given** items are in the cart, **When** the user views the breakdown, **Then** subtotal, fees, VAT, and total labels display in Arabic
3. **Given** the user completes a sale, **When** the sale processes successfully, **Then** a success message "تمت العملية بنجاح" appears
4. **Given** the user makes an error (e.g., insufficient stock), **When** an error occurs, **Then** an Arabic error message displays explaining the issue
5. **Given** the user wants to view past sales, **When** they navigate to sale history, **Then** all sale records display with Arabic labels

---

### User Story 3 - Inventory Management (Priority: P2)

An Arabic-speaking warehouse manager needs to restock products and view inventory levels. They open the inventory page, see low-stock alerts in Arabic, select products from a dropdown (not manual UUID input), and process restocks. The inventory log shows all movements with Arabic reason labels.

**Why this priority**: Inventory management is essential for operations but secondary to sales processing.

**Independent Test**: Select a product from dropdown, restock items, and view the inventory log with Arabic labels.

**Acceptance Scenarios**:

1. **Given** the user opens inventory page, **When** they view low stock alerts, **Then** product names and stock levels display in Arabic
2. **Given** the user needs to restock, **When** they select a product, **Then** a dropdown shows products with Arabic names instead of requiring UUID input
3. **Given** the user views inventory log, **When** they see movement reasons, **Then** reasons display in Arabic (مبيعة، إعادة تخزين، تعديل، إلغاء)
4. **Given** the user submits a restock, **When** the operation succeeds, **Then** "تمت إعادة التخزين بنجاح" displays

---

### User Story 4 - Project Management (Priority: P2)

An Arabic-speaking project manager creates a new project, assigns items and expenses, tracks project status, and marks it complete. All project-related interfaces display in Arabic with full RTL layout. Project profits calculate automatically and display with Arabic currency formatting.

**Why this priority**: Projects are important for custom order tracking but can operate independently.

**Independent Test**: Create a project, add items, complete it, and verify all Arabic labels and calculations.

**Acceptance Scenarios**:

1. **Given** the user opens projects page, **When** they view existing projects, **Then** project names, status badges, and financials display in Arabic
2. **Given** the user creates a new project, **When** they fill the form, **Then** all field labels are in Arabic (اسم المشروع، سعر البيع، المنتجات، المصاريف)
3. **Given** a project has items and expenses, **When** viewing project details, **Then** the profit breakdown shows all amounts with ر.س formatting
4. **Given** the user completes a project, **When** they click complete button, **Then** confirmation dialog shows "هل أنت متأكد منإتمام المشروع؟" and status changes to "مكتمل"

---

### User Story 5 - Partner Profit Distribution (Priority: P2)

An Arabic-speaking business owner distributes profits among partners. They view the partners list, select profit distribution, see the breakdown per partner, and confirm. All partner names and amounts display in Arabic. Distribution history shows past payouts.

**Why this priority**: Partner management is important for profit sharing but depends on project completion.

**Independent Test**: Add a partner, run profit distribution, and verify the Arabic breakdown and success message.

**Acceptance Scenarios**:

1. **Given** the user opens partners page, **When** they view partner list, **Then** partner names, share percentages, and investment amounts display in Arabic
2. **Given** the user distributes profits, **When** they select distribution criteria, **Then** all labels are in Arabic (المشاريع، الفترة)
3. **Given** distribution completes, **When** results display, **Then** a breakdown shows each partner's share in Arabic with currency formatting
4. **Given** the user views partner history, **When** they select a partner, **Then** past distributions display with dates and amounts in Arabic

---

### User Story 6 - Report Viewing and Export (Priority: P3)

An Arabic-speaking manager views reports (sales, projects, partners, inventory) with Arabic labels and charts. They can filter by date range and export to CSV, Excel, or PDF with Arabic content properly rendered.

**Why this priority**: Reports are important for analysis but can be addressed after core functionality.

**Independent Test**: Navigate to each report, verify Arabic labels, apply date filter, and export to each format.

**Acceptance Scenarios**:

1. **Given** the user opens sales report,**When** they view summary cards and table, **Then** all labels display in Arabic (إجمالي الإيرادات، صافي الربح، عدد المبيعات، متوسط هامش الربح)
2. **Given** the user views any report, **When** they apply date filter, **Then** date picker labels are in Arabic (من تاريخ، إلى تاريخ)
3. **Given** the user exports to CSV, **When** the file downloads, **Then** CSV contains Arabic column headers and data
4. **Given** the user exports to PDF, **When** the file opens, **Then** PDF renders Arabic text correctly with RTL layout

---

### Edge Cases

- What happens when a user enters mixed Arabic/English text in product names?
  → Display as entered, labels remain Arabic
- What happens when Arabic font fails to load?
  → Fallback to system Arabic font (most systems have Arabic support)
- What happens when PDF export contains Arabic text?
  → Ensure Arabic font subset is embedded in PDF
- What happens when numbers are entered in Arabic-Indic numerals in forms?
  → Accept both, convert to Western for storage, display in Arabic format
- What happens when RTL layout breaks on a specific component?
  → Use CSS logical properties for automatic RTL handling
- What happens when sale history has no results?
  → Display empty state message in Arabic: "لا توجد مبيعات بعد."

---

## Requirements

### Functional Requirements

**ARABIC TRANSLATION & RTL:**

- **FR-001**: System MUST display all UI text in Standard Arabic (الفصحى)
- **FR-002**: System MUST implement RTL (Right-to-Left) layout throughout the application
- **FR-003**: System MUST set `lang="ar"` and `dir="rtl"` on the root HTML element
- **FR-004**: System MUST use CSS logical properties (start/end) instead of physical (left/right) for automatic RTL support
- **FR-005**: System MUST format all currency values with Arabic numerals and ر.س symbol
- **FR-006**: System MUST format all dates in Arabic format (e.g., ١٥ يناير ٢٠٢٦)

**DASHBOARD:**

- **FR-007**: Dashboard MUST display four summary cards with Arabic labels
- **FR-008**: Dashboard MUST show four charts (sales, projects, partners, inventory) with Arabic labels
- **FR-009**: Charts MUST render correctly in RTL mode with right-to-left data flow
- **FR-010**: Dashboard MUST link to corresponding reports and modules in Arabic

**POINT OF SALE:**

- **FR-011**: POS page MUST display product grid with Arabic product names and categories
- **FR-012**: POS cart MUST show item breakdown with Arabic labels (المنتج، الكمية، السعر، الإجمالي)
- **FR-013**: POS MUST allow adding custom fees with Arabic fee type names (شحن، تركيب، مخصص)
- **FR-014**: POS MUST display payment method dropdown with Arabic method names
- **FR-015**: POS MUST show sale breakdown with Arabic labels (المجموع الفرعي، الرسوم، ضريبة القيمة المضافة، الإجمالي)
- **FR-016**: System MUST create a sale history page listing all past sales
- **FR-017**: System MUST provide a sale detail view showing complete transaction breakdown

**PRODUCTS & CATEGORIES:**

- **FR-018**: Products page MUST display product list with Arabic labels
- **FR-019**: Product create/edit modal MUST have Arabic field labels
- **FR-020**: System MUST provide a dedicated categories management page
- **FR-021**: Categories CRUD MUST operate with Arabic labels

**INVENTORY:**

- **FR-022**: Inventory page MUST display low-stock alerts with Arabic messages
- **FR-023**: Inventory MUST use product dropdown/autocomplete instead of manual UUID input
- **FR-024**: Inventory log MUST display movement reasons in Arabic
- **FR-025**: Restock and adjustment forms MUST have Arabic labels

**PROJECTS:**

- **FR-026**: Projects page MUST display project list with Arabic status labels
- **FR-027**: Project create modal MUST have Arabic field labels
- **FR-028**: System MUST provide project detail view with items and expenses breakdown
- **FR-029**: Project completion MUST show Arabic confirmation dialog
- **FR-030**: Projects MUST support status filtering (الكل، قيد التنفيذ، مكتمل)

**PARTNERS:**

- **FR-031**: Partners page MUST display partner list with Arabic labels
- **FR-032**: Partner create/edit modal MUST have Arabic field labels
- **FR-033**: Distribution modal MUST display project selection in Arabic
- **FR-034**: Distribution result MUST show breakdown per partner in Arabic
- **FR-035**: System MUST provide partner history view showing past distributions

**REPORTS:**

- **FR-036**: Sales report MUST display summary cards and table with Arabic labels
- **FR-037**: Projects report MUST display project summary with Arabic labels
- **FR-038**: Partners report MUST display payout summary with Arabic labels
- **FR-039**: Inventory report MUST display movement summary with Arabic labels
- **FR-040**: All reports MUST support date filtering with Arabic date picker labels

**EXPORT:**

- **FR-041**: CSV export MUST include Arabic column headers and data
- **FR-042**: Excel export MUST include Arabic column headers and data
- **FR-043**: PDF export MUST render Arabic text with RTL layout
- **FR-044**: Export progress modal MUST display Arabic progress messages

**SHARED COMPONENTS:**

- **FR-045**: Error boundary MUST display Arabic error messages
- **FR-046**: Loading states MUST display Arabic loading text
- **FR-047**: Empty states MUST display Arabic placeholder messages
- **FR-048**: Confirmation dialogs MUST have Arabic confirm/cancel buttons

### Key Entities

- **ArabicText**: All user-facing text elements that must be translated to Standard Arabic
- **RTLLayout**: Layout configuration that reverses horizontal flow for Arabic reading direction
- **CurrencyValue**: Monetary values formatted with Arabic numerals and ر.س symbol
- **DateValue**: Date values formatted with Arabic month names and Arabic-Indic numerals
- **ReportData**: Aggregated data structures for sales, projects, partners, and inventory reports
- **NavigationItem**: Sidebar/menu items with Arabic labels and RTL-aware icons

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: All UI elements (100%) display in Arabic with correct RTL layout
- **SC-002**: All pages load within 3 seconds on standard 4G connection
- **SC-003**: Currency values display correctly with Arabic numerals (٠-٩) and ر.س symbol
- **SC-004**: Date values display in Arabic format (e.g., ١٥ يناير ٢٠٢٦)
- **SC-005**: CSV, XLSX, and PDF exports contain properly rendered Arabic content
- **SC-006**: Charts render correctly in RTL mode with Arabic axis labels and tooltips
- **SC-007**: Form submissions validate input and display errors in Arabic
- **SC-008**: Navigation sidebar displays on right side with RTL menu items
- **SC-009**: All backend endpoints are properly integrated with Arabic responses
- **SC-010**: Zero (0) hardcoded English text remains in the codebase
- **SC-011**: Product dropdown shows product names instead of requiring UUID input
- **SC-012**: Sale history page lists all past transactions with Arabic labels
- **SC-013**: Project detail view shows complete item and expense breakdown
- **SC-014**: Partner history shows distribution history with Arabic labels

---

## Assumptions

- Backend API endpoints remain unchanged and return the same data structures
- No authentication/authorization system changes are required (or handled separately)
- Arabic content uses Standard Arabic (الفصحى) forall text
- Currency is Saudi Riyal (SAR) with ر.س symbol
- Date format follows Gregorian calendar with Arabic month names
- All users are Arabic-speaking (no multi-language switching required)
- RTL support is browser-native (modern browsers support RTL natively)
- Export files (CSV, XLSX, PDF) will contain Arabic content with proper encoding
- WebSocket real-time updates display in Arabic
- Form inputs accept both Western and Arabic-Indic numerals
- Arabic fonts are available via system fonts or web fonts
- The backend GET /api/projects endpoint must be added or use dashboard data for project listing