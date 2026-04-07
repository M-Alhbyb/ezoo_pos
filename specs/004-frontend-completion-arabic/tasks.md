# Implementation Tasks: Frontend Completion with Arabic RTL

**Feature**: 004-frontend-completion-arabic
**Branch**: `004-frontend-completion-arabic`
**Status**: Ready for Implementation
**Created**: 2026-04-06

---

## Overview

Complete the EZOO POS frontend with full Arabic (RTL) translation and layout. This feature transforms all existing English interfaces into Arabic, adds missing pages, and ensures proper RTL rendering. Organized by user story for independent implementation and testing.

**Total Tasks**: 106
**User Stories**: 6
**Estimated Time**: 15-20 days

---

## Dependency Graph

**Story Completion Order** (each story is independently testable):

```
Setup/Foundation (Phase 1)
    │
    ├─── US1: Arabic Dashboard (Phase 2) ─────────────┐
    │                                                  │
    ├─── US2: Point of Sale (Phase 3) ────────────────┤
    │                                                  │
    ├─── US3: Inventory Management (Phase 4) ─────────┤──► Polish (Phase 9)
    │                                                  │
    ├─── US4: Project Management (Phase 5) ───────────┤
    │                                                  │
    ├─── US5: Partner Profit Distribution (Phase 6) ──┤
    │                                                  │
    └─── US6: Report Viewing (Phase 7) ────────────────┘
                                                       │
                               Settings & Expenses (Phase 8)
```

**Parallel Opportunities**:
- User Stories 1-6 can be implemented in parallel after Setup phase
- Each story has independent test criteria
- Polish phase requires all stories complete

---

## Implementation Strategy

**MVP Minimum**: US1 (Arabic Dashboard) + US2 (Point of Sale)
- Delivers core business value (Arabic interface for daily operations)
- Enables immediate user feedback
- Estimated time: 5-7 days

**Full MVP**: All 6 User Stories
- Delivers complete Arabic interface
- Enables comprehensive testing
- Estimated time: 15-20 days

---

## Phase1: Setup & Foundation

**Goal**: Create foundational Arabic constants, formatting utilities, and RTL configuration that all other phases depend on.

**Independent Test**: Verify constants compile, formatting functions produce correct output, RTL layout applied to root element.

### 1.1 Arabic Constants & Utilities

- [x] T001 Create Arabic constants file at `frontend/lib/constants/arabic.ts` with all UI text translations
- [x] T002 Create status enum translations at `frontend/lib/constants/status.ts` for project/inventory/payment statuses
- [x] T003 Create validation messages at `frontend/lib/constants/validation.ts` for form error messages
- [x] T004 [P] Create formatting utilities at `frontend/lib/utils/format.ts` with formatCurrency, formatDate, formatNumber, formatPercentage, formatDateTime functions
- [x] T005 [P] Create normalization utilities at `frontend/lib/utils/normalize.ts` with toWesternNumerals, toArabicNumerals, normalizeInput functions

### 1.2 RTL Configuration

- [x] T006 Update root layout at `frontend/app/layout.tsx` to add `lang="ar"` and `dir="rtl"` attributes
- [x] T007 Update Tailwind configuration at `frontend/tailwind.config.ts` to ensure RTL support with logical properties

### 1.3 Shared Components - RTL & Arabic

- [x] T008 Update ErrorBoundary at `frontend/components/shared/ErrorBoundary.tsx` to display Arabic error messages
- [x] T009 [P] Update ConnectionStatus at `frontend/components/shared/ConnectionStatus.tsx` to display Arabic connection status
- [x] T010 [P] Create LoadingSpinner component at `frontend/components/shared/LoadingSpinner.tsx` with Arabic loading text
- [x] T011 [P] Create EmptyState component at `frontend/components/shared/EmptyState.tsx` with Arabic empty states
- [x] T012 [P] Create ErrorMessage component at `frontend/components/shared/ErrorMessage.tsx` for Arabic error display
- [x] T013 [P] Create ConfirmModal component at `frontend/components/shared/ConfirmModal.tsx` with Arabic confirm/cancel buttons

---

