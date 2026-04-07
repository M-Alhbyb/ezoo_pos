# Research: Frontend Completion with Arabic RTL

**Feature**: 004-frontend-completion-arabic
**Date**: 2026-04-06

## Technical Decisions

### 1. RTL Implementation Strategy

**Decision**: Use Tailwind CSS logical properties with `dir="rtl"` attribute

**Rationale**:
- Tailwind CSS provides built-in RTL support via logical properties
- Using `dir="rtl"` on `<html>` element enables browser-native RTL
- CSS logical properties (`margin-inline-start`, `padding-inline-end`) automatically adapt to text direction
- No additional RTL library required

**Alternatives Considered**:
- RTL CSS preprocessors (rejected - adds complexity)
- Separate RTL stylesheet (rejected - maintenance burden)
- CSS-in-JS RTL libraries (rejected - overkill for this use case)

**Implementation**:
```tsx
// app/layout.tsx
<html lang="ar" dir="rtl">
  <body>{children}</body>
</html>
```

### 2. Arabic Text Management

**Decision**: Hardcoded Arabic constants file (no i18n system)

**Rationale**:
- Single language (Arabic only) - no need for full i18n framework
- Simpler maintenance without translation keys management
- Faster bundle size without i18n library overhead
- Constants file allows easy review and updates

**Alternatives Considered**:
- next-intl (rejected - adds complexity for single language)
- react-i18next (rejected - requires translation file management)
- JSON translation files (rejected - over-engineering for single language)

**Implementation**:
```typescript
// lib/constants/arabic.ts
export const ARABIC = {
  common: {
    save: 'حفظ',
    cancel: 'إلغاء',
    delete: 'حذف',
    // ...
  },
  dashboard: {
    totalRevenue: 'إجمالي الإيرادات',
    activeProjects: 'المشاريع النشطة',
    // ...
  },
  // ...
} as const;
```

### 3. Number and Currency Formatting

**Decision**: Use `Intl.NumberFormat` with `ar-SA` locale

**Rationale**:
- Native browser API - no dependencies
- Consistent formatting across the application
- Supports both Western and Arabic-Indic numerals
- Proper currency formatting with ر.س symbol

**Alternatives Considered**:
- numeral.js (rejected - library dependency)
- Custom formatting functions (rejected - reinventing the wheel)
- decimal.js formatting (rejected - backend concern)

**Implementation**:
```typescript
// lib/utils/format.ts
export function formatCurrency(value: number | string): string {
  return new Intl.NumberFormat('ar-SA', {
    style: 'currency',
    currency: 'SAR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value));
}

export function formatDate(date: Date | string): string {
  return new Intl.DateTimeFormat('ar-SA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(date));
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat('ar-SA').format(value);
}
```

### 4. PDF Export for Arabic

**Decision**: Use existing WeasyPrint/ReportLab with Arabic font configuration

**Rationale**:
- Backend already handles PDF export
- Arabic text rendering requires proper font embedding
- WeasyPrint supports Arabic text with RTL automatically
- ReportLab supports Arabic with `arabic_reshaper` and `bidi.algorithm`

**Alternatives Considered**:
- Client-side PDF generation (rejected - Arabic rendering issues)
- External PDF service (rejected - unnecessary complexity)
- Canvas-based PDF (rejected - poor Arabic support)

**Backend Changes Required**:
- Ensure Arabic fonts are installed on server
- Configure WeasyPrint/ReportLab with Arabic font paths
- Test RTL rendering in PDF output

### 5. Chart RTL Support

**Decision**: Configure Recharts for RTL with Arabic labels

**Rationale**:
- Existing charts use Recharts
- Recharts supports RTL layout via component props
- Custom tick formatters for Arabic text
- Legend positioning respects RTL

**Alternatives Considered**:
- D3.js RTL (rejected - significant rewrite)
- Chart.js RTL plugin (rejected - would require library switch)
- Custom canvas charts (rejected - over-engineering)

