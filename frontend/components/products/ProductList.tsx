/**
 * ProductList Component
 * 
 * Displays a paginated list of products with search and filtering capabilities.
 * Task: T042
 */

"use client";

import { useState } from "react";

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
          placeholder="Search products..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="border rounded px-4 py-2 w-64"
        />
      </div>

      <table className="min-w-full bg-white border">
        <thead>
          <tr className="bg-gray-100">
            <th className="text-left px-4 py-2">Name</th>
            <th className="text-left px-4 py-2">SKU</th>
            <th className="text-left px-4 py-2">Category</th>
            <th className="text-left px-4 py-2">Price</th>
            <th className="text-left px-4 py-2">Stock</th>
            <th className="text-left px-4 py-2">Status</th>
            <th className="text-left px-4 py-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {filteredProducts.map(product => (
            <tr key={product.id} className="border-t">
              <td className="px-4 py-2">{product.name}</td>
              <td className="px-4 py-2">{product.sku || "-"}</td>
              <td className="px-4 py-2">{product.category_name}</td>
              <td className="px-4 py-2">{product.selling_price}</td>
              <td className="px-4 py-2">{product.stock_quantity}</td>
              <td className="px-4 py-2">
                <span className={`px-2 py-1 rounded text-xs ${product.is_active ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}`}>
                  {product.is_active ? "Active" : "Inactive"}
                </span>
              </td>
              <td className="px-4 py-2">
                <button
                  onClick={() => onEdit && onEdit(product)}
                  className="text-blue-600 hover:text-blue-800 mr-2"
                >
                  Edit
                </button>
                {product.is_active && (
                  <button
                    onClick={() => onDelete && onDelete(product.id)}
                    className="text-red-600 hover:text-red-800"
                  >
                    Delete
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {filteredProducts.length === 0 && (
        <div className="text-center text-gray-500 py-8">
          No products found
        </div>
      )}
    </div>
  );
}