## Phase 2: User Story 1 - Arabic Dashboard Access (P1)

**Story Goal**: Arabic-speaking business owner views dashboard with all labels in Arabic, RTL layout, and properly formatted numbers.

**Independent Test**: Open the application, navigate to dashboard, verify all text elements display in Arabic, layout is RTL, charts show Arabic labels, currency displays ج.س.

### 2.1 Layout Components - RTL

- [x] T014 [US1] Update DashboardLayout at `frontend/components/dashboard/DashboardLayout.tsx` for RTL-aware layout
- [x] T015 [US1] Create/get Sidebar component at `frontend/components/layout/Sidebar.tsx` with RTL navigation (sidebar on right)
- [x] T016 [US1] Create/get Header component at `frontend/components/layout/Header.tsx` with RTL header layout
- [x] T017 [US1] Create PageHeader component at `frontend/components/layout/PageHeader.tsx` for RTL page titles

### 2.2 Dashboard Page - Arabic

- [x] T018 [US1] Update Dashboard page at `frontend/app/dashboard/page.tsx` to use ARABIC constants for all labels
- [x] T019 [US1] Replace summary card labels with Arabic translations (إجمالي الإيرادات، المشاريع النشطة، الشركاء، المنتجات المنخفضة)
- [x] T020 [US1] Update chart components to use Arabic axis labels and tooltips
- [x] T021 [US1] Update quick navigation area with Arabic labels

### 2.3 Chart Components - RTL & Arabic

- [x] T022 [US1] Update LineChart at `frontend/components/charts/LineChart.tsx` for RTL rendering with Arabic labels
- [x] T023 [US1] Update BarChart at `frontend/components/charts/BarChart.tsx` for RTL rendering with Arabic labels
- [x] T024 [US1] Update PieChart at `frontend/components/charts/PieChart.tsx` with Arabic labels
- [x] T025 [US1] Update StackedBarChart at `frontend/components/charts/StackedBarChart.tsx` for RTL rendering with Arabic labels
- [X] T026 [US1] Update chart index exports at `frontend/components/charts/index.tsx`

### 2.4 Export Components

- [x] T027 [US1] Update ExportButton at `frontend/components/dashboard/ExportButton.tsx` with Arabic labels
- [x] T028 [US1] Update DatePicker at `frontend/components/dashboard/DatePicker.tsx` with Arabic labels (من تاريخ، إلى تاريخ)

---

## Phase 3: User Story 2 - Point of Sale Transaction (P1)

**Story Goal**: Arabic-speaking cashier processes complete sale transaction with Arabic interface, views sale history.

**Independent Test**: Complete a full sale transaction from product selection to sale completion, verify product grid, cart, fees, breakdown, and history all display in Arabic.

### 3.1 POS Terminal - Arabic

- [X] T029 [US2] Update POS page at `frontend/app/pos/page.tsx` to use ARABIC constants for all labels
- [X] T030 [US2] Update ProductGrid at `frontend/components/pos/ProductGrid.tsx` with RTL layout and Arabic product display
- [X] T031 [US2] Update ProductSearch at `frontend/components/pos/ProductSearch.tsx` with Arabic placeholder text
- [X] T032 [US2] Update POSCart at `frontend/components/pos/POSCart.tsx` with Arabic labels (المنتج، الكمية، السعر، الإجمالي)
- [X] T033 [US2] Update SaleBreakdown at `frontend/components/pos/SaleBreakdown.tsx` with Arabic labels (المجموع الفرعي، الرسوم، ضريبة القيمة المضافة، الإجمالي)

### 3.2 Fee Editor & Payment - Arabic

- [X] T034 [US2] Update FeeEditor at `frontend/components/pos/FeeEditor.tsx` with Arabic fee type names (شحن، تركيب، مخصص)
- [X] T035 [US2] Update PaymentMethodSelect at `frontend/components/pos/PaymentMethodSelect.tsx` with Arabic labels
- [X] T036 [US2] Update ConfirmButton at `frontend/components/pos/ConfirmButton.tsx` with Arabic confirm text
- [X] T037 [US2] Update ReversalModal at `frontend/components/pos/ReversalModal.tsx` with Arabic reversal labels

