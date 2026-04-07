"use client";

import { useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";

interface Product {
  id: string;
  name: string;
  sku: string | null;
  category_id: string;
  category_name: string;
  base_price: string;
  selling_price: string;
  stock_quantity: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ProductListProps {
  products: Product[];
  onEdit?: (product: Product) => void;
  onDelete?: (productId: string) => void;
}

export default function ProductList({ products, onEdit, onDelete }: ProductListProps) {
  const [searchTerm, setSearchTerm] = useState("");

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (product.sku && product.sku.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <input
          type="text"
          placeholder={ARABIC.products.searchProducts}
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary px-4 py-2 w-64"
          dir="rtl"
        />
      </div>

      <div className="glass rounded-2xl overflow-hidden shadow-sm">
        <table className="min-w-full text-start">
          <thead>
            <tr className="bg-slate-50/50 border-b border-slate-200">
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.products.productName}</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.products.sku}</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.products.category}</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.products.sellingPrice}</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-center">{ARABIC.products.stockQuantity}</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.products.status}</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.common.actions}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white/50">
            {filteredProducts.map(product => (
              <tr key={product.id} className="hover:bg-slate-50/80 transition-colors">
                <td className="px-6 py-4 font-medium text-slate-800">{product.name}</td>
                <td className="px-6 py-4 text-slate-600 font-mono text-sm">{product.sku || ARABIC.common.none}</td>
                <td className="px-6 py-4 text-slate-600">{product.category_name}</td>
                <td className="px-6 py-4 text-end font-medium text-slate-800">{formatCurrency(product.selling_price)}</td>
                <td className="px-6 py-4 text-center">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${product.stock_quantity > 10 ? 'bg-emerald-100 text-emerald-800' : product.stock_quantity > 0 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'}`}>
                    {product.stock_quantity}
                  </span>
                </td>
                <td className="px-6 py-4">
                  {product.is_active ? (
                    <span className="flex items-center text-sm text-slate-600">
                      <div className="w-2 h-2 rounded-full bg-emerald-500 ms-2"></div>
                      {ARABIC.products.active}
                    </span>
                  ) : (
                    <span className="flex items-center text-sm text-slate-400">
                      <div className="w-2 h-2 rounded-full bg-slate-300 ms-2"></div>
                      {ARABIC.products.inactive}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => onEdit && onEdit(product)}
                      className="text-primary hover:text-primary-dark"
                    >
                      {ARABIC.common.edit}
                    </button>
                    {product.is_active && (
                      <button
                        onClick={() => onDelete && onDelete(product.id)}
                        className="text-rose-600 hover:text-rose-800"
                      >
                        {ARABIC.common.delete}
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredProducts.length === 0 && (
        <div className="text-center text-slate-400 py-8">
          {ARABIC.products.noProducts}
        </div>
      )}
    </div>
  );
}