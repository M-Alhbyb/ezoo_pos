import { Decimal } from 'decimal.js';

export function formatCurrency(value: number | string | Decimal): string {
  const num = typeof value === 'string' ? parseFloat(value) : typeof value === 'object' ? Number(value) : value;
  return new Intl.NumberFormat('ar-SD-u-nu-latn', {
    style: 'currency',
    currency: 'SDG',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

export function formatCurrencyCompact(value: number | string | Decimal): string {
  const num = typeof value === 'string' ? parseFloat(value) : typeof value === 'object' ? Number(value) : value;
  if (num >= 1000000) {
    return new Intl.NumberFormat('ar-SD-u-nu-latn', {
      style: 'currency',
      currency: 'SDG',
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(num);
  }
  return formatCurrency(num);
}

export function formatDate(date: Date | string, format: 'short' | 'long' = 'long'): string {
  const d = new Date(date);
  const options: Intl.DateTimeFormatOptions =
    format === 'long'
      ? { year: 'numeric', month: 'long', day: 'numeric' }
      : { year: 'numeric', month: 'short', day: 'numeric' };
  return new Intl.DateTimeFormat('ar-SD-u-nu-latn', options).format(d);
}

export function formatDateTime(date: Date | string): string {
  return new Intl.DateTimeFormat('ar-SD-u-nu-latn', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
  }).format(new Date(date));
}

export function formatTime(date: Date | string): string {
  return new Intl.DateTimeFormat('ar-SD-u-nu-latn', {
    hour: 'numeric',
    minute: 'numeric',
  }).format(new Date(date));
}

export function formatNumber(value: number, decimals: number = 0): string {
  return new Intl.NumberFormat('ar-SD-u-nu-latn', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return new Intl.NumberFormat('ar-SD-u-nu-latn', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100);
}

export function formatInteger(value: number): string {
  return new Intl.NumberFormat('ar-SD-u-nu-latn').format(Math.round(value));
}

export function formatDecimal(value: number | string | Decimal, places: number = 2): string {
  const num = typeof value === 'string' ? parseFloat(value) : typeof value === 'object' ? Number(value) : value;
  return num.toFixed(places);
}

export function formatWeight(kg: number): string {
  if (kg >= 1000) {
    return `${formatNumber(kg / 1000)} طن`;
  }
  return `${formatNumber(kg)} كجم`;
}

export function formatQuantity(quantity: number, unit: string = 'وحدة'): string {
  return `${formatNumber(quantity)} ${unit}`;
}

export function parseArabicNumber(input: string): number {
  const normalized = normalizeArabicNumerals(input);
  return parseFloat(normalized) || 0;
}

export function normalizeArabicNumerals(input: string): string {
  const arabicToWestern: Record<string, string> = {
    '٠': '0',
    '١': '1',
    '٢': '2',
    '٣': '3',
    '٤': '4',
    '٥': '5',
    '٦': '6',
    '٧': '7',
    '٨': '8',
    '٩': '9',
  };
  return input.replace(/[٠-٩]/g, (match) => arabicToWestern[match] || match);
}

export function toArabicNumerals(input: string | number): string {
  // Deactivated: return input as-is to use Latin digits globally
  return String(input);
}
