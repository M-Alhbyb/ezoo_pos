const ARABIC_TO_WESTERN: Record<string, string> = {
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

const WESTERN_TO_ARABIC: Record<string, string> = {
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

export function toWesternNumerals(input: string): string {
  return input.replace(/[٠-٩]/g, (match) => ARABIC_TO_WESTERN[match] || match);
}

export function toArabicNumerals(input: string | number): string {
  return String(input).replace(/[0-9]/g, (d) => WESTERN_TO_ARABIC[d] || d);
}

export function normalizeInput(value: string): string {
  return toWesternNumerals(value.trim());
}

export function normalizeNumber(value: string | number): number {
  const normalized = typeof value === 'string' ? toWesternNumerals(value) : String(value);
  return parseFloat(normalized) || 0;
}

export function isArabicNumeral(input: string): boolean {
  return /[٠-٩]/.test(input);
}

export function isWesternNumeral(input: string): boolean {
  return /[0-9]/.test(input);
}

export function containsArabicNumerals(input: string): boolean {
  return /[٠-٩]/.test(input);
}

export function containsWesternNumerals(input: string): boolean {
  return /[0-9]/.test(input);
}
