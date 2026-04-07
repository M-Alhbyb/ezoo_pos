/**
 * ConfirmButton Component
 * 
 * Button to submit sale with validation.
 * Task: T075
 */

"use client";

import { ARABIC } from "@/lib/constants/arabic";

interface ConfirmButtonProps {
  onConfirm: () => Promise<void>;
  disabled: boolean;
  loading: boolean;
}

export default function ConfirmButton({ onConfirm, disabled, loading }: ConfirmButtonProps) {
  const handleConfirm = async () => {
    if (disabled || loading) return;

    const confirmed = window.confirm(
      ARABIC.pos.confirmSaleMessage || 'هل أنت متأكد من إتمام هذا البيع؟ لا يمكن التراجع عن هذا الإجراء.'
    );

    if (confirmed) {
      await onConfirm();
    }
  };

  return (
    <button
      onClick={handleConfirm}
      disabled={disabled || loading}
      className={`
        w-full py-4 text-lg font-medium rounded
        ${disabled || loading
          ? "bg-slate-300 text-slate-500 cursor-not-allowed"
          : "bg-emerald-600 text-white hover:bg-emerald-700"
        }
      `}
    >
      {loading ? ARABIC.common.loading : ARABIC.pos.completeSale || 'إتمام البيع'}
    </button>
  );
}