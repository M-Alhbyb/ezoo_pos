"use client";

import { useState, useEffect } from "react";
import { Search, Package, AlertCircle } from "lucide-react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";

interface Product {
  id: string;
  name: string;
  sku: string | null;
  selling_price: string;
  stock_quantity: number;
}

interface ProductSelectorProps {
  value: string;
  onChange: (productId: string) => void;
  placeholder?: string;
}

export default function ProductSelector({ value, onChange, placeholder }: ProductSelectorProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch("/api/products?active_only=true&page_size=100");
      if (!response.ok) throw new Error("Failed to fetch products");
      const data = await response.json();
      setProducts(data.items);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = products.filter(
    (p) =>
      p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      p.sku?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const selectedProduct = products.find((p) => p.id === value);

  if (loading) {
    return (
      <div className="w-full bg-white border border-slate-200 text-slate-500 text-sm rounded-xl p-3">
        {ARABIC.common.loading}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 text-sm flex items-center gap-2">
        <AlertCircle className="w-4 h-4" />
        {error}
      </div>
    );
  }

  return (
    <div className="relative">
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="w-full bg-white border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all p-3 cursor-pointer flex justify-between items-center"
      >
        {selectedProduct ? (
          <div className="flex items-center gap-2">
            <Package className="w-4 h-4 text-slate-400" />
            <span className="font-medium">{selectedProduct.name}</span>
            {selectedProduct.sku && (
              <span className="text-xs text-slate-400 font-mono">{selectedProduct.sku}</span>
            )}
          </div>
        ) : (
          <span className="text-slate-400">{placeholder || ARABIC.inventory.selectProduct}</span>
        )}
        <svg
          className={`w-4 h-4 text-slate-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setIsOpen(false)} />
          <div className="absolute z-20 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-lg overflow-hidden">
            <div className="p-3 border-b border-slate-100">
              <div className="relative">
                <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  placeholder={ARABIC.common.search || 'بحث...'}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full ps-10 pe-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none"
                  autoFocus
                />
              </div>
            </div>

            <div className="max-h-64 overflow-y-auto">
              {filteredProducts.length === 0 ? (
                <div className="p-4 text-center text-slate-400">
                  {ARABIC.products.noProducts || 'لا توجد منتجات'}
                </div>
              ) : (
                filteredProducts.map((product) => (
                  <div
                    key={product.id}
                    onClick={() => {
                      onChange(product.id);
                      setIsOpen(false);
                      setSearchQuery("");
                    }}
                    className={`p-3 cursor-pointer hover:bg-slate-50 transition-colors ${
                      product.id === value ? "bg-blue-50" : ""
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium text-slate-800">{product.name}</p>
                        {product.sku && (
                          <p className="text-xs text-slate-400 font-mono">{product.sku}</p>
                        )}
                      </div>
                      <div className="text-end">
                        <p className="font-semibold text-slate-800">{formatCurrency(product.selling_price)}</p>
                        <p className={`text-xs ${
                          product.stock_quantity === 0
                            ? "text-rose-600"
                            : product.stock_quantity <= 5
                            ? "text-amber-600"
                            : "text-emerald-600"
                        }`}>
                          {product.stock_quantity} {ARABIC.products.inStock || 'متوفر'}
                        </p>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}