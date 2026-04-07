/**
 * ProductForm Component
 * 
 * Form for creating and editing products.
 * Task: T043
 */

"use client";

import { useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";

interface Product {
  id?: string;
  name: string;
  sku: string | null;
  category_id: string;
  base_price: string;
  selling_price: string;
  stock_quantity: number;
}

interface Category {
  id: string;
  name: string;
}

interface ProductFormProps {
  product?: Product;
  categories: Category[];
  onSubmit: (data: Partial<Product>) => Promise<void>;
  onCancel: () => void;
}

export default function ProductForm({ product, categories, onSubmit, onCancel }: ProductFormProps) {
  const [formData, setFormData] = useState({
    name: product?.name || "",
    sku: product?.sku || "",
    category_id: product?.category_id || "",
    base_price: product?.base_price || "",
    selling_price: product?.selling_price || "",
    stock_quantity: product?.stock_quantity || 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await onSubmit({
        ...formData,
        sku: formData.sku || null,
      });
    } catch (err: any) {
      setError(err.message || ARABIC.common.error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-rose-600">{error}</div>}

      <div>
        <label className="block text-sm font-medium mb-1">{ARABIC.products.productName} *</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
          dir="rtl"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">{ARABIC.products.sku} ({ARABIC.common.optional})</label>
        <input
          type="text"
          value={formData.sku}
          onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
          className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
          dir="ltr"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">{ARABIC.products.category} *</label>
        <select
          value={formData.category_id}
          onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
          className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
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

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">{ARABIC.products.basePrice} *</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.base_price}
            onChange={(e) => setFormData({ ...formData, base_price: e.target.value })}
            className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none text-end"
            dir="ltr"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">{ARABIC.products.sellingPrice} *</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.selling_price}
            onChange={(e) => setFormData({ ...formData, selling_price: e.target.value })}
            className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none text-end"
            dir="ltr"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">{ARABIC.inventory.balance}</label>
        <input
          type="number"
          min="0"
          value={formData.stock_quantity}
          onChange={(e) => setFormData({ ...formData, stock_quantity: parseInt(e.target.value) || 0 })}
          className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none text-end"
          dir="ltr"
        />
      </div>

      <div className="flex justify-end gap-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border border-slate-200 rounded-xl hover:bg-slate-50 text-slate-600"
          disabled={loading}
        >
          {ARABIC.common.cancel}
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary-dark disabled:opacity-50"
          disabled={loading}
        >
          {loading ? ARABIC.common.saving : ARABIC.common.save}
        </button>
      </div>
    </form>
  );
}