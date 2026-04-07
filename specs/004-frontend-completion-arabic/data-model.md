# Data Model: Frontend Completion with Arabic RTL

**Feature**: 004-frontend-completion-arabic
**Date**: 2026-04-06

## Overview

This document defines the frontend data structures, component architecture, and translation constants for Arabic RTL support. No backend changes required.

---

## Arabic Constants

### Core Structure

```typescript
// lib/constants/arabic.ts

export const ARABIC = {
  // Common Actions
  common: {
    save: 'حفظ',
    cancel: 'إلغاء',
    delete: 'حذف',
    edit: 'تعديل',
    add: 'إضافة',
    update: 'تحديث',
    confirm: 'تأكيد',
    back: 'رجوع',
    next: 'التالي',
    submit: 'إرسال',
    search: 'بحث',
    filter: 'تصفية',
    export: 'تصدير',
    import: 'استيراد',
    refresh: 'تحديث',
    loading: 'جاري التحميل...',
    saving: 'جاري الحفظ...',
    success: 'تمت العملية بنجاح',
    error: 'حدث خطأ',
    required: 'هذا الحقل مطلوب',
  },

  // Navigation
  nav: {
    dashboard: 'لوحة التحكم',
    pos: 'نقطة البيع',
    products: 'المنتجات',
    categories: 'التصنيفات',
    inventory: 'المخزون',
    projects: 'المشاريع',
    partners: 'الشركاء',
    reports: 'التقارير',
    settings: 'الإعدادات',
    expenses: 'المصاريف',
    salesReport: 'تقرير المبيعات',
    projectsReport: 'تقرير المشاريع',
    partnersReport: 'تقرير الشركاء',
    inventoryReport: 'تقرير المخزون',
  },

  // Dashboard
  dashboard: {
    title: 'لوحة التحكم',
    subtitle: 'تحليلات الأعمال والتتبع بالوقت الفعلي',
    totalRevenue: 'إجمالي الإيرادات',
    activeProjects: 'المشاريع النشطة',
    partners: 'الشركاء',
    lowStockItems: 'المنتجات المنخفضة',
    salesGrowth: 'نمو المبيعات',
    projectPerformance: 'أداء المشاريع',
    partnerDividends: 'أرباح الشركاء',
    stockActivity: 'حركة المخزون',
    viewDetails: 'عرض التفاصيل',
    viewProjects: 'عرض المشاريع',
    manage: 'إدارة',
    reports: 'التقارير',
    quickNavigation: 'التنقل السريع',
    salesPOS: 'نقطة البيع',
    salesPOSDesc: 'تشغيل الوحدة لإنشاء مبيعات جديدة ومعالجة الدفع.',
    inventory: 'المخزون',
    inventoryDesc: 'تعديل الكتالوجات وإضافة المنتجات وتتبع التصنيفات.',
    projectsDesc: 'تتبع مالي تفصيلي للمشاريع المخصصة.',
    partnersDesc: 'أتمتة توزيع الأرباح وإدارة حصص المستثمرين.',
  },

  // POS
  pos: {
    title: 'نقطة البيع',
    product: 'المنتج',
    quantity: 'الكمية',
    price: 'السعر',
    total: 'الإجمالي',
    subtotal: 'المجموع الفرعي',
    fees: 'الرسوم',
    vat: 'ضريبة القيمة المضافة',
    grandTotal: 'الإجمالي الكلي',
    shipping: 'الشحن',
    installation: 'التركيب',
    custom: 'مخصص',
    paymentMethod: 'طريقة الدفع',
    selectPaymentMethod: 'اختر طريقة الدفع',
    completeSale: 'إتمام البيع',
    clearCart: 'إفراغ السلة',
    cartEmpty: 'السلة فارغة',
    addProducts: 'أضف منتجات للبدء',
    saleComplete: 'تمت عملية البيع بنجاح',
    saleHistory: 'سجل المبيعات',
    saleDetails: 'تفاصيل البيع',
    reversal: 'إلغاء',
    reversalReason: 'سبب الإلغاء',
  },

  // Products
  products: {
    title: 'إدارة المنتجات',
    subtitle: 'الكاش والفئات وتتبع المخزون',
    productName: 'اسم المنتج',
    sku: 'رمز المنتج',
    category: 'التصنيف',
    basePrice: 'السعر الأساسي',
    sellingPrice: 'سعر البيع',
    stockQuantity: 'الكمية المتاحة',
    status: 'الحالة',
    active: 'نشط',
    inactive: 'غير نشط',
    addProduct: 'إضافة منتج',
    editProduct: 'تعديل المنتج',
    deleteProduct: 'حذف المنتج',
    noProducts: 'لا توجد منتجات',
    addProductStart: 'أضف منتجاً جديداً للبدء',
    searchProducts: 'البحث عن منتجات...',
    filterByCategory: 'تصفية حسب التصنيف',
  },

  // Categories
  categories: {
    title: 'إدارة التصنيفات',
    subtitle: 'تنظيم المنتجات في تصنيفات',
    categoryName: 'اسم التصنيف',
    productCount: 'عدد المنتجات',
    addCategory: 'إضافة تصنيف',
    editCategory: 'تعديل التصنيف',
    deleteCategory: 'حذف التصنيف',
    noCategories: 'لا توجد تصنيفات',
    addCategoryStart: 'أضف تصنيفاً جديداً للبدء',
  },

  // Inventory
  inventory: {
    title: 'إدارة المخزون',
    subtitle: 'تتبع المنتجات منخفضة المخزون وتعديل الكميات',
    lowStockAlerts: 'تنبيهات المخزون المنخفض',
    inventoryLog: 'سجل المخزون',
    restock: 'إعادة التخزين',
    adjustment: 'تعديل الكمية',
    selectProduct: 'اختر المنتج',
    reason: 'السبب',
    quantity: 'الكمية',
    balance: 'الرصيد',
    delta: 'التغيير',
    movements: 'الحركات',
    movementTypes: {
      sale: 'مبيعة',
      restock: 'إعادة تخزين',
      adjustment: 'تعديل',
      reversal: 'إلغاء',
    },
    restockSuccess: 'تمت إعادة التخزين بنجاح',
    adjustmentSuccess: 'تم التعديل بنجاح',
    allStockHealthy: 'مستويات المخزون صحية',
  },

  // Projects
  projects: {
    title: 'إدارة المشاريع',
    subtitle: 'تتبع الأعمال المخصصة والطلبات المعقدة',
    projectName: 'اسم المشروع',
    sellingPrice: 'سعر البيع',
    totalCost: 'التكلفة الإجمالية',
    totalExpenses: 'إجمالي المصاريف',
    profit: 'الربح',
    status: 'الحالة',
    statusTypes: {
      draft: 'قيد التنفيذ',
      completed: 'مكتمل',
    },
    items: 'المنتجات',
    expenses: 'المصاريف',
    createProject: 'إنشاء مشروع',
    editProject: 'تعديل المشروع',
    completeProject: 'إتمام المشروع',
    confirmComplete: 'هل أنت متأكد من إتمام المشروع؟',
    noProjects: 'لا توجد مشاريع',
    createProjectStart: 'أنشئ مشروعاً جديداً للبدء',
    viewDetails: 'عرض التفاصيل',
  },

  // Partners
  partners: {
    title: 'إدارة الشركاء',
    subtitle: 'تتبع حصص الشركاء وتوزيع الأرباح',
    partnerName: 'اسم الشريك',
    sharePercentage: 'نسبة الملكية',
    investmentAmount: 'مبلغ الاستثمار',
    addPartner: 'إضافة شريك',
    editPartner: 'تعديل الشريك',
    deletePartner: 'حذف الشريك',
    distributeProfits: 'توزيع الأرباح',
    distribution: 'التوزيع',
    distributionSuccess: 'تم التوزيع بنجاح',
    amountReceived: 'المبلغ المستلم',
    noPartners: 'لا يوجد شركاء',
    addPartnerStart: 'أضف شريكاً للبدء',
    viewHistory: 'عرض السجل',
    distributionHistory: 'سجل التوزيعات',
  },

  // Reports
  reports: {
    sales: {
      title: 'تقرير المبيعات',
      subtitle: 'تحليلات يومية وتفصيل الإيرادات لكل معاملة',
      totalRevenue: 'إجمالي الإيرادات',
      netProfit: 'صافي الربح',
      salesCount: 'عدد المبيعات',
      avgMargin: 'متوسط هامش الربح',
      date: 'التاريخ',
      dailyStatistics: 'الإحصائيات اليومية',
    },
    projects: {
      title: 'تقرير المشاريع',
      subtitle: 'تحليل الأداء المالي للمشاريع',
      totalProjects: 'إجمالي المشاريع',
      totalSellingPrice: 'إجمالي سعر البيع',
      totalCost: 'إجمالي التكاليف',
      totalExpenses: 'إجمالي المصاريف',
      totalProfit: 'إجمالي الأرباح',
    },
    partners: {
      title: 'تقرير الشركاء',
      subtitle: 'توزيعات الأرباح وتفاصيل المستثمرين',
      totalPayout: 'إجمالي التوزيعات',
      partnersCount: 'عدد الشركاء',
    },
    inventory: {
      title: 'تقرير المخزون',
      subtitle: 'حركة المخزون والتنبيهات',
      totalMovements: 'إجمالي الحركات',
      from: 'من تاريخ',
      to: 'إلى تاريخ',
    },
    export: {
      csv: 'تصدير CSV',
      excel: 'تصدير Excel',
      pdf: 'تصدير PDF',
      exporting: 'جاري التصدير...',
      exportSuccess: 'تم التصدير بنجاح',
    },
  },

  // Settings
  settings: {
    title: 'الإعدادات',
    subtitle: 'تكوين النظام والطرق والرسوم',
    paymentMethods: 'طرق الدفع',
    feePresets: 'إعدادات الرسوم',
    vatSettings: 'إعدادات ضريبة القيمة المضافة',
    vatEnabled: 'تفعيل الضريبة',
    vatRate: 'نسبة الضريبة',
    addPaymentMethod: 'إضافة طريقة دفع',
    methodName: 'اسم الطريقة',
    methodNameAr: 'اسم الطريقة (بالعربية)',
    methodNameEn: 'اسم الطريقة (بالإنجليزية)',
  },

  // Expenses
  expenses: {
    title: 'إدارة المصاريف',
    subtitle: 'تتبع المصاريف التشغيلية',
    description: 'الوصف',
    amount: 'المبلغ',
    category: 'التصنيف',
    date: 'التاريخ',
    addExpense: 'إضافة مصروف',
    noExpenses: 'لا توجد مصاريف',
  },

  // Form Labels
  forms: {
    required: 'مطلوب',
    optional: 'اختياري',
    invalidFormat: 'تنسيق غير صالح',
    minLength: 'الحد الأدنى {min} أحرف',
    maxLength: 'الحد الأقصى {max} أحرف',
    minValue: 'القيمة لا تقل عن {min}',
    maxValue: 'القيمة لا تتجاوز {max}',
    invalidEmail: 'البريد الإلكتروني غير صالح',
    invalidNumber: 'الرقم غير صالح',
    invalidDate: 'التاريخ غير صالح',
    passwordMismatch: 'كلمات المرور غير متطابقة',
  },

  // Errors
  errors: {
    networkError: 'خطأ في الاتصال بالشبكة',
    serverError: 'خطأ في الخادم. يرجى المحاولة لاحقاً',
    validationError: 'يرجى التحقق من البيانات المدخلة',
    notFound: 'لم يتم العثور على البيانات',
    permissionDenied: 'ليس لديك صلاحية للقيام بهذا الإجراء',
    unknownError: 'حدث خطأ غير متوقع',
    insufficientStock: 'الكمية المطلوبة غير متوفرة في المخزون',
    duplicateEntry: 'هذا العنصر موجود بالفعل',
    operationFailed: 'فشلت العملية',
  },

  // Empty States
  emptyStates: {
    noProducts: 'لا توجد منتجات. أضف منتجاً جديداً للبدء.',
    noSales: 'لا توجد مبيعات بعد.',
    noProjects: 'لا توجد مشاريع. أنشئ مشروعاً جديداً.',
    noPartners: 'لا يوجد شركاء. أضف شريكاً للبدء.',
    noInventory: 'لا توجد سجلات مخزون.',
    noData: 'لا توجد بيانات للفترة المحددة.',
    noSearchResults: 'لم يتم العثور على نتائج.',
  },

  // Status
  status: {
    active: 'نشط',
    inactive: 'غير نشط',
    pending: 'قيد الانتظار',
    completed: 'مكتمل',
    draft: 'قيد التنفيذ',
    cancelled: 'ملغي',
  },

  // Dates
  dates: {
    today: 'اليوم',
    yesterday: 'أمس',
    thisWeek: 'هذا الأسبوع',
    thisMonth: 'هذا الشهر',
    lastMonth: 'الشهر الماضي',
    thisYear: 'هذا العام',
    custom: 'مخصص',
    from: 'من',
    to: 'إلى',
  },

  // Numbers
  numbers: {
    currency: 'ر.س',
    items: 'عناصر',
    page: 'صفحة',
    of: 'من',
    showing: 'عرض',
  },
} as const;
```

