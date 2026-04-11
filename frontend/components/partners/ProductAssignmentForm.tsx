/**
 * ProductAssignmentForm Component
 * 
 * Form for creating and editing product assignments to partners.
 * Task: T044 - Phase 7
 */

"use client";

import { useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";

interface ProductAssignment {
  id?: string;
  partner_id: string;
  product_id: string;
  assigned_quantity: number;
  share_percentage: string;
  status: string;
  remaining_quantity: number;
}

interface Partner {
  id: string;
  name: string;
  share_percentage: string;
}

interface Product {
  id: string;
  name: string;
  category_id: string;
}

interface ProductAssignmentFormProps {
  assignment?: ProductAssignment;
  partners: Partner[];
  products: Product[];
  onSubmit: (data: Partial<ProductAssignment>) => Promise<void>;
  onCancel: () => void;
}

export default function ProductAssignmentForm({
  assignment,
  partners,
  products,
  onSubmit,
  onCancel,
}: ProductAssignmentFormProps) {
  const [formData, setFormData] = useState({
    partner_id: assignment?.partner_id || "",
    product_id: assignment?.product_id || "",
    assigned_quantity: assignment?.assigned_quantity || 0,
    share_percentage: assignment?.share_percentage || "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const selectedPartner = partners.find(p => p.id === formData.partner_id);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await onSubmit({
        ...formData,
        share_percentage: formData.share_percentage || selectedPartner?.share_percentage,
      });
    } catch (err: any) {
      setError(err.message || "حدث خطأ في إنشاء المهمة");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-rose-600">{error}</div>}

      <div>
        <label className="block text-sm font-medium mb-1">
          الشريك *
        </label>
        <select
          value={formData.partner_id}
          onChange={(e) => setFormData({ ...formData, partner_id: e.target.value })}
          className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
          required
          disabled={!!assignment}
        >
          <option value="">اختر الشريك</option>
          {partners.map(partner => (
            <option key={partner.id} value={partner.id}>
              {partner.name} ({partner.share_percentage}%)
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          المنتج *
        </label>
        <select
          value={formData.product_id}
          onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
          className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
          required
          disabled={!!assignment}
        >
          <option value="">اختر المنتج</option>
          {products.map(product => (
            <option key={product.id} value={product.id}>
              {product.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          الكمية المخصصة *
        </label>
        <input
          type="number"
          value={formData.assigned_quantity}
          onChange={(e) => setFormData({ ...formData, assigned_quantity: parseInt(e.target.value) || 0 })}
          className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
          min="1"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          نسبة الربح % ({selectedPartner?.share_percentage}% افتراضي)
        </label>
        <input
          type="number"
          step="0.01"
          value={formData.share_percentage}
          onChange={(e) => setFormData({ ...formData, share_percentage: e.target.value })}
          className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
          placeholder={selectedPartner?.share_percentage}
          min="0"
          max="100"
        />
        <p className="text-xs text-slate-500 mt-1">
          اترك فارغ لاستخدام النسبة الافتراضية للشريك
        </p>
      </div>

      {assignment && (
        <div className="bg-slate-50 p-3 rounded-lg">
          <div className="text-sm text-slate-600">
            <div>الحالة: {assignment.status === 'active' ? 'نشط' : 'مكتمل'}</div>
            <div>الكمية المتبقية: {assignment.remaining_quantity} / {assignment.assigned_quantity}</div>
          </div>
        </div>
      )}

      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          disabled={loading}
          className="flex-1 bg-primary text-white py-2 px-4 rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50"
        >
          {loading ? "جارٍ الحفظ..." : assignment ? "تحديث المهمة" : "إنشاء المهمة"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 transition-colors"
        >
          إلغاء
        </button>
      </div>
    </form>
  );
}