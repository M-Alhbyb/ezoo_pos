# Contracts: Frontend Completion with Arabic RTL

**Feature**: 004-frontend-completion-arabic
**Date**: 2026-04-06

## Overview

This feature is **frontend-only** and requires no backend API contract changes. All existing backend endpoints remain unchanged. The frontend consumes the same API responses but displays content in Arabic.

---

## No API Changes Required

### Existing Endpoints (No Modifications)

All existing backend endpoints continue to work as-is:

| Module | Endpoint | Change Required |
|--------|----------|------------------|
| POS | All `/api/sales/*` endpoints | None |
| Products | All `/api/products/*` endpoints | None |
| Inventory | All `/api/inventory/*` endpoints | None |
| Projects | All `/api/projects/*` endpoints | None |
| Partners | All `/api/partners/*` endpoints | None |
| Reports | All `/api/reports/*` endpoints | None |
| Dashboard | All `/api/dashboard/*` endpoints | None |
| Settings | All `/api/settings/*` endpoints | None |
| Categories | All `/api/categories/*` endpoints | None |
| Expenses | All `/api/expenses/*` endpoints | None |

---

## Backend Considerations

### PDF Export with Arabic

**Current Status**: Backend uses WeasyPrint/ReportLab for PDF generation.

**Required Changes**:
1. Ensure Arabic fonts are available on the server
2. Configure PDF generation with Arabic font support
3. Test RTL rendering in PDF output

**Configuration Needed**:
```python
# Ensure Arabic fonts are installed
# Font file: NotoSansArabic-Regular.ttf

# WeasyPrint CSS
@font-face {
    font-family: 'Noto Sans Arabic';
    src: url('/fonts/NotoSansArabic-Regular.ttf');
}
body {
    font-family: 'Noto Sans Arabic', sans-serif;
    direction: rtl;
}

# ReportLab Arabic configuration
import arabic_reshaper
from bidi.algorithm import get_display

def render_arabic_text(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)
```

---

## Frontend Contract

### Constants Contract

The frontend will use the `ARABIC` constant object for all user-facing text:

```typescript
import { ARABIC } from '@/lib/constants/arabic';

// Usage
<h1>{ARABIC.dashboard.title}</h1>
<button>{ARABIC.common.save}</button>
```

### Formatting Contract

All formatting functions use `Intl` API with `ar-SA` locale:

```typescript
formatCurrency(1234.56)// "١،٢٣٤٫٥٦ ج.س"
formatDate(new Date())        // "١٥ يناير ٢٠٢٦"
formatNumber(1234)            // "١،٢٣٤"
```

### Input Normalization Contract

Form inputs accept both Western and Arabic-Indic numerals:

```typescript
// Input: "١٢٣" or "123"
// Stored: "123" (Western numerals)
// Display: "١٢٣" (Arabic-Indic numerals)
```

---

## Export File Formats

### CSV Export

**Encoding**: UTF-8 with BOM for Excel Arabic support
**Headers**: Arabic column names
**Content**: Arabic text

### Excel Export

**Encoding**: UTF-8
**Headers**: Arabic column names
**Content**: RTL sheets if needed

### PDF Export

**Fonts**: Embedded Arabic fonts (Noto Sans Arabic)
**Direction**: RTL layout
**Content**: Arabic text with proper glyph shaping

---

## WebSocket Messages

### Stock Update (Arabic Display)

```typescript
// WebSocket message format (unchanged)
{
  type: 'stock_update',
  product_id: 'uuid',
  product_name: 'Product Name',// Can be Arabic
  new_quantity: 10,
  delta: -5
}

// Frontend displays Arabic message
const message = `${ARABIC.inventory.movementTypes.sale}: ${productName}`;
```

---

## No Breaking Changes

This feature:
- Adds no new API endpoints
- Modifies no existing API responses
- Requires no database migrations
- Requires no backend code changes (except PDF font configuration)

---

## Testing Contract

### Frontend Tests Required

1. All pages render with Arabic text
2. RTL layout is correctly applied
3. Currency formatting shows ج.س
4. Date formatting shows Arabic month names
5. Export files contain Arabic content
6. Charts display Arabic labels

### Integration Tests Required

1. API calls work with Arabic product names
2. Form submissions accept both numeral systems
3. WebSocket messages display correctly in Arabic