---

## Component Architecture

### Shared Components

```
components/shared/
├── ErrorBoundary.tsx      # Arabic error messages
├── ConnectionStatus.tsx   # Arabic connection status
├── LoadingSpinner.tsx     # RTL-aware spinner
├── EmptyState.tsx         # Arabic empty states
├── ErrorMessage.tsx       # Arabic error display
├── DatePicker.tsx         # RTL date picker
├── ExportButton.tsx       # Export dropdown (CSV/Excel/PDF)
├── ConfirmModal.tsx       # Confirmation dialog (Arabic)
└── PageHeader.tsx         # Page title with subtitle
```

### Layout Components

```
components/layout/
├── DashboardLayout.tsx    # Main layout (RTL)
├── Sidebar.tsx            # Navigation (RTL)
├── Header.tsx             # Top header
└── Breadcrumb.tsx         # Navigation path
```

---

## Utility Functions

### Formatting Utilities

```typescript
// lib/utils/format.ts

import { ARABIC } from '@/lib/constants/arabic';

/**
 * Format currency value with Arabic locale and SAR symbol
 */
export function formatCurrency(value: number | string | Decimal): string {
  const num = typeof value === 'string' ? parseFloat(value) : Number(value);
  return new Intl.NumberFormat('ar-SA', {
    style: 'currency',
    currency: 'SAR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

/**
 * Format date with Arabic month names
 */
export function formatDate(date: Date | string, format: 'short' | 'long' = 'long'): string {
  const d = new Date(date);
  const options: Intl.DateTimeFormatOptions = format === 'long' 
    ? { year: 'numeric', month: 'long', day: 'numeric' }
    : { year: 'numeric', month: 'short', day: 'numeric' };
  return new Intl.DateTimeFormat('ar-SA', options).format(d);
}

/**
 * Format number with Arabic locale
 */
export function formatNumber(value: number): string {
  return new Intl.NumberFormat('ar-SA').format(value);
}

/**
 * Format percentage with Arabic locale
 */
export function formatPercentage(value: number, decimals: number = 1): string {
  return new Intl.NumberFormat('ar-SA', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100);
}

/**
 * Format datetime with time
 */
export function formatDateTime(date: Date | string): string {
  return new Intl.DateTimeFormat('ar-SA', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
  }).format(new Date(date));
}
```