### 3.3 Sale History - New Pages

- [X] T038 [US2] Create Sale History page at `frontend/app/pos/history/page.tsx` listing all past sales with Arabic labels
- [X] T039 [US2] Create Sale Detail page at `frontend/app/pos/history/[saleId]/page.tsx` showing complete transaction breakdown in Arabic

---

## Phase 4: User Story 3 - Inventory Management (P2)

**Story Goal**: Arabic-speaking warehouse manager restocks products using dropdown selector (not UUID), views inventory log with Arabic reason labels.

**Independent Test**: Select product from dropdown, restock items, view inventory log, verify all movement reasons display in Arabic.

### 4.1 Inventory Page - Arabic

- [X] T040 [US3] Update Inventory page at `frontend/app/inventory/page.tsx` to use ARABIC constants for all labels
- [X] T041 [US3] Create ProductSelector component at `frontend/components/inventory/ProductSelector.tsx` as dropdown for product selection (replaces UUID input)
- [X] T042 [US3] Update inventory movement reasons to display in Arabic (مبيعة، إعادة تخزين، تعديل، إلغاء)
- [X] T043 [US3] Update restock form with Arabic labels and success message
- [X] T044 [US3] Update adjustment form with Arabic labels and success message

---

## Phase 5: User Story 4 - Project Management (P2)

**Story Goal**: Arabic-speaking project manager creates project, assigns items/expenses, marks complete, views project details with all labels in Arabic.

**Independent Test**: Create project, add items, complete it, view project details, verify all labels and status badges display in Arabic with currency formatting.

### 5.1 Projects List - Arabic

- [X] T045 [US4] Update Projects page at `frontend/app/projects/page.tsx` to use ARABIC constants for all labels
- [X] T046 [US4] Update project status badges to display Arabic status (قيد التنفيذ، مكتمل)
- [X] T047 [US4] Add status filter dropdown with Arabic labels (الكل، قيد التنفيذ، مكتمل)
- [X] T048 [US4] Update ProjectModal at `frontend/components/projects/ProjectModal.tsx` with Arabic field labels

### 5.2 Project Detail - New Page

- [X] T049 [US4] Create Project Detail page at `frontend/app/projects/[projectId]/page.tsx` showing items and expenses breakdown in Arabic
- [X] T050 [US4] Add project completion confirmation dialog with Arabic text
- [X] T051 [US4] Display profit breakdown with ج.س formatting in project detail

---

## Phase 6: User Story 5 - Partner Profit Distribution (P2)

**Story Goal**: Arabic-speaking business owner views partners, distributes profits, views distribution history with all labels in Arabic.

**Independent Test**: Add partner, run profit distribution, view partner history, verify breakdown and amounts display in Arabic with currency formatting.

### 6.1 Partners List - Arabic

- [X] T052 [US5] Update Partners page at `frontend/app/partners/page.tsx` to use ARABIC constants for all labels
- [X] T053 [US5] Update PartnerModal at `frontend/components/partners/PartnerModal.tsx` with Arabic field labels
- [X] T054 [US5] Update DistributeModal at `frontend/components/partners/DistributeModal.tsx` with Arabic labels and project selection
- [X] T055 [US5] Update distribution result display to show Arabic breakdown with currency formatting

### 6.2 Partner History - New Page

- [X] T056 [US5] Create Partner History page at `frontend/app/partners/[partnerId]/page.tsx` showing distribution history in Arabic

---

## Phase 7: User Story 6 - Report Viewing and Export (P3)

**Story Goal**: Arabic-speaking manager views reports with Arabic labels, applies date filters, exports to CSV/Excel/PDF with Arabic content.

**Independent Test**: Navigate to each report, verify Arabic labels, apply date filter, export to each format, verify Arabic content in exports.

### 7.1 Sales Report - Arabic

