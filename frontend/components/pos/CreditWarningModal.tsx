"use client";

import { ARABIC } from "@/lib/constants/arabic";

interface CreditWarningModalProps {
  isOpen: boolean;
  currentBalance: number;
  creditLimit: number;
  saleAmount: number;
  newBalance: number;
  onConfirm: () => void;
  onCancel: () => void;
}

export default function CreditWarningModal({
  isOpen,
  currentBalance,
  creditLimit,
  saleAmount,
  newBalance,
  onConfirm,
  onCancel,
}: CreditWarningModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl animate-scale-up">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-amber-50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-amber-100 text-amber-600 flex items-center justify-center">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
              </svg>
            </div>
            <h2 className="text-xl font-bold text-amber-800">{ARABIC.customers.creditWarning}</h2>
          </div>
        </div>

        <div className="p-6">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mb-6">
            <p className="text-amber-800 text-sm text-center font-medium">
              ستتجاوز هذه البيع الحد الائتماني للعميل
            </p>
          </div>

          <div className="space-y-3 mb-6">
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">الرصيد الحالي:</span>
              <span className="font-bold text-slate-800">{currentBalance.toFixed(2)} ج.س</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">مبلغ البيع:</span>
              <span className="font-bold text-rose-600">+{saleAmount.toFixed(2)} ج.س</span>
            </div>
            <div className="flex justify-between text-sm border-t border-slate-100 pt-3">
              <span className="text-slate-500">الرصيد الجديد:</span>
              <span className="font-bold text-rose-600">{newBalance.toFixed(2)} ج.س</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-500">الحد الائتماني:</span>
              <span className="font-bold text-slate-800">{creditLimit.toFixed(2)} ج.س</span>
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={onCancel}
              className="flex-1 px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              {ARABIC.common.cancel}
            </button>
            <button
              onClick={onConfirm}
              className="flex-1 px-5 py-2.5 bg-amber-500 text-white text-sm font-bold rounded-xl hover:bg-amber-600 transition-all shadow-lg shadow-amber-100"
            >
              {ARABIC.common.confirm}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}