export const PROJECT_STATUS = {
  DRAFT: { en: 'Draft', ar: 'قيد التنفيذ', key: 'draft' },
  COMPLETED: { en: 'Completed', ar: 'مكتمل', key: 'completed' },
} as const;

export const INVENTORY_REASONS = {
  sale: { en: 'Sale', ar: 'مبيعة', key: 'sale' },
  restock: { en: 'Restock', ar: 'إعادة تخزين', key: 'restock' },
  adjustment: { en: 'Adjustment', ar: 'تعديل', key: 'adjustment' },
  reversal: { en: 'Reversal', ar: 'إلغاء', key: 'reversal' },
} as const;

export const FEE_TYPES = {
  shipping: { en: 'Shipping', ar: 'الشحن', key: 'shipping' },
  installation: { en: 'Installation', ar: 'التركيب', key: 'installation' },
  custom: { en: 'Custom', ar: 'مخصص', key: 'custom' },
} as const;

export const FEE_VALUE_TYPES = {
  fixed: { en: 'Fixed', ar: 'ثابت', key: 'fixed' },
  percent: { en: 'Percentage', ar: 'نسبة', key: 'percent' },
} as const;

export const PAYMENT_METHOD_STATUS = {
  active: { en: 'Active', ar: 'نشط', key: 'active' },
  inactive: { en: 'Inactive', ar: 'غير نشط', key: 'inactive' },
} as const;

export const SALE_STATUS = {
  completed: { en: 'Completed', ar: 'مكتمل', key: 'completed' },
  reversed: { en: 'Reversed', ar: 'ملغي', key: 'reversed' },
} as const;

export const PRODUCT_STATUS = {
  active: { en: 'Active', ar: 'نشط', key: 'active' },
  inactive: { en: 'Inactive', ar: 'غير نشط', key: 'inactive' },
} as const;

export function getStatusLabel<T extends Record<string, { en: string; ar: string; key: string }>>(
  statusMap: T,
  statusKey: string
): string {
  const status = Object.values(statusMap).find((s) => s.key === statusKey || s.key === statusKey.toLowerCase());
  return status?.ar ?? statusKey;
}

export function getProjectStatusLabel(status: string): string {
  return getStatusLabel(PROJECT_STATUS, status);
}

export function getInventoryReasonLabel(reason: string): string {
  return getStatusLabel(INVENTORY_REASONS, reason);
}

export function getFeeTypeLabel(feeType: string): string {
  return getStatusLabel(FEE_TYPES, feeType);
}
