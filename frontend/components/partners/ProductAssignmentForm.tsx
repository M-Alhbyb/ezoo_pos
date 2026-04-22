"use client";

import { useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { User, Package, Hash, Percent, AlertCircle } from "lucide-react";
import NumberInput from "@/components/shared/NumberInput";

export interface ProductAssignment {
  id?: string;
  partner_id: number;
  product_id: string;
  assigned_quantity: number;
  share_percentage: string | number;
  status?: 'active' | 'fulfilled';
  remaining_quantity?: number;
}

interface Partner {
  id: number;
  name: string;
  share_percentage: string;
}

interface Product {
  id: string;
  name: string;
  category_id: string;
}

interface ProductAssignmentFormProps {
  assignment?: ProductAssignment | null;
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
    share_percentage: Number(assignment?.share_percentage) || 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const t = ARABIC.partners.assignments;
  const selectedPartner = partners.find(p => p.id === Number(formData.partner_id));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await onSubmit({
        ...formData,
        partner_id: Number(formData.partner_id),
        share_percentage: formData.share_percentage || Number(selectedPartner?.share_percentage) || 0,
      });
    } catch (err: any) {
      setError(err.message || ARABIC.errors.saveFailed);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5 text-start">
      {error && (
        <div className="bg-rose-50 border border-rose-100 text-rose-600 rounded-xl p-3 text-sm flex items-center gap-2">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      )}

      {/* Partner Selection */}
      <div className="space-y-1.5">
        <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1.5">
          <User className="w-3.5 h-3.5" />
          {t.partner} *
        </label>
        <select
          value={formData.partner_id}
          onChange={(e) => setFormData({ ...formData, partner_id: e.target.value })}
          className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary p-3 transition-all outline-none appearance-none"
          required
          disabled={!!assignment}
        >
          <option value="">اختر الشريك</option>
          {partners.map(partner => (
            <option key={partner.id} value={partner.id}>
              {partner.name} ({parseFloat(partner.share_percentage).toFixed(1)}%)
            </option>
          ))}
        </select>
      </div>

      {/* Product Selection */}
      <div className="space-y-1.5">
        <label className="text-xs font-bold text-slate-500 uppercase flex items-center gap-1.5">
          <Package className="w-3.5 h-3.5" />
          {t.product} *
        </label>
        <select
          value={formData.product_id}
          onChange={(e) => setFormData({ ...formData, product_id: e.target.value })}
          className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary p-3 transition-all outline-none appearance-none"
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

      <div className="grid grid-cols-2 gap-4">
        <NumberInput
          label={t.quantity}
          value={formData.assigned_quantity}
          onChange={(val) => setFormData({ ...formData, assigned_quantity: val })}
          required
          min={1}
        />

        <NumberInput
          label={t.share}
          suffix="%"
          value={formData.share_percentage}
          onChange={(val) => setFormData({ ...formData, share_percentage: val })}
          placeholder={selectedPartner?.share_percentage || "0.0"}
          max={100}
        />
      </div>

      <p className="text-[10px] text-slate-400 font-medium">
        * اترك نسبة الربح فارغة لاستخدام النسبة الافتراضية للشريك ({selectedPartner?.share_percentage || "0"}%).
      </p>

      {assignment && (
        <div className="bg-slate-50 p-4 rounded-2xl border border-slate-100 flex justify-between items-center">
          <div className="text-xs font-bold text-slate-500 uppercase">{t.status}</div>
          <div className={`px-2 py-0.5 rounded-full text-xs font-bold ${assignment.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
            {assignment.status === 'active' ? t.active : t.fulfilled}
          </div>
        </div>
      )}

      <div className="flex gap-3 pt-4 border-t border-slate-50">
        <button
          type="submit"
          disabled={loading}
          className="flex-grow bg-primary text-white py-3 px-6 rounded-2xl font-bold hover:bg-blue-600 transition-all shadow-md shadow-blue-100 disabled:opacity-50"
        >
          {loading ? ARABIC.common.saving : assignment ? t.editAssignment : t.newAssignment}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-3 bg-slate-100 text-slate-600 font-bold rounded-2xl hover:bg-slate-200 transition-all"
        >
          {ARABIC.common.cancel}
        </button>
      </div>
    </form>
  );
}