**Implementation**:
```tsx
// Chart configuration for RTL
<ResponsiveContainer>
  <LineChart data={data} layout="vertical">
    <XAxis 
      tickFormatter={(value) => formatNumber(value)}
      tick={{ fill: '#374151', fontSize: 12 }}
    />
    <YAxis 
      dataKey="التاريخ"
      type="category"
      tick={{ fill: '#374151', fontSize: 12 }}
    />
    <Tooltip 
      formatter={(value) => formatCurrency(value)}
      labelFormatter={(label) => `${label}`}
    />
    <Legend />
  </LineChart>
</ResponsiveContainer>
```

### 6. Form Input Handling

**Decision**: Accept both Western and Arabic-Indic numerals, normalize to Western for storage

**Rationale**:
- Users may input Arabic-Indic numerals (١٢٣)
- Backend expects Western numerals
- Normalization happens transparently on submit

**Implementation**:
```typescript
// lib/utils/normalize.ts
const ARABIC_NUMERALS: Record<string, string> = {
  '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
  '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
};

export function normalizeArabicNumerals(input: string): string {
  return input.replace(/[٠-٩]/g, (match) => ARABIC_NUMERALS[match] || match);
}

export function toArabicNumerals(input: string | number): string {
  const arabicNumerals = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
  return String(input).replace(/[0-9]/g, (d) => arabicNumerals[parseInt(d)]);
}
```

### 7. CSS Architecture for RTL

**Decision**: Replace all physical properties with logical properties

**Rationale**:
- Logical properties (`margin-inline-start`, `border-inline-end`) automatically mirror for RTL
- Tailwind provides logical property utilities (`ms-*`, `me-*`, `ps-*`, `pe-*`)
- Reduces manual RTL override CSS

**Examples of Conversions**:
| Physical Property | Logical Property | Tailwind Class |
|-------------------|------------------|----------------|
| `margin-left: 16px` | `margin-inline-start: 16px` | `ms-4` |
| `padding-right: 8px` | `padding-inline-end: 8px` | `pe-2` |
| `right: 0` | `inset-inline-end: 0` | `end-0` |
| `border-left: 1px` | `border-inline-start: 1px` | `border-s` |

### 8. Component Architecture

**Decision**: Single constants file + per-file Arabic strings

**Rationale**:
- Centralized constants for shared text (buttons, labels, errors)
- Component-local strings for specific messaging
- Easy to audit for missing translations

**Structure**:
```
frontend/lib/constants/
├── arabic.ts          # Common UI strings
├── errors.ts          # Error messages in Arabic
├── validation.ts      # Validation messages in Arabic
└── reports.ts         # Report-specific strings

frontend/lib/utils/
├── format.ts          # Number/date/currency formatting
└── normalize.ts       # Input normalization
```

## Dependencies Analysis

### Existing Dependencies (No Changes Required)
- Next.js 14 App Router
- React 18
- TailwindCSS 3.4
- Recharts (charts)
- lucide-react (icons)

### New Dependencies (None Required)
The feature uses only native browser APIs and existing dependencies.

## Performance Considerations

### Bundle Size
- Arabic constants: ~15KB (all strings)
- No additional i18n library overhead
- No RTL library overhead

### Runtime Performance
- `Intl.NumberFormat` and `Intl.DateTimeFormat` are native APIs
- No runtime translation lookup overhead
- CSS logical properties are browser-native

### Load Time
- Arabic fonts should use `font-display: swap`
- System Arabic fonts as fallback
- No additional font files required for basic Arabic

## Testing Strategy

### Visual Regression
- RTL screenshots for all pages
- Arabic text rendering verification
- Chart RTL rendering tests

### Functional Tests
- Currency formatting tests
- Date formatting tests
- Number conversion tests
- Form input normalization tests

### Accessibility
- Screen reader testing with Arabic
- Keyboard navigation for RTL
- Focus management for RTL

## Risk Mitigation

### Risk: Arabic Font Availability
**Mitigation**: Use system fonts with web font fallback

### Risk: RTL Breaking Existing Components
**Mitigation**: Comprehensive visual testing before merge

### Risk: PDF Arabic Rendering
**Mitigation**: Test PDF generation with Arabic content early

### Risk: Mixed Content (Arabic/English)
**Mitigation**: Define clear handling rules (display as-entered for user content)