- [X] T057 [US6] Update Sales Report page at `frontend/app/dashboard/reports/sales/page.tsx` to use ARABIC constants
- [X] T058 [US6] Replace summary card labels with Arabic (إجمالي الإيرادات، صافي الربح، عدد المبيعات، متوسط هامش الربح)
- [X] T059 [US6] Update DataTable at `frontend/components/reports/DataTable.tsx` with Arabic column headers
- [X] T060 [US6] Add chart visualization to sales report with Arabic labels

### 7.2 Projects Report - Arabic

- [X] T061 [US6] Update Projects Report page at `frontend/app/dashboard/reports/projects/page.tsx` with Arabic labels
- [X] T062 [US6] Replace project summary labels with Arabic
- [X] T063 [US6] Add chart visualization to projects report with Arabic labels

### 7.3 Partners Report - Arabic

- [X] T064 [US6] Update Partners Report page at `frontend/app/dashboard/reports/partners/page.tsx` with Arabic labels
- [X] T065 [US6] Replace payout summary labels with Arabic
- [X] T066 [US6] Add chart visualization to partners report with Arabic labels

### 7.4 Inventory Report - Arabic

- [X] T067 [US6] Update Inventory Report page at `frontend/app/dashboard/reports/inventory/page.tsx` with Arabic labels
- [X] T068 [US6] Replace movement summary labels with Arabic
- [X] T069 [US6] Add chart visualization to inventory report with Arabic labels

### 7.5 Report Components

- [X] T070 [US6] Update ExportButtonGroup at `frontend/components/reports/ExportButtonGroup.tsx` with Arabic export labels
- [X] T071 [US6] Update ExportCSVButton at `frontend/components/reports/ExportCSVButton.tsx` with Arabic labels
- [X] T072 [US6] Update ExportExcelButton at `frontend/components/reports/ExportExcelButton.tsx` with Arabic labels
- [X] T073 [US6] Update ExportPDFButton at `frontend/components/reports/ExportPDFButton.tsx` with Arabic labels
- [X] T074 [US6] Update ExportProgressModal at `frontend/components/reports/ExportProgressModal.tsx` with Arabic progress messages

---

## Phase 8: Settings, Products & Categories

**Goal**: Complete remaining modules with Arabic interface and add missing pages.

### 8.1 Products - Arabic

- [x] T075 Update Products page at `frontend/app/products/page.tsx` to use ARABIC constants for all labels
- [x] T076 Update ProductModal at `frontend/components/products/ProductModal.tsx` with Arabic field labels
- [x] T077 Update ProductForm at `frontend/components/products/ProductForm.tsx` with Arabic form labels
- [x] T078 Update ProductList at `frontend/components/products/ProductList.tsx` with Arabic table headers
- [x] T079 Update CategoryFilter at `frontend/components/products/CategoryFilter.tsx` with Arabic category names

### 8.2 Categories - New Page

- [x] T080 Create Categories page at `frontend/app/categories/page.tsx` with full CRUD interface in Arabic
- [x] T081 Create CategoryModal component for add/edit categories with Arabic labels
- [x] T082 Create CategoryList component for categories table with Arabic headers

### 8.3 Settings - Arabic

- [x] T083 Update Settings page at `frontend/app/settings/page.tsx` to use ARABIC constants for all labels
- [x] T084 Update PaymentMethodManager at `frontend/components/settings/PaymentMethodManager.tsx` with Arabic labels
- [x] T085 Update FeePresetManager at `frontend/components/settings/FeePresetManager.tsx` with Arabic labels
- [x] T086 Update SystemSettingsManager at `frontend/components/settings/SystemSettingsManager.tsx` with Arabic labels

### 8.4 Expenses - New Page

- [x] T087 Create Expenses page at `frontend/app/expenses/page.tsx` with expense management interface in Arabic
- [x] T088 Create ExpenseModal component for add/edit expenses with Arabic labels
- [x] T089 Create ExpensesList component for expenses table with Arabic headers

---

## Phase 9: Polish & Cross-Cutting

**Goal**: Final review, export testing, and comprehensive Arabic verification across all pages.

### 9.1 Export Testing

- [x] T090 Test CSV export functionality verifies Arabic headers and content render correctly
- [x] T091 Test Excel export functionality verifies Arabic headers and content render correctly
- [x] T092 Configure PDF Arabic font support in backend for proper Arabic text rendering
- [x] T093 Test PDF export functionality verifies RTL layout and Arabic text render correctly

