/**
 * ProductForm Component
 * 
 * Form for creating and editing products.
 * Task: T043
 */

"use client";

import { useState } from "react";

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
      setError(err.message || "Failed to save product");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && <div className="text-red-600">{error}</div>}

      <div>
        <label className="block text-sm font-medium mb-1">Name *</label>
        <input
          type="text"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          className="border rounded px-3 py-2 w-full"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">SKU (optional)</label>
        <input
          type="text"
          value={formData.sku}
          onChange={(e) => setFormData({ ...formData, sku: e.target.value })}
          className="border rounded px-3 py-2 w-full"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Category *</label>
        <select
          value={formData.category_id}
          onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
          className="border rounded px-3 py-2 w-full"
          required
        >
          <option value="">Select a category</option>
          {categories.map(cat => (
            <option key={cat.id} value={cat.id}>
              {cat.name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Base Price *</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.base_price}
            onChange={(e) => setFormData({ ...formData, base_price: e.target.value })}
            className="border rounded px-3 py-2 w-full"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-1">Selling Price *</label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.selling_price}
            onChange={(e) => setFormData({ ...formData, selling_price: e.target.value })}
            className="border rounded px-3 py-2 w-full"
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Initial Stock</label>
        <input
          type="number"
          min="0"
          value={formData.stock_quantity}
          onChange={(e) => setFormData({ ...formData, stock_quantity: parseInt(e.target.value) || 0 })}
          className="border rounded px-3 py-2 w-full"
        />
      </div>

      <div className="flex justify-end space-x-2">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 border rounded hover:bg-gray-100"
          disabled={loading}
        >
          Cancel
        </button>
        <button
          type="submit"
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Saving..." : "Save"}
        </button>
      </div>
    </form>
  );
}