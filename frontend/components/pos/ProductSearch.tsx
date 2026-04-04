/**
 * ProductSearch Component
 * 
 * Search products by name or SKU for adding to cart.
 * Task: T070
 */

"use client";

import { useState } from "react";

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
        <label className="block text-sm font-medium mb-1">Search Products</label>
        <input
          type="text"
          value={searchTerm}
          onChange={handleSearch}
          placeholder="Search by name or SKU..."
          className="border rounded px-3 py-2 w-full"
        />
      </div>

      {loading && <div className="text-gray-500">Searching...</div>}

      {error && <div className="text-red-600">{error}</div>}

      {!loading && products.length > 0 && (
        <div className="border rounded max-h-64 overflow-y-auto">
          {products.map((product) => (
            <button
              key={product.id}
              onClick={() => {
                onProductSelect(product);
                setSearchTerm("");
                setProducts([]);
              }}
              className="w-full text-left px-4 py-2 hover:bg-gray-50 border-b last:border-b-0"
            >
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-medium">{product.name}</div>
                  {product.sku && <div className="text-sm text-gray-500">SKU: {product.sku}</div>}
                </div>
                <div className="text-right">
                  <div className="font-medium">${product.selling_price}</div>
                  <div className="text-sm text-gray-500">Stock: {product.stock_quantity}</div>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}

      {!loading && searchTerm && products.length === 0 && (
        <div className="text-gray-500 text-center py-4">No products found</div>
      )}
    </div>
  );
}