"use client";

import { useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";

interface Product {
  id: string;
  name: string;
  sku: string | null;
  selling_price: string;
  stock_quantity: number;
}

interface ProductSearchProps {
  onProductSelect: (product: Product) => void;
}

export default function ProductSearch({ onProductSelect }: ProductSearchProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const searchProducts = async (term: string) => {
    if (!term) {
      setProducts([]);
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`/api/products?search=${encodeURIComponent(term)}&active_only=true`);
      if (!response.ok) throw new Error("Failed to search products");

      const data = await response.json();
      setProducts(data.items);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const term = e.target.value;
    setSearchTerm(term);
    searchProducts(term);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">{ARABIC.pos.product}</label>
        <input
          type="text"
          value={searchTerm}
          onChange={handleSearch}
          placeholder={ARABIC.products.searchProducts}
          className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-3"
          dir="rtl"
        />
      </div>

      {loading && <div className="text-slate-500">{ARABIC.common.loading}</div>}

      {error && <div className="text-rose-600">{error}</div>}

      {!loading && products.length > 0 && (
        <div className="border border-slate-200 rounded-xl max-h-64 overflow-y-auto bg-white/50">
          {products.map((product) => (
            <button
              key={product.id}
              onClick={() => {
                onProductSelect(product);
                setSearchTerm("");
                setProducts([]);
              }}
              className="w-full text-start px-4 py-2 hover:bg-slate-50 border-b last:border-b-0 transition-colors"
            >
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-medium">{product.name}</div>
                  {product.sku && <div className="text-sm text-slate-500">{ARABIC.products.sku}: {product.sku}</div>}
                </div>
                <div className="text-end">
                  <div className="font-medium">{formatCurrency(product.selling_price)}</div>
                  <div className="text-sm text-slate-500">{ARABIC.products.inStock}: {product.stock_quantity}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {!loading && searchTerm && products.length === 0 && (
        <div className="text-slate-500 text-center py-4">{ARABIC.products.noProducts}</div>
      )}
    </div>
  );
}