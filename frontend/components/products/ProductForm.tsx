"use client";

import { useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { User, Package, Hash, Percent, TrendingUp } from "lucide-react";

interface Product {
  id?: string;
  name: string;
  sku: string | null;
  category_id: string;
  base_price: string;
  selling_price: string;
  stock_quantity: number;
  partner_id?: string | null;
}

interface Category {
  id: string;
  name: string;
}

interface Partner {
  id: string;
  name: string;
  share_percentage: string;
}

interface ProductFormProps {
  product?: Product;
  categories: Category[];
  partners: Partner[];
  onSubmit: (data: any) => Promise<void>;
  onCancel: () => void;
}

export default function ProductForm({ product, categories, partners, onSubmit, onCancel }: ProductFormProps) {
  const [formData, setFormData] = useState({
    name: product?.name || "",
    sku: product?.sku || "",
    category_id: product?.category_id || "",
    base_price: product?.base_price || "",
    selling_price: product?.selling_price || "",
    stock_quantity: product?.stock_quantity || 0,
    partner_id: product?.partner_id || "",
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const t_assign = ARABIC.partners.assignments;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await onSubmit({
        ...formData,
        sku: formData.sku || null,
        partner_id: formData.partner_id || null,
      });
    } catch (err: any) {
      setError(err.message || ARABIC.common.error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-700 rounded-2xl p-4 text-sm flex items-center gap-3 animate-slide-up">
          <Package className="w-5 h-5 text-rose-500" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {/* Core Product Info */}
      <div className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.products.productName} *</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary p-3 transition-all outline-none"
              dir="rtl"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.products.sku} ({ARABIC.common.optional})</label>
            <input
              type="text"
              value={formData.sku || ""}
              onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary p-3 transition-all outline-none"
              dir="ltr"
              placeholder="SKU-0000"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.products.category} *</label>
          <select
            value={formData.category_id}
            onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
            className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary p-3 transition-all outline-none appearance-none"
            required
          >
            <option value="">{ARABIC.common.selectCategory}</option>
            {categories.map(cat => (
              <option key={cat.id} value={cat.id}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>

        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.products.basePrice} *</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.base_price}
              onChange={(e) => setFormData({ ...formData, base_price: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary p-3 transition-all outline-none text-end"
              dir="ltr"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.products.sellingPrice} *</label>
            <input
              type="number"
              step="0.01"
              min="0"
              value={formData.selling_price}
              onChange={(e) => setFormData({ ...formData, selling_price: e.target.value })}
              className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary p-3 transition-all outline-none text-end"
              dir="ltr"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-1.5">{ARABIC.inventory.balance}</label>
            <input
              type="number"
              min="0"
              value={formData.stock_quantity}
              onChange={(e) => setFormData({ ...formData, stock_quantity: parseInt(e.target.value) || 0 })}
              className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary p-3 transition-all outline-none text-end"
              dir="ltr"
            />
          </div>
        </div>
      </div>

      {/* Assignment Section */}
      <div className="bg-slate-50/50 border border-slate-100 rounded-2xl p-6 relative overflow-hidden group/assign">
        <div className="absolute top-0 right-0 w-24 h-24 bg-primary/5 rounded-full -mr-12 -mt-12 blur-2xl group-hover/assign:bg-primary/10 transition-colors"></div>
        
        <h3 className="text-sm font-bold text-slate-700 mb-4 flex items-center gap-2 relative">
          <TrendingUp className="w-4 h-4 text-primary" />
          {t_assign.partner}
          <span className="text-[10px] font-medium text-slate-400 font-sans tracking-wide">({ARABIC.common.optional})</span>
        </h3>

        <div className="space-y-4 relative">
          <div>
            <label className="block text-[10px] font-bold text-slate-400 uppercase mb-1.5 flex items-center gap-1.5">
              <User className="w-3 h-3" />
              {t_assign.partner}
            </label>
            <select
              value={formData.partner_id || ""}
              onChange={(e) => setFormData({ ...formData, partner_id: e.target.value })}
              className="w-full bg-white border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-4 focus:ring-primary/10 focus:border-primary p-3 transition-all outline-none appearance-none"
            >
              <option value="">{ARABIC.common.none}</option>
              {partners.map(partner => (
                <option key={partner.id} value={partner.id}>
                  {partner.name} ({parseFloat(partner.share_percentage).toFixed(1)}%)
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-6 py-2.5 border border-slate-200 rounded-xl hover:bg-slate-50 text-slate-600 font-bold transition-all"
          disabled={loading}
        >
          {ARABIC.common.cancel}
        </button>
        <button
          type="submit"
          className="px-8 py-2.5 bg-primary text-white rounded-xl hover:bg-blue-600 disabled:opacity-50 font-bold transition-all shadow-md shadow-blue-100"
          disabled={loading}
        >
          {loading ? ARABIC.common.saving : ARABIC.common.save}
        </button>
      </div>
    </form>
  );
}