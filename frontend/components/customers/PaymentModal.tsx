import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import NumberInput from "@/components/shared/NumberInput";

interface PaymentData {
  amount: number;
  payment_method: string;
  note?: string;
}

interface CustomerPaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: PaymentData) => Promise<void>;
  loading?: boolean;
}

export default function CustomerPaymentModal({ isOpen, onClose, onSubmit, loading: externalLoading }: CustomerPaymentModalProps) {
  const [amount, setAmount] = useState(0);
  const [paymentMethod, setPaymentMethod] = useState("Cash");
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      setAmount(0);
      setPaymentMethod("Cash");
      setNote("");
      setError("");
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (amount <= 0) {
      setError(ARABIC.pos.amount);
      return;
    }
    if (!paymentMethod.trim()) {
      setError(ARABIC.pos.paymentMethod);
      return;
    }

    setLoading(true);
    setError("");

    try {
      await onSubmit({
        amount,
        payment_method: paymentMethod.trim(),
        note: note.trim() || undefined,
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const isLoading = loading || externalLoading;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in text-start">
      <div className="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl animate-scale-up">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-xl font-semibold text-slate-800">{ARABIC.customers.recordPayment}</h2>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="mb-6 p-3 bg-rose-50 text-rose-700 rounded-xl text-sm border border-rose-200 flex items-center">
              <svg className="w-4 h-4 me-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
              {error}
            </div>
          )}

          <div className="space-y-5">
            <NumberInput
              label={ARABIC.customers.amount}
              suffix="ج.س"
              value={amount}
              onChange={setAmount}
              autoFocus
            />

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">{ARABIC.pos.paymentMethod}</label>
              <select
                value={paymentMethod}
                onChange={(e) => setPaymentMethod(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all font-medium text-slate-800"
              >
                <option value="Cash">نقداً</option>
                <option value="Bank Transfer">تحويل بنكي</option>
                <option value="Check">شيك</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">{ARABIC.customers.note}</label>
              <input
                type="text"
                value={note}
                onChange={(e) => setNote(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 transition-all font-medium text-slate-800"
                placeholder="ملاحظة عن الدفعة..."
              />
            </div>
          </div>

          <div className="mt-8 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              {ARABIC.common.cancel}
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-5 py-2.5 bg-emerald-600 text-white text-sm font-bold rounded-xl hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-100 flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isLoading ? ARABIC.common.saving : ARABIC.customers.recordPayment}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}