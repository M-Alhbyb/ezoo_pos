import { Decimal } from 'decimal.js';

export function formatCurrency(value: number | string | Decimal): string {
  const num = typeof value === 'string' ? parseFloat(value) : typeof value === 'object' ? Number(value) : value;
  return new Intl.NumberFormat('ar-SD', {
    style: 'currency',
    currency: 'SDG',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(num);
}

export function formatCurrencyCompact(value: number | string | Decimal): string {
  const num = typeof value === 'string' ? parseFloat(value) : typeof value === 'object' ? Number(value) : value;
  if (num >= 1000000) {
    return new Intl.NumberFormat('ar-SD', {
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
  return new Intl.DateTimeFormat('ar-SD', options).format(d);
}

export function formatDateTime(date: Date | string): string {
  return new Intl.DateTimeFormat('ar-SD', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
  }).format(new Date(date));
}

export function formatTime(date: Date | string): string {
  return new Intl.DateTimeFormat('ar-SD', {
    hour: 'numeric',
    minute: 'numeric',
  }).format(new Date(date));
}

export function formatNumber(value: number, decimals: number = 0): string {
  return new Intl.NumberFormat('ar-SD', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return new Intl.NumberFormat('ar-SD', {
    style: 'percent',
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100);
}

export function formatInteger(value: number): string {
  return new Intl.NumberFormat('ar-SD').format(Math.round(value));
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
  const westernToArabic: Record<string, string> = {
    '0': '٠',
    '1': '١',
    '2': '٢',
    '3': '٣',
    '4': '٤',
    '5': '٥',
    '6': '٦',
    '7': '٧',
    '8': '٨',
    '9': '٩',
  };
  return String(input).replace(/[0-9]/g, (d) => westernToArabic[d] || d);
}
