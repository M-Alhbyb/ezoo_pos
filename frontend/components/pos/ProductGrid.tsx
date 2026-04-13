/**
 * ProductGrid Component
 * 
 * Displays all active products in a grid for quick selection.
 * Supports category filtering.
 */

"use client";

import { useState, useEffect } from "react";
import { Search, Package, CheckCircle2, AlertCircle } from "lucide-react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";

interface Product {
  id: string;
  name: string;
  sku: string | null;
  category_id: string;
  category_name: string | null;
  category_color: string | null;
  selling_price: string;
  stock_quantity: number;
}

interface Category {
  id: string;
  name: string;
  product_count: number;
}

interface ProductGridProps {
  onProductSelect: (product: Product) => void;
}

export default function ProductGrid({ onProductSelect }: ProductGridProps) {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchQuery, setSearchQuery] = useState("");

  // Theme mapping for Tailwind safety (ensures classes are picked up by JIT)
  const CATEGORY_THEMES: Record<string, { bg: string; border: string; text: string; icon: string }> = {
    "bg-blue-50/60": { bg: "bg-blue-50/60", border: "border-blue-100/50", text: "text-blue-700", icon: "bg-blue-100/50 text-blue-600" },
    "bg-emerald-50/60": { bg: "bg-emerald-50/60", border: "border-emerald-100/50", text: "text-emerald-700", icon: "bg-emerald-100/50 text-emerald-600" },
    "bg-amber-50/60": { bg: "bg-amber-50/60", border: "border-amber-100/50", text: "text-amber-700", icon: "bg-amber-100/50 text-amber-600" },
    "bg-rose-50/60": { bg: "bg-rose-50/60", border: "border-rose-100/50", text: "text-rose-700", icon: "bg-rose-100/50 text-rose-600" },
    "bg-indigo-50/60": { bg: "bg-indigo-50/60", border: "border-indigo-100/50", text: "text-indigo-700", icon: "bg-indigo-100/50 text-indigo-600" },
    "bg-cyan-50/60": { bg: "bg-cyan-50/60", border: "border-cyan-100/50", text: "text-cyan-700", icon: "bg-cyan-100/50 text-cyan-600" },
    "bg-orange-50/60": { bg: "bg-orange-50/60", border: "border-orange-100/50", text: "text-orange-700", icon: "bg-orange-100/50 text-orange-600" },
    "bg-teal-50/60": { bg: "bg-teal-50/60", border: "border-teal-100/50", text: "text-teal-700", icon: "bg-teal-100/50 text-teal-600" },
    "bg-fuchsia-50/60": { bg: "bg-fuchsia-50/60", border: "border-fuchsia-100/50", text: "text-fuchsia-700", icon: "bg-fuchsia-100/50 text-fuchsia-600" },
    "bg-slate-100/50": { bg: "bg-slate-100/50", border: "border-slate-200/50", text: "text-slate-700", icon: "bg-slate-200/50 text-slate-600" },
  };

  const DEFAULT_THEME = { 
    bg: "bg-white hover:bg-slate-50", 
    border: "border-slate-200", 
    text: "text-slate-500", 
    icon: "bg-slate-100 text-slate-400" 
  };

  useEffect(() => {
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      
      // Fetch products and categories in parallel
      const [productsRes, categoriesRes] = await Promise.all([
        fetch("/api/products?active_only=true&page_size=100"),
        fetch("/api/categories")
      ]);

      if (!productsRes.ok || !categoriesRes.ok) {
        throw new Error("Failed to fetch products or categories");
      }

      const productsData = await productsRes.json();
      const categoriesData = await categoriesRes.json();

      setProducts(productsData.items);
      setCategories(categoriesData.items);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredProducts = products.filter(product => {
    const matchesCategory = !selectedCategoryId || product.category_id === selectedCategoryId;
    const matchesSearch = !searchQuery || 
      product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      product.sku?.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
        <p className="text-slate-500 font-medium animate-pulse">{ARABIC.common.loading}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center py-12 px-6 glass rounded-2xl border-rose-100 bg-rose-50/30">
        <AlertCircle className="w-12 h-12 text-rose-500 mb-3" />
        <p className="text-rose-700 font-semibold">{ARABIC.common.error}</p>
        <p className="text-rose-600/70 text-sm mt-1 text-center">{error}</p>
        <button 
          onClick={fetchInitialData}
          className="mt-4 px-4 py-2 bg-rose-100/50 hover:bg-rose-100 text-rose-700 rounded-xl text-sm font-medium transition-all"
        >
          {ARABIC.common.tryAgain || 'حاول مرة أخرى'}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Category Tabs & Search Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-2 overflow-x-auto pb-2 scrollbar-hide no-scrollbar">
          <button
            onClick={() => setSelectedCategoryId(null)}
            className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all whitespace-nowrap ${
              selectedCategoryId === null
                ? "bg-primary text-white shadow-lg shadow-primary/30"
                : "bg-slate-100 text-slate-600 hover:bg-slate-200"
            }`}
          >
            {ARABIC.products.allCategories || 'الكل'}
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategoryId(cat.id)}
              className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all whitespace-nowrap ${
                selectedCategoryId === cat.id
                  ? "bg-primary text-white shadow-lg shadow-primary/30"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>

        <div className="relative group">
          <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400 group-focus-within:text-primary transition-colors" />
          <input
            type="text"
            placeholder={ARABIC.pos.searchProducts || 'البحث عن منتجات...'}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="ps-10 pe-4 py-2 bg-slate-100/50 border border-slate-200 rounded-xl text-sm w-full md:w-64 focus:ring-2 focus:ring-primary/20 focus:border-primary focus:bg-white outline-none transition-all"
          />
        </div>
      </div>

      {/* Product Grid Area */}
      <div className="max-h-[500px] overflow-y-auto pe-2 no-scrollbar">
        {filteredProducts.length > 0 ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 pb-4">
            {filteredProducts.map((product) => {
              const theme = (product.category_color && CATEGORY_THEMES[product.category_color]) || DEFAULT_THEME;
              
              return (
                <button
                  key={product.id}
                  onClick={() => product.stock_quantity > 0 && onProductSelect(product)}
                  disabled={product.stock_quantity <= 0}
                  className={`group relative flex flex-col p-4 ${theme.bg} ${
                    product.stock_quantity > 0 
                      ? "hover:bg-white hover:shadow-xl hover:-translate-y-1 border-primary/10" 
                      : "opacity-60 grayscale cursor-not-allowed bg-slate-100 border-slate-200"
                  } border ${theme.border} hover:border-primary/20 rounded-2xl text-start transition-all duration-300`}
                >
                  <div className="flex-1">
                    <div className="flex justify-between items-start mb-1">
                      <span className={`text-[10px] font-bold ${theme.text} uppercase tracking-widest truncate max-w-[100px]`}>
                        {product.category_name || ARABIC.categories.title || "غير مصنف"}
                      </span>
                      {product.stock_quantity <= 0 ? (
                        <span className="flex items-center text-[10px] font-bold text-slate-500">
                          <Package className="w-2.5 h-2.5 me-0.5" />
                          {ARABIC.products.outOfStock || 'نفدت الكمية'}
                        </span>
                      ) : product.stock_quantity <= 5 ? (
                        <span className="flex items-center text-[10px] font-bold text-rose-500 animate-pulse">
                          <AlertCircle className="w-2.5 h-2.5 me-0.5" />
                          {ARABIC.products.lowStock || 'منخفض'}
                        </span>
                      ) : null}
                    </div>
                    <h3 className="text-sm font-bold text-slate-800 line-clamp-2 mb-1 group-hover:text-primary transition-colors">
                      {product.name}
                    </h3>
                    <p className="text-[10px] text-slate-400 font-medium truncate mb-3">
                      {product.sku || ARABIC.products.sku || 'بدون رمز'}
                    </p>
                  </div>
                  
                  <div className="flex items-end justify-between mt-auto">
                    <div>
                      <p className="text-[10px] text-slate-400 font-semibold mb-0.5 uppercase tracking-tighter">{ARABIC.pos.price || 'السعر'}</p>
                      <p className="text-base font-black text-slate-900 tracking-tight">
                        {formatCurrency(product.selling_price)}
                      </p>
                    </div>
                    <div className={`p-2 ${theme.icon} ${product.stock_quantity > 0 ? "group-hover:bg-primary group-hover:text-white" : ""} rounded-xl transition-all duration-300 shadow-sm`}>
                       <Package className="w-4 h-4" />
                    </div>
                  </div>

                  {/* Hover Effect Ring */}
                  {product.stock_quantity > 0 && (
                    <div className="absolute inset-0 border-2 border-primary/0 group-active:border-primary/40 rounded-2xl transition-all"></div>
                  )}
                </button>
              );
            })}
        </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 px-6 glass rounded-2xl">
            <Package className="w-16 h-16 text-slate-200 mb-4" />
            <h3 className="text-lg font-bold text-slate-400">{ARABIC.products.noProducts || 'لا توجد منتجات'}</h3>
            <p className="text-slate-400/60 text-sm mt-1">{ARABIC.pos.tryAdjustingFilters || 'جرب تعديل الفلاتر أو البحث'}</p>
            {(selectedCategoryId || searchQuery) && (
              <button 
                onClick={() => {
                  setSelectedCategoryId(null);
                  setSearchQuery("");
                }}
                className="mt-4 px-4 py-2 text-primary font-bold text-sm hover:underline"
              >
                {ARABIC.common.clearAll || 'مسح الكل'}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