### Normalization Utilities

```typescript
// lib/utils/normalize.ts

/**
 * Mapping of Arabic-Indic numerals to Western numerals
 */
const ARABIC_TO_WESTERN: Record<string, string> = {
  '٠': '0', '١': '1', '٢': '2', '٣': '3', '٤': '4',
  '٥': '5', '٦': '6', '٧': '7', '٨': '8', '٩': '9',
};

/**
 * Mapping of Western numerals to Arabic-Indic numerals
 */
const WESTERN_TO_ARABIC: Record<string, string> = {
  '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
  '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩',
};

/**
 * Convert Arabic-Indic numerals to Western numerals
 */
export function toWesternNumerals(input: string): string {
  return input.replace(/[٠-٩]/g, (match) => ARABIC_TO_WESTERN[match] || match);
}

/**
 * Convert Western numerals to Arabic-Indic numerals
 */
export function toArabicNumerals(input: string | number): string {
  return String(input).replace(/[0-9]/g, (d) => WESTERN_TO_ARABIC[d] || d);
}

/**
 * Normalize input - accept both numeral systems
 */
export function normalizeInput(value: string): string {
  return toWesternNumerals(value.trim());
}
```

---

## Page Components

### Required New Pages

```
app/
├── pos/
│   ├── page.tsx              # POS terminal (update Arabic)
│   └── history/
│       ├── page.tsx          # NEW: Sale history list
│       └── [saleId]/
│           └── page.tsx      # NEW: Sale detail view
│
├── categories/
│   └── page.tsx              # NEW: Categories management
│
├── expenses/
│   └── page.tsx              # NEW: Expenses management
│
├── projects/
│   ├── page.tsx              # Update Arabic
│   └── [projectId]/
│       └── page.tsx          # NEW: Project detail view
│
├── partners/
│   ├── page.tsx              # Update Arabic
│   └── [partnerId]/
│       └── page.tsx          # NEW: Partner history view
```

