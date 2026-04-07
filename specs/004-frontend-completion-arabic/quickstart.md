# Quickstart: Frontend Completion with Arabic RTL

**Feature**: 004-frontend-completion-arabic
**Date**: 2026-04-06

## Prerequisites

- Node.js 18+
- npm or yarn
- Git access to EZOO POS repository
- Basic understanding of React, Next.js, and TailwindCSS

## Quick Setup

### 1. Checkout the Feature Branch

```bash
git checkout 004-frontend-completion-arabic
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## Development Workflow

### Phase 1: Foundation (Days 1-2)

**Task**: Set up RTL foundation and Arabic constants

1. **Update Root Layout** (`app/layout.tsx`):
   ```tsx
   <html lang="ar" dir="rtl">
     <body>{children}</body>
   </html>
   ```

2. **Create Arabic Constants** (`lib/constants/arabic.ts`):
   - Copy the constants from `data-model.md`
   - Organize by module (common, dashboard, pos, etc.)

3. **Create Formatting Utilities** (`lib/utils/format.ts`):
   - `formatCurrency()`
   - `formatDate()`
   - `formatNumber()`
   - `formatPercentage()`

4. **Create Normalize Utilities** (`lib/utils/normalize.ts`):
   - `toWesternNumerals()`
   - `toArabicNumerals()`
   - `normalizeInput()`

### Phase 2: Core Components (Days 3-4)

**Task**: Update shared components for Arabic RTL

1. **ErrorBoundary**: Replace English messages with `ARABIC.errors.*`
2. **LoadingSpinner**: Use `ARABIC.common.loading`
3. **EmptyState**: Use `ARABIC.emptyStates.*`
4. **ConfirmModal**: Use `ARABIC.common.confirm/cancel`

### Phase 3: Dashboard & Reports (Days 5-7)

**Task**: Translate dashboard and all report pages

1. **Dashboard Page**:
   - Summary cards: `ARABIC.dashboard.*`
   - Chart labels: `ARABIC.dashboard.*`
   - Quick navigation: `ARABIC.dashboard.quickNavigation`

2. **Sales Report**:
   - Summary cards: `ARABIC.reports.sales.*`
   - Table columns: Arabic labels
   - Export buttons: `ARABIC.reports.export.*`

3. **Other Reports**: Follow same pattern

### Phase 4: POS Module (Days 8-9)

**Task**: Translate POS and add sale history

1. **POS Terminal**:
   - Product grid: Arabic product names
   - Cart labels: `ARABIC.pos.*`
   - Fee editor: Arabic fee types
   - Payment methods: Arabic names

2. **New: Sale History Page**:
   - `app/pos/history/page.tsx`
   - Display past sales with Arabic labels
   - Link to sale detail view

3. **New: Sale Detail View**:
   - `app/pos/history/[saleId]/page.tsx`
   - Show complete transaction breakdown

### Phase 5: Products & Inventory (Days 10-11)

**Task**: Translate products, categories, inventory

1. **Products Page**: `ARABIC.products.*`
2. **New: Categories Page**: `app/categories/page.tsx`
3. **Inventory Page**: `ARABIC.inventory.*`
   - Replace UUID input with dropdown

### Phase 6: Projects & Partners (Days 12-14)

**Task**: Translate projects and partners, add history views

1. **Projects Page**: `ARABIC.projects.*`
2. **New: Project Detail**: `app/projects/[projectId]/page.tsx`
3. **Partners Page**: `ARABIC.partners.*`
4. **New: Partner History**: `app/partners/[partnerId]/page.tsx`

### Phase 7: Settings & Expenses (Days 15-16)

**Task**: Translate settings and add expenses page

1. **Settings Page**: `ARABIC.settings.*`
2. **New: Expenses Page**: `app/expenses/page.tsx`

### Phase 8: Final Polish (Days 17-18)

**Task**: Charts, exports, and testing

1. **Charts**: Ensure RTL rendering
2. **Exports**: Test CSV, Excel, PDF
3. **Testing**: All pages, all flows

## Key Files to Modify

### Layout Files
- `app/layout.tsx` - Add `lang="ar"` and `dir="rtl"`
- `components/dashboard/DashboardLayout.tsx` - RTL sidebar

### Constants Files (New)
- `lib/constants/arabic.ts` - All UI text
- `lib/constants/status.ts` - Status translations
- `lib/constants/validation.ts` - Validation messages

### Utility Files (New)
- `lib/utils/format.ts` - Formatting functions
- `lib/utils/normalize.ts` - Input normalization

### Page Files (Update)
- All `app/*/page.tsx` files - Replace English with Arabic

### Component Files (Update)
- All `components/**/*.tsx` files - RTL adjustments

## Testing Commands

### Visual Testing
```bash
# Run development server
npm run dev

