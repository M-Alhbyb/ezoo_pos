"use client";
import { useState, useEffect } from "react";
import ProductModal from "@/components/products/ProductModal";
import CategoryModal from "@/components/products/CategoryModal";
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
}

interface Category {
  id: string;
  name: string;
  product_count: number;
}

export default function ProductsPage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [activeCategoryId, setActiveCategoryId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | undefined>(undefined);
  
  // Category CRUD state
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<Category | undefined>(undefined);

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, []);

  const fetchProducts = async (categoryId?: string, search?: string) => {
    try {
      setLoading(true);
      setActiveCategoryId(categoryId || null);
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

  const handleAddCategory = () => {
    setEditingCategory(undefined);
    setIsCategoryModalOpen(true);
  };

  const handleEditCategory = (category: Category, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingCategory(category);
    setIsCategoryModalOpen(true);
  };

  const handleDeleteCategory = async (categoryId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(ARABIC.common.confirmDelete)) return;
    
    try {
      const response = await fetch(`/api/categories/${categoryId}`, {
        method: "DELETE",
      });
      
      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail?.error?.message || "Failed to delete category");
      }
      
      if (activeCategoryId === categoryId) {
        setActiveCategoryId(null);
        await fetchProducts();
      }
      await fetchCategories();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleSaveCategory = async (data: { name: string }) => {
    try {
      const url = editingCategory 
        ? `/api/categories/${editingCategory.id}` 
        : "/api/categories";
      const method = editingCategory ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail?.error?.message || "Failed to save category");
      }

      await fetchCategories();
      setIsCategoryModalOpen(false);
    } catch (err: any) {
      throw err;
    }
  };

  const handleDelete = async (productId: string) => {
    if (!confirm(ARABIC.common.confirmDelete)) return;
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

  const handleEditProduct = (product: Product) => {
    setEditingProduct(product);
    setIsModalOpen(true);
  };

  const handleAddProduct = () => {
    setEditingProduct(undefined);
    setIsModalOpen(true);
  };

  const handleSaveProduct = async (data: Partial<Product>) => {
    try {
      const url = editingProduct 
        ? `/api/products/${editingProduct.id}` 
        : "/api/products";
      const method = editingProduct ? "PATCH" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to save product");
      }

      await fetchProducts(activeCategoryId || undefined);
      await fetchCategories();
      setIsModalOpen(false);
    } catch (err: any) {
      throw err;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.products.title}</h1>
          <p className="text-slate-500 mt-1">{ARABIC.products.subtitle}</p>
        </div>
        <button 
          onClick={handleAddProduct}
          className="flex items-center px-4 py-2.5 bg-primary text-white font-medium rounded-xl hover:bg-blue-600 transition-all shadow-sm shadow-blue-200"
        >
          <svg className="w-5 h-5 ms-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
          {ARABIC.products.addProduct}
        </button>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl mb-4 border border-rose-200 animate-slide-up flex items-center shadow-sm">
          <svg className="w-5 h-5 ms-3 text-rose-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-6">
        <aside className="w-full md:w-64 shrink-0">
          <div className="glass p-5 rounded-2xl sticky top-24">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">{ARABIC.products.filterByCategory}</h2>
              <button 
                onClick={handleAddCategory}
                className="p-1.5 text-indigo-500 hover:bg-indigo-50 rounded-lg transition-colors"
                title={ARABIC.categories.addCategory}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
              </button>
            </div>
            <div className="space-y-1">
              <button
                className={`w-full text-start px-4 py-2.5 rounded-xl transition-all font-medium text-sm flex justify-between items-center ${activeCategoryId === null ? 'bg-slate-100 text-slate-800' : 'text-slate-600 hover:bg-slate-50'}`}
                onClick={() => fetchProducts()}
              >
                {ARABIC.products.allCategories}
              </button>
              {categories.map(cat => (
                <button
                  key={cat.id}
                  className={`w-full text-start px-4 py-2.5 rounded-xl transition-all font-medium text-sm flex justify-between items-center group/cat ${activeCategoryId === cat.id ? 'bg-indigo-50 text-indigo-700' : 'text-slate-600 hover:bg-slate-50'}`}
                  onClick={() => fetchProducts(cat.id)}
                >
                  <div className="flex items-center gap-2 min-w-0 flex-1 ps-1">
                    <span className="truncate">{cat.name}</span>
                    <div className="flex items-center gap-0.5 opacity-0 group-hover/cat:opacity-100 transition-opacity">
                      <div 
                        onClick={(e) => handleEditCategory(cat, e)}
                        className="p-1 text-slate-400 hover:text-indigo-600 hover:bg-white rounded transition-all"
                        title={ARABIC.categories.editCategory}
                      >
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                      </div>
                      <div 
                        onClick={(e) => handleDeleteCategory(cat.id, e)}
                        className="p-1 text-slate-400 hover:text-rose-500 hover:bg-white rounded transition-all"
                        title={ARABIC.categories.deleteCategory}
                      >
                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                      </div>
                    </div>
                  </div>
                  <span className={`bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full text-xs font-semibold shrink-0 group-hover/cat:hidden ${activeCategoryId === cat.id ? 'bg-indigo-100 text-indigo-600' : ''}`}>
                    {cat.product_count}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <main className="flex-1 min-w-0">
          <div className="glass rounded-2xl overflow-hidden shadow-sm">
            {loading ? (
              <div className="flex flex-col items-center justify-center py-20 text-slate-400">
                <svg className="animate-spin w-8 h-8 mb-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="font-medium">{ARABIC.common.loading}</span>
              </div>
            ) : products.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-start border-collapse animate-fade-in">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-200">
                      <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.products.productName}</th>
                      <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.products.sku}</th>
                      <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.products.sellingPrice}</th>
                      <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-center">{ARABIC.products.stockQuantity}</th>
                      <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.products.status}</th>
                      <th className="px-6 py-4 text-end text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.common.actions}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 bg-white/50">
                    {products.map((product) => (
                      <tr key={product.id} className="hover:bg-slate-50/80 transition-colors group">
                        <td className="px-6 py-4">
                          <div className="font-medium text-slate-800">{product.name}</div>
                          <div className="text-xs text-slate-500 mt-0.5">{product.category_name}</div>
                        </td>
                        <td className="px-6 py-4 text-slate-600 font-mono text-sm">{product.sku || <span className="text-slate-400 italic">{ARABIC.common.none}</span>}</td>
                        <td className="px-6 py-4 text-end font-medium text-slate-800">{formatCurrency(product.selling_price)}</td>
                        <td className="px-6 py-4 text-center">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${product.stock_quantity > 10 ? 'bg-emerald-100 text-emerald-800' : product.stock_quantity > 0 ? 'bg-amber-100 text-amber-800' : 'bg-rose-100 text-rose-800'}`}>
                            {product.stock_quantity}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          {product.is_active ? (
                            <span className="flex items-center text-sm text-slate-600"><div className="w-2 h-2 rounded-full bg-emerald-500 ms-2"></div>{ARABIC.products.active}</span>
                          ) : (
                            <span className="flex items-center text-sm text-slate-400"><div className="w-2 h-2 rounded-full bg-slate-300 ms-2"></div>{ARABIC.products.inactive}</span>
                          )}
                        </td>
                        <td className="px-6 py-4 text-end opacity-0 group-hover:opacity-100 transition-opacity">
                          <div className="flex justify-end gap-1">
                            <button
                              onClick={() => handleEditProduct(product)}
                              className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                              title={ARABIC.products.editProduct}
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                            </button>
                            <button
                              onClick={() => handleDelete(product.id)}
                              className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                              title={ARABIC.products.deleteProduct}
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-24 text-slate-400 animate-fade-in">
                <svg className="w-16 h-16 mb-4 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                <div className="text-lg font-medium text-slate-600 mb-1">{ARABIC.products.noProducts}</div>
                <p className="text-sm">{ARABIC.products.addProductStart}</p>
              </div>
            )}
          </div>
        </main>
      </div>

      <ProductModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        product={editingProduct}
        categories={categories}
        onSubmit={handleSaveProduct}
      />

      <CategoryModal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        category={editingCategory}
        onSubmit={handleSaveCategory}
      />
    </div>
  );
}