---

## TailwindCSS RTL Configuration

```typescript
// tailwind.config.ts (updates needed)

const config: Config = {
  content: ['./app/**/*.{js,ts,jsx,tsx,mdx}', './components/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      // RTL-aware utilities (already available in Tailwind)
      // Use ms-* / me-* for margin-start / margin-end
      // Use ps-* / pe-* for padding-start / padding-end
      // Use start-* / end-* for inset-inline-start / inset-inline-end
      // Use border-s-* / border-e-* for border-inline-start / border-inline-end
    },
  },
};
```

---

## Export Configuration

### PDF Arabic Font Setup

```python
# Backend: Add Arabic font support for PDF exports

# WeasyPrint configuration
@font-face {
    font-family: 'Noto Sans Arabic';
    src: url('/fonts/NotoSansArabic-Regular.ttf');
}

/* ReportLab Arabic configuration */
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Arabic', '/fonts/NotoSansArabic-Regular.ttf'))

# Use arabic_reshaper for proper glyph shaping
import arabic_reshaper
from bidi.algorithm import get_display

def render_arabic(text: str) -> str:
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)
```

---

## Status Enum Translations

```typescript
// lib/constants/status.ts

export const PROJECT_STATUS = {
  DRAFT: { en: 'Draft', ar: 'قيد التنفيذ' },
  COMPLETED: { en: 'Completed', ar: 'مكتمل' },
} as const;

export const INVENTORY_REASONS = {
  sale: { en: 'Sale', ar: 'مبيعة' },
  restock: { en: 'Restock', ar: 'إعادة تخزين' },
  adjustment: { en: 'Adjustment', ar: 'تعديل' },
  reversal: { en: 'Reversal', ar: 'إلغاء' },
} as const;

export const FEE_TYPES = {
  shipping: { en: 'Shipping', ar: 'الشحن' },
  installation: { en: 'Installation', ar: 'التركيب' },
  custom: { en: 'Custom', ar: 'مخصص' },
} as const;

export const FEE_VALUE_TYPES = {
  fixed: { en: 'Fixed', ar: 'ثابت' },
  percent: { en: 'Percentage', ar: 'نسبة' },
} as const;
```

