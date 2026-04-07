# Implementation Plan: Frontend Completion with Arabic RTL

**Branch**: `004-frontend-completion-arabic` | **Date**: 2026-04-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-frontend-completion-arabic/spec.md`

---

## Summary

Complete the EZOO POS frontend with full Arabic (RTL) translation and layout. This is a frontend-only feature that transforms all existing English interfaces into Arabic, adds missing pages (sale history, project details, partner history, categories, expenses), and ensures proper RTL rendering across all components. No backend changes required except PDF Arabic font configuration.

**Technical Approach**: Use hardcoded Arabic constants (no i18n framework), Tailwind CSS logical properties for RTL, native `Intl` API for formatting, and create new pages for missing functionality.

---

## Technical Context

**Language/Version**: TypeScript 5, Next.js 14 (existing)
**Primary Dependencies**: React 18, TailwindCSS 3.4, Recharts (existing)
**Storage**: PostgreSQL (unchanged - frontend only)
**Testing**: Jest/Vitest (existing)
**Target Platform**: Web browser (modern browsers with RTL support)
**Project Type**: Web application (frontend changes only)
**Performance Goals**: <3s page load, RTL rendering <100ms
**Constraints**: Must maintain existing API contracts, no backend logic changes
**Scale/Scope**: ~50+ components, ~15 pages, ~12 new pages

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### II. Single Source of Truth ✓

**Status**: PASS

The frontend consumes backend API responses without modification. All financial calculations remain in the backend. No duplicated financial logic in frontend.

### VII. Backend Authority ✓

**Status**: PASS

All business logic remains in FastAPI backend. Frontend is a presentation layer only. No validation logic changes required.

### V. Simplicity of Use ✓

**Status**: PASS

Arabic interface maintains the same workflow simplicity. Sale completion requires minimal clicks. Financial breakdowns visible on every transaction screen.

### VI. Data Integrity ✓

**Status**: PASS

No changes to data persistence. Frontend displays data as received from backend. Form inputs normalized to Western numerals before API submission.

### VIII. Input Validation ✓

**Status**: PASS

Input normalization accepts both Western and Arabic-Indic numerals. Backend validation remains authoritative.

### IX. Extensibility by Design ✓

**Status**: PASS

No schema changes. New pages consume existing API endpoints. Translation constants are easily extensible.

---

## Project Structure

### Documentation (this feature)

```text
specs/004-frontend-completion-arabic/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Technical research and decisions
├── data-model.md        # Arabic constants and component architecture
├── quickstart.md        # Developer quickstart guide
├── contracts/
│   └── api-contracts.md # API contracts (no changes)
└── tasks.md             # Implementation tasks (created by /speckit.tasks)
```

### Source Code (repository root)

```text
frontend/
├── app/
│   ├── layout.tsx              # UPDATE: Add lang="ar" dir="rtl"
│   ├── page.tsx                # UPDATE: Arabic text
│   ├── dashboard/
│   │   ├── page.tsx            # UPDATE: Arabic text
│   │   └── reports/
│   │       ├── sales/page.tsx    # UPDATE: Arabic text
│   │       ├── projects/page.tsx # UPDATE: Arabic text
│   │       ├── partners/page.tsx  # UPDATE: Arabic text
│   │       └── inventory/page.tsx # UPDATE: Arabic text
│   ├── pos/
│   │   ├── page.tsx            # UPDATE: Arabic text
│   │   └── history/             # NEW
│   │       ├── page.tsx          # NEW: Sale history list
│   │       └── [saleId]/page.tsx # NEW: Sale detail view
│   ├── products/page.tsx       # UPDATE: Arabic text
│   ├── categories/page.tsx     # NEW: Categories management
│   ├── inventory/page.tsx      # UPDATE: Arabic text, dropdown
│   ├── projects/
│   │   ├── page.tsx            # UPDATE: Arabic text
│   │   └── [projectId]/page.tsx  # NEW: Project detail view
│   ├── partners/
│   │   ├── page.tsx            # UPDATE: Arabic text
│   │   └── [partnerId]/page.tsx # NEW: Partner history view
│   ├── settings/page.tsx       # UPDATE: Arabic text
│   └── expenses/page.tsx        # NEW: Expenses management│
├── components/
│   ├── shared/               # UPDATE: All components Arabic
│   ├── layout/               # UPDATE: RTL layout
│   ├── charts/               # UPDATE: RTL-aware
│   ├── pos/                  # UPDATE: Arabic text
│   ├── products/             # UPDATE: Arabic text
│   ├── inventory/             # UPDATE: Arabic text, dropdown
│   ├── projects/              # UPDATE: Arabic text
│   ├── partners/              # UPDATE: Arabic text
│   ├── reports/              # UPDATE: Arabic text
│   └── settings/              # UPDATE: Arabic text
│
├── lib/
│   ├── constants/
│   │   ├── arabic.ts          # NEW: All UI text in Arabic
│   │   ├── status.ts          # NEW: Status enum translations
│   │   └── validation.ts      # NEW: Validation messages
│   │
│   └── utils/
│       ├── format.ts          # NEW: Number/date/currency formatting
│       └── normalize.ts       # NEW: Input normalization│
└── tailwind.config.ts         # UPDATE: RTL configuration
```

**Structure Decision**: Web application structure with Next.js 14 App Router. Frontend only changes. New pages for sale history, project details, partner history, categories, and expenses. All existing pages updated for Arabic RTL.

---

## Complexity Tracking

> No constitution violations. No complexity justification required.

---

## Implementation Phases

### Phase 0: Foundation (Priority: P1)

**Estimated Time**: 2-3 days

**Tasks**:
1. Set up Arabic constants file structure
2. Create formatting utilities (currency, date, number)
3. Create normalization utilities (Arabic-Indic numerals)
4. Update root layout for RTL (`lang="ar"`, `dir="rtl"`)
5. Configure Tailwind for RTL support
6. Create shared RTL-aware components (ErrorBoundary, LoadingSpinner, EmptyState)

**Deliverables**:
- `lib/constants/arabic.ts`
- `lib/utils/format.ts`
- `lib/utils/normalize.ts`
- Updated `app/layout.tsx`
- Updated shared components

**Validation**:
- [ ] All constants compile without errors
- [ ] Formatting functions produce correct output
- [ ] RTL layout applied to root element

### Phase 1: Dashboard & Core Components (Priority: P1)

**Estimated Time**: 2-3 days

**Tasks**:
1. Translate dashboard summary cards
2. Update chart components for RTL
3. Translate all chart labels
4. Update layout components (Sidebar, Header)
5. Update all shared components with Arabic text

**Deliverables**:
- Updated `app/dashboard/page.tsx`
- Updated `components/layout/*`
- Updated `components/shared/*`
- Updated `components/charts/*`

**Validation**:
- [ ] Dashboard displays Arabic labels
- [ ] Charts render correctly in RTL
- [ ] Sidebar appears on right side

### Phase 2: POS Module (Priority: P1)

**Estimated Time**: 2-3 days

**Tasks**:
1. Translate POS terminal (product grid, cart, fees, breakdown)
2. Create sale history page
3. Create sale detail view
4. Update fee editor for Arabic fee types
5. Translate payment method dropdown

**Deliverables**:
- Updated `app/pos/page.tsx`
- New `app/pos/history/page.tsx`
- New `app/pos/history/[saleId]/page.tsx`
- Updated `components/pos/*`

**Validation**:
- [ ] POS displays Arabic labels
- [ ] Sale history lists past transactions
- [ ] Sale detail shows complete breakdown

### Phase 3: Products & Categories (Priority: P2)

**Estimated Time**: 1-2 days

**Tasks**:
1. Translate products page
2. Create categories management page
3. Update product modal
4. Update category filter

**Deliverables**:
- Updated `app/products/page.tsx`
- New `app/categories/page.tsx`
- Updated `components/products/*`

**Validation**:
- [ ] Products page displays Arabic labels
- [ ] Categories page allows CRUD operations

### Phase 4: Inventory (Priority: P2)

**Estimated Time**: 1-2 days

**Tasks**:
1. Translate inventory page
2. Replace UUID input with product dropdown
3. Translate inventory log movement reasons
4. Update restock/adjustment forms

**Deliverables**:
- Updated `app/inventory/page.tsx`
- New `components/inventory/ProductSelector.tsx`

**Validation**:
- [ ] Product dropdown shows product names
- [ ] Movement reasons display in Arabic

### Phase 5: Projects (Priority: P2)

**Estimated Time**: 2 days

**Tasks**:
1. Translate projects list page
2. Create project detail view
3. Translate project creation modal
4. Add status filter

**Deliverables**:
- Updated `app/projects/page.tsx`
- New `app/projects/[projectId]/page.tsx`
- Updated `components/projects/*`

**Validation**:
- [ ] Projects list displays Arabic status
- [ ] Project detail shows items/expenses

### Phase 6: Partners (Priority: P2)

**Estimated Time**: 2 days

**Tasks**:
1. Translate partners list page
2. Create partner history view
3. Translate distribution modal
4. Add partner edit functionality

**Deliverables**:
- Updated `app/partners/page.tsx`
- New `app/partners/[partnerId]/page.tsx`
- Updated `components/partners/*`

**Validation**:
- [ ] Partners list displays Arabic labels
- [ ] Partner history shows distributions

### Phase 7: Reports (Priority: P3)

**Estimated Time**: 2 days

**Tasks**:
1. Translate sales report
2. Translate projects report
3. Translate partners report
4. Translate inventory report
5. Update chart visualizations

**Deliverables**:
- Updated `app/dashboard/reports/sales/page.tsx`
- Updated `app/dashboard/reports/projects/page.tsx`
- Updated `app/dashboard/reports/partners/page.tsx`
- Updated `app/dashboard/reports/inventory/page.tsx`
- Updated `components/reports/*`

**Validation**:
- [ ] All reports show Arabic labels
- [ ] Charts display Arabic axis labels

### Phase 8: Settings & Expenses (Priority: P3)

**Estimated Time**: 1-2 days

**Tasks**:
1. Translate settings page
2. Create expenses management page

**Deliverables**:
- Updated `app/settings/page.tsx`
- New `app/expenses/page.tsx`

**Validation**:
- [ ] Settings displays Arabic labels
- [ ] Expenses page allows expense creation

### Phase 9: Exports & Final Polish (Priority: P3)

**Estimated Time**: 1-2 days

**Tasks**:
1. Test CSV export with Arabic content
2. Test Excel export with Arabic content
3. Configure PDF Arabic font support
4. Test PDF generation
5. Final visual review of all pages

**Deliverables**:
- Tested export functionality
- PDF Arabic font configuration

**Validation**:
- [ ] CSV export includes Arabic headers
- [ ] Excel export includes Arabic content
- [ ] PDF renders Arabic text correctly

---

## Dependencies

### Frontend Dependencies (No Changes Required)
- Next.js 14
- React 18
- TailwindCSS 3.4
- Recharts (charts)
- lucide-react (icons)

### Backend Dependencies (Minimal)
- Arabic fonts for PDF generation
- WeasyPrint/ReportLab Arabic configuration

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Arabic font unavailable | Use system fonts with web font fallback |
| RTL breaking components | Use CSS logical properties throughout |
| PDF Arabic rendering | Test early with Arabic font embedding |
| Mixed Arabic/English content | Define clear handling rules |
| Number input confusion | Accept both numeral systems, normalize internally |

---

## Testing Strategy

### Visual Testing
- Screenshot comparison for RTL layout
- Arabic text rendering verification
- Chart RTL rendering tests

### Functional Testing
- Currency formatting with Arabic numerals
- Date formatting with Arabic months
- Input normalization (both numeral systems)
- Form submission and validation
- Export functionality (CSV, Excel, PDF)

### Integration Testing
- API calls with Arabic product names
- WebSocket messages in Arabic
- Error handling in Arabic

---

## Success Metrics

- [ ] 100% of UI elements display in Arabic
- [ ] All pages load in <3 seconds
- [ ] RTL layout correct on all pages
- [ ] Charts render correctly
- [ ] Exports contain Arabic content
- [ ] Zero hardcoded English text remains
- [ ] Product dropdown shows names (not UUIDs)
- [ ] Sale history page functional
- [ ] Project detail view functional
- [ ] Partner history view functional