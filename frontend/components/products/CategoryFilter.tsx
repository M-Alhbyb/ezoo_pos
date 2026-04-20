/**
 * CategoryFilter Component
 * 
 * Filter component for products by category.
 * Task: T044
 */

"use client";

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
      <h3 className="font-medium">Categories</h3>
      <div className="space-y-1">
        <button
          onClick={() => onSelect(undefined)}
          className={`w-full text-left px-3 py-2 rounded ${
            !selectedCategoryId ? "bg-blue-100 text-blue-800" : "hover:bg-gray-100"
          }`}
        >
          All Products
        </button>
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => onSelect(category.id)}
            className={`w-full text-left px-3 py-2 rounded ${
              selectedCategoryId === category.id ? "bg-blue-100 text-blue-800" : "hover:bg-gray-100"
            }`}
          >
            {category.name} ({category.product_count})
          </button>
        ))}
      </div>
    </div>
  );
}