### 9.2 Products Page - Enhancements

- [x] T094 Replace UUID input in inventory page with searchable product dropdown
- [x] T095 Add product image placeholder handling for missing images in Arabic context

### 9.3 Visual Review

- [x] T096 Review all pages for RTL layout correctness (sidebar position, text alignment, icon mirroring)
- [x] T097 Review all pages for Arabic text rendering (fonts, spacing, truncation)
- [x] T098 Review all forms for RTL input direction and Arabic labels
- [x] T099 Review all modals for Arabic content and RTL layout

### 9.4 Final Verification

- [x] T100 Verify all currency values display with ج.س symbol and Arabic numerals
- [x] T101 Verify all dates display with Arabic month names
- [x] T102 Verify all error messages display in Arabic
- [x] T103 Verify all success messages display in Arabic
- [x] T104 Verify all empty states display Arabic messages
- [x] T105 Verify WebSocket real-time updates display Arabic content
- [x] T106 Final review: confirm zero hardcoded English text remains in codebase

---

## Parallel Execution Examples

### By US (User Story)

**US1 (Dashboard) team can work independently:**
```bash
git checkout -b feature/arabic-dashboard
# Implement T014-T028
# Test: Open dashboard, verify Arabic labels, RTL layout, charts
```

**US2 (POS) team can work independently after US1:**
```bash
git checkout -b feature/arabic-pos
# Implement T029-T039
# Test: Complete sale transaction, verify all POS interactions in Arabic
```

**US3 (Inventory) team can work in parallel with US1&US2:**
```bash
git checkout -b feature/arabic-inventory
# Implement T040-T044
# Test: Restock from dropdown, view log with Arabic reasons
```

### By Component Type

**Frontend developers can parallelize:**
- Developer A: All pages (T018, T029, T040, T045, T052, T057-T069)
- Developer B: All components (T022-T026, T030-T037, T041-T044)
- Developer C: All constants and utilities (T001-T005)

---

## Validation Checklist

### US1 - Arabic Dashboard Access
- [ ] Dashboard displays Arabic labels (إجمالي الإيرادات, المشاريع النشطة, الشركاء, المنتجات المنخفضة)
- [ ] Charts render with Arabic axis labels and RTL
- [ ] Sidebar appears on right side
- [ ] Currency displays with ج.س symbol

### US2 - Point of Sale Transaction
- [ ] Product grid displays Arabic product names
- [ ] Cart displays Arabic labels (المنتج, الكمية, السعر, الإجمالي)
- [ ] Fee types display in Arabic (شحن, تركيب, مخصص)
- [ ] Sale history lists past transactions with Arabic labels
- [ ] Sale detail shows complete breakdown in Arabic

### US3 - Inventory Management
- [ ] Product dropdown shows product names (not UUIDs)
- [ ] Movement reasons display in Arabic (مبيعة, إعادة تخزين, تعديل, إلغاء)
- [ ] Restock success message in Arabic
- [ ] Adjustment success message in Arabic

### US4 - Project Management
- [ ] Projects list displays Arabic status badges
- [ ] Project detail shows items/expenses breakdown
- [ ] Completion confirmation dialog in Arabic
- [ ] Profit displays with ج.س formatting

### US5 - Partner Profit Distribution
- [ ] Partners list displays Arabic labels
- [ ] Distribution result shows Arabic breakdown
- [ ] Partner history shows past distributions in Arabic

### US6 - Report Viewing and Export
- [ ] All reports display Arabic summary cards
- [ ] Date pickers display Arabic labels (من تاريخ, إلى تاريخ)
- [ ] CSV export includes Arabic headers
- [ ] Excel export includes Arabic content
- [ ] PDF renders Arabic text with RTL

---

## Notes

- All tasks follow the strict checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
- Tasks marked with `[P]` can be parallelized (different files, no dependencies)
- Tasks marked with `[US#]` belong to specific User Story
- Each User Story phase is independently testable
- MVP scope: Implement US1 + US2 first for core business value