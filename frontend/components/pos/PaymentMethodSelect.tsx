/**
 * PaymentMethodSelect Component
 * 
 * Select payment method from available options.
 * Task: T074
 */

"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";

interface PaymentMethod {
  id: string;
  name: string;
  is_active: boolean;
}

interface PaymentMethodSelectProps {
  value: string | null;
  onChange: (payment_method_id: string) => void;
}

export default function PaymentMethodSelect({ value, onChange }: PaymentMethodSelectProps) {
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
      setPaymentMethods(data.items.filter((pm: PaymentMethod) => pm.is_active));

      if (!value && data.items.length > 0) {
        onChange(data.items[0].id);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-slate-500">{ARABIC.common.loading}</div>;
  }

  if (error) {
    return <div className="text-red-600">{error}</div>;
  }

  if (paymentMethods.length === 0) {
    return <div className="text-red-600">{ARABIC.pos.noPaymentMethods || 'لا توجد طرق دفع متاحة'}</div>;
  }

  return (
    <div>
      <label className="block text-sm font-medium mb-1">{ARABIC.pos.paymentMethod || 'طريقة الدفع'} *</label>
      <select
        value={value || ""}
        onChange={(e) => onChange(e.target.value)}
        className="border rounded px-3 py-2 w-full"
      >
        <option value="">{ARABIC.pos.selectPaymentMethod || 'اختر طريقة الدفع'}</option>
        {paymentMethods.map((pm) => (
          <option key={pm.id} value={pm.id}>
            {pm.name}
          </option>
        ))}
      </select>
    </div>
  );
}