---

## Validation Messages

```typescript
// lib/constants/validation.ts

export const VALIDATION_MESSAGES = {
  required: (field: string) => `${field} مطلوب`,
  minLength: (field: string, min: number) => `${field} يجب أن يكون على الأقل ${min}أحرف`,
  maxLength: (field: string, max: number) => `${field} يجب أن لا يتجاوز ${max} أحرف`,
  minValue: (field: string, min: number) => `${field} يجب أن يكون على الأقل ${min}`,
  maxValue: (field: string, max: number) => `${field} يجب أن لا يتجاوز ${max}`,
  invalidEmail: () => 'البريد الإلكتروني غير صالح',
  invalidNumber: () => 'الرقم غير صالح',
  invalidDate: () => 'التاريخ غير صالح',
  passwordMismatch: () => 'كلمات المرور غير متطابقة',
  stockInsufficient: (requested: number, available: number) => 
    `الكمية المطلوبة (${requested}) غير متوفرة. المتاح: ${available}`,
} as const;
```

---

## Summary

This data model provides:

1. **Arabic Constants**: Comprehensive translation strings for all UI elements
2. **Component Architecture**: Shared components for RTL and Arabic support
3. **Utility Functions**: Formatting and normalization functions
4. **New Pages**: Required pages for history, detail views
5. **Status Enums**: Arabic translations for all status values
6. **Validation Messages**: User-friendly Arabic validation error messages