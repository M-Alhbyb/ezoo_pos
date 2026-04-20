"use client";

import { ARABIC } from "@/lib/constants/arabic";

interface Category {
  id: string;
  name: string;
  product_count: number;
}

interface CategoryFilterProps {
  categories: Category[];
  selectedCategoryId?: string;
  onSelect: (categoryId: string | undefined) => void;
}

export default function CategoryFilter({ categories, selectedCategoryId, onSelect }: CategoryFilterProps) {
  return (
    <div className="space-y-2">
      <h3 className="font-medium text-sm text-slate-400 uppercase tracking-wider">{ARABIC.products.category}</h3>
      <div className="space-y-1">
        <button
          onClick={() => onSelect(undefined)}
          className={`w-full text-start px-4 py-2.5 rounded-xl transition-all font-medium text-sm flex justify-between items-center ${
            !selectedCategoryId ? 'bg-slate-100 text-slate-800' : 'text-slate-600 hover:bg-slate-50'
          }`}
        >
          {ARABIC.products.allCategories}
        </button>
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => onSelect(category.id)}
            className={`w-full text-start px-4 py-2.5 rounded-xl transition-all font-medium text-sm flex justify-between items-center ${
              selectedCategoryId === category.id ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-50'
            }`}
          >
            <span className="truncate ps-2">{category.name}</span>
            <span className="bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full text-xs font-semibold">{category.product_count}</span>
          </button>
        ))}
      </div>
    </div>
  );
}