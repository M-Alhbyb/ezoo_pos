/**
 * ProductModal Component
 * 
 * A premium, glassmorphic modal for creating and editing products.
 */

"use client";

import { useEffect, useState } from "react";
import ProductForm from "./ProductForm";

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

interface ProductModalProps {
  product?: Product;
  categories: Category[];
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: Partial<Product>) => Promise<void>;
}

export default function ProductModal({
  product,
  categories,
  isOpen,
  onClose,
  onSubmit,
}: ProductModalProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (isOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  if (!isOpen || !mounted) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      {/* Backdrop with blur */}
      <div 
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity animate-in fade-in duration-300"
        onClick={onClose}
      />
      
      {/* Modal Content */}
      <div className="relative w-full max-w-2xl bg-white/90 backdrop-blur-md rounded-3xl shadow-2xl border border-white/20 overflow-hidden animate-in zoom-in-95 fade-in duration-300">
        <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-white/50">
          <div>
            <h2 className="text-2xl font-bold text-slate-800 tracking-tight">
              {product ? "Edit Product" : "Add New Product"}
            </h2>
            <p className="text-slate-500 text-sm mt-0.5">
              {product ? "Update product details and pricing." : "Create a new product in your catalog."}
            </p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400 hover:text-slate-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <div className="p-8 max-h-[80vh] overflow-y-auto">
          <ProductForm 
            product={product} 
            categories={categories} 
            onSubmit={async (data) => {
              await onSubmit(data);
              onClose();
            }} 
            onCancel={onClose} 
          />
        </div>
      </div>
    </div>
  );
}