# Check each page visually
# Open http://localhost:3000/dashboard
# Open http://localhost:3000/pos
# etc.
```

### RTL Testing Checklist
- [ ] Sidebar appears on right side
- [ ] Text is right-aligned
- [ ] Tables flow right-to-left
- [ ] Charts render correctly
- [ ] Forms have RTL layout
- [ ] Icons mirror appropriately

### Arabic Testing Checklist
- [ ] All labels in Arabic
- [ ] Currency shows ج.س
- [ ] Dates show Arabic month names
- [ ] Numbers show Arabic numerals (optional)
- [ ] Error messages in Arabic
- [ ] Success messages in Arabic
- [ ] Export files have Arabic content

## Common Patterns

### Using Arabic Constants
```tsx
import { ARABIC } from '@/lib/constants/arabic';

export function MyComponent() {
  return (
    <div>
      <h1>{ARABIC.dashboard.title}</h1>
      <button>{ARABIC.common.save}</button>
    </div>
  );
}
```

### Formatting Currency
```tsx
import { formatCurrency } from '@/lib/utils/format';

export function PriceDisplay({ amount }: { amount: number }) {
  return <span>{formatCurrency(amount)}</span>;
  // Output: "١،٢٣٤٫٥٦ ج.س"
}
```

### Formatting Dates
```tsx
import { formatDate } from '@/lib/utils/format';

export function DateDisplay({ date }: { date: string }) {
  return <span>{formatDate(date)}</span>;
  // Output: "١٥ يناير ٢٠٢٦"
}
```

### RTL-Aware Styling
```tsx
// Instead of margin-left
<div className="ms-4">...</div> // margin-inline-start// Instead of padding-right
<div className="pe-2">...</div> // padding-inline-end

// Instead of right: 0
<div className="end-0">...</div> // inset-inline-end
```

### Input Normalization
```tsx
import { normalizeInput } from '@/lib/utils/normalize';

export function NumberInput(props: InputProps) {
  return (
    <input
      {...props}
      onBlur={(e) => {
        const normalized = normalizeInput(e.target.value);
        props.onBlur?.(normalized);
      }}
    />
  );
}
```

## Troubleshooting

### Arabic Font Not Loading
- Ensure system fonts support Arabic
- Consider adding `@font-face` for Noto Sans Arabic

### RTL Layout Breaking
- Use logical properties (`ms-*`, `me-*`, `ps-*`, `pe-*`)
- Avoid `left`/`right` CSS properties
- Check `flex-row-reverse` for horizontal layouts

### Numbers Not Converting
- Use `Intl.NumberFormat('ar-SA')`
- For input, use `normalizeInput()` before sending to API

### PDF Arabic Not Rendering
- Ensure server has Arabic fonts installed
- Use `arabic_reshaper` and `bidi.algorithm` for RTL

## Resources

- [TailwindCSS RTL Documentation](https://tailwindcss.com/docs/adding-base-styles#adding-basic-typography)
- [MDN RTL Guide](https://developer.mozilla.org/en-US/docs/Web/Localization/RTL_Responsive_Design)
- [Intl.NumberFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat)
- [Intl.DateTimeFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat)