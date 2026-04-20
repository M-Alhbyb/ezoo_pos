export const VALIDATION_MESSAGES = {
  required: (field: string) => `${field} مطلوب`,
  minLength: (field: string, min: number) => `${field} يجب أن يكون على الأقل ${min} أحرف`,
  maxLength: (field: string, max: number) => `${field} يجب أن لا يتجاوز ${max} أحرف`,
  minValue: (field: string, min: number) => `${field} يجب أن يكون على الأقل ${min}`,
  maxValue: (field: string, max: number) => `${field} يجب أن لا يتجاوز ${max}`,
  invalidEmail: () => 'البريد الإلكتروني غير صالح',
  invalidNumber: () => 'الرقم غير صالح',
  invalidDate: () => 'التاريخ غير صالح',
  invalidPhone: () => 'رقم الهاتف غير صالح',
  passwordMismatch: () => 'كلمات المرور غير متطابقة',
  stockInsufficient: (requested: number, available: number) =>
    `الكمية المطلوبة (${requested}) غير متوفرة. المتاح: ${available}`,
  positiveNumber: (field: string) => `${field} يجب أن يكون رقماً موجباً`,
  nonNegative: (field: string) => `${field} لا يمكن أن يكون سالباً`,
  invalidUUID: () => 'معرّف غير صالح',
  duplicateEntry: (field: string) => `${field} موجود بالفعل`,
  invalidFormat: (field: string) => `${field} بتنسيق غير صالح`,
  maxPercentage: () => 'النسبة لا يمكن أن تتجاوز 100%',
  invalidPercentage: () => 'النسبة المئوية غير صالحة',
} as const;

export function getValidationMessage(
  key: keyof typeof VALIDATION_MESSAGES,
  ...args: (string | number)[]
): string {
  const message = VALIDATION_MESSAGES[key];
  if (typeof message === 'function') {
    return message(...args);
  }
  return message;
}
