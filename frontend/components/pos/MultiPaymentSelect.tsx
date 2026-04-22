/**
 * MultiPaymentSelect Component
 * 
 * Allows users to split a sale among multiple payment methods.
 */

"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import NumberInput from "@/components/shared/NumberInput";

interface PaymentMethod {
  id: string;
  name: string;
  is_active: boolean;
}

export interface SalePayment {
  payment_method_id: string;
  amount: number;
}

interface MultiPaymentSelectProps {
  total: number;
  payments: SalePayment[];
  onChange: (payments: SalePayment[]) => void;
}

export default function MultiPaymentSelect({ total, payments, onChange }: MultiPaymentSelectProps) {
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchPaymentMethods();
  }, []);

  const fetchPaymentMethods = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/payment-methods");
      if (!response.ok) throw new Error("Failed to fetch payment methods");

      const data = await response.json();
      const activeMethods = data.items.filter((pm: PaymentMethod) => pm.is_active);
      setPaymentMethods(activeMethods);

      // Initialize with one payment method if empty
      if (payments.length === 0 && activeMethods.length > 0) {
        onChange([{ payment_method_id: activeMethods[0].id, amount: total }]);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addPayment = () => {
    if (paymentMethods.length === 0) return;
    
    const currentTotal = payments.reduce((sum, p) => sum + p.amount, 0);
    const remaining = Math.max(0, total - currentTotal);
    
    onChange([
      ...payments,
      { payment_method_id: paymentMethods[0].id, amount: remaining }
    ]);
  };

  const removePayment = (index: number) => {
    if (payments.length <= 1) return;
    const newPayments = payments.filter((_, i) => i !== index);
    onChange(newPayments);
  };

  const updatePayment = (index: number, updates: Partial<SalePayment>) => {
    const newPayments = payments.map((p, i) => 
      i === index ? { ...p, ...updates } : p
    );
    onChange(newPayments);
  };

  const currentSum = payments.reduce((sum, p) => sum + p.amount, 0);
  const isBalanced = Math.abs(currentSum - total) < 0.01;

  if (loading) return <div className="text-slate-500 text-sm py-2">{ARABIC.common.loading}...</div>;
  if (error) return <div className="text-rose-500 text-sm py-2">{error}</div>;

  return (
    <div className="space-y-4 text-start">
      <div className="flex justify-between items-center">
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">
          {ARABIC.pos.paymentMethod || 'طريقة الدفع'}
        </label>
        <button
          type="button"
          onClick={addPayment}
          className="text-xs font-medium text-primary hover:text-primary-dark transition-colors flex items-center"
        >
          <svg className="w-3.5 h-3.5 me-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4" />
          </svg>
          {ARABIC.common?.add || 'إضافة'}
        </button>
      </div>

      <div className="space-y-3">
        {payments.map((payment, index) => (
          <div key={index} className="flex gap-2 items-start">
            <div className="flex-grow">
              <select
                value={payment.payment_method_id}
                onChange={(e) => updatePayment(index, { payment_method_id: e.target.value })}
                className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all shadow-sm"
              >
                {paymentMethods.map((pm) => (
                  <option key={pm.id} value={pm.id}>{pm.name}</option>
                ))}
              </select>
            </div>
            <div className="w-40">
              <NumberInput
                value={payment.amount}
                onChange={(val) => updatePayment(index, { amount: val })}
                className="p-2.5 rounded-xl text-sm"
                containerClassName="w-full"
              />
            </div>
            {payments.length > 1 && (
              <button
                type="button"
                onClick={() => removePayment(index)}
                className="p-2.5 text-slate-400 hover:text-rose-500 transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>
        ))}
      </div>

      <div className={`text-xs font-medium p-2.5 rounded-lg flex justify-between items-center ${isBalanced ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' : 'bg-rose-50 text-rose-700 border border-rose-100'}`}>
        <span>{ARABIC.pos.total || 'المجموع'}: {total.toLocaleString()} {ARABIC.common?.currency || 'ج.س'}</span>
        <div className="flex items-center">
          {isBalanced ? (
            <svg className="w-4 h-4 me-1.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-4 h-4 me-1.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          )}
          <span>{ARABIC.pos.remaining || 'المتبقي'}: {(total - currentSum).toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
        </div>
      </div>
    </div>
  );
}
