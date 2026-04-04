"use client";

import { useState, useEffect } from "react";

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
}

interface Category {
  id: string;
  name: string;
  product_count: number;
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, []);

  const fetchProducts = async (categoryId?: string, search?: string) => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (categoryId) params.append("category_id", categoryId);
      if (search) params.append("search", search);
      
      const response = await fetch(`/api/products?${params.toString()}`);
      if (!response.ok) throw new Error("Failed to fetch products");
      
      const data = await response.json();
      setProducts(data.items);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch("/api/categories");
      if (!response.ok) throw new Error("Failed to fetch categories");
      
      const data = await response.json();
      setCategories(data.items);
    } catch (err: any) {
      console.error("Failed to fetch categories:", err);
    }
  };

  const handleDelete = async (productId: string) => {
    try {
      const response = await fetch(`/api/products/${productId}`, {
        method: "DELETE",
      });
      
      if (!response.ok) throw new Error("Failed to delete product");
      
      setProducts(products.filter(p => p.id !== productId));
    } catch (err: any) {
      alert(err.message);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Products</h1>
        <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
          Add Product
        </button>
      </div>

      {error && (
        <div className="bg-red-100 text-red-700 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}

      <div className="flex gap-6">
        <aside className="w-64">
          <div className="border rounded p-4">
            <h2 className="font-medium mb-2">Filter by Category</h2>
            {categories.map(cat => (
              <button
                key={cat.id}
                className="block w-full text-left px-2 py-1 hover:bg-gray-100 rounded"
                onClick={() => fetchProducts(cat.id)}
              >
                {cat.name} ({cat.product_count})
              </button>
            ))}
            <button
              className="block w-full text-left px-2 py-1 hover:bg-gray-100 rounded mt-2 font-medium"
              onClick={() => fetchProducts()}
            >
              All Categories
            </button>
          </div>
        </aside>

        <main className="flex-1">
          {loading ? (
            <div className="text-center py-8">Loading products...</div>
          ) : (
            <div className="border rounded">
              <table className="min-w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="text-left px-4 py-2">Name</th>
                    <th className="text-left px-4 py-2">SKU</th>
                    <th className="text-left px-4 py-2">Category</th>
                    <th className="text-left px-4 py-2">Price</th>
                    <th className="text-left px-4 py-2">Stock</th>
                    <th className="text-left px-4 py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(product => (
                    <tr key={product.id} className="border-t">
                      <td className="px-4 py-2">{product.name}</td>
                      <td className="px-4 py-2">{product.sku || "-"}</td>
                      <td className="px-4 py-2">{product.category_name}</td>
                      <td className="px-4 py-2">${product.selling_price}</td>
                      <td className="px-4 py-2">{product.stock_quantity}</td>
                      <td className="px-4 py-2">
                        <button
                          onClick={() => handleDelete(product.id)}
                          className="text-red-600 hover:underline"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {products.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  No products found
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}