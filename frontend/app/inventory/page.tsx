"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatDateTime } from "@/lib/utils/format";
import ProductSelector from "@/components/inventory/ProductSelector";

interface InventoryLog {
  id: string;
  product_id: string;
  delta: number;
  reason: string;
  reference_id: string | null;
  balance_after: number;
  created_at: string;
}

interface Product {
  id: string;
  name: string;
  sku: string | null;
  stock_quantity: number;
  is_active: boolean;
}

export default function InventoryPage() {
  const [logs, setLogs] = useState<InventoryLog[]>([]);
  const [lowStockProducts, setLowStockProducts] = useState<Product[]>([]);
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Restock form state
  const [restockProductId, setRestockProductId] = useState("");
  const [restockQuantity, setRestockQuantity] = useState("");
  const [restockLoading, setRestockLoading] = useState(false);

  // Adjustment form state
  const [adjustProductId, setAdjustProductId] = useState("");
  const [adjustmentValue, setAdjustmentValue] = useState("");
  const [adjustReason, setAdjustReason] = useState("");
  const [adjustLoading, setAdjustLoading] = useState(false);

  useEffect(() => {
    fetchLowStockProducts();
  }, []);

  const fetchLowStockProducts = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/inventory/low-stock?threshold=10");
      if (!response.ok) throw new Error("Failed to fetch low stock products");

      const data = await response.json();
      setLowStockProducts(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchInventoryLog = async (productId: string) => {
    try {
      setLoading(true);
      setSelectedProduct(productId);

      const response = await fetch(`/api/inventory/log/${productId}`);
      if (!response.ok) throw new Error("Failed to fetch inventory log");

      const data = await response.json();
      setLogs(data.items);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRestock = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!restockProductId || !restockQuantity) {
      setError("Product ID and quantity are required");
      return;
    }

    try {
      setRestockLoading(true);
      setError("");

      const response = await fetch("/api/inventory/restock", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: restockProductId,
          quantity: parseInt(restockQuantity),
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail?.error?.message || "Restock failed");
      }

      // Refresh data
      setRestockProductId("");
      setRestockQuantity("");
      await fetchLowStockProducts();

      if (selectedProduct) {
        await fetchInventoryLog(selectedProduct);
      }

      alert("Restock successful!");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setRestockLoading(false);
    }
  };

  const handleAdjust = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!adjustProductId || !adjustmentValue || !adjustReason) {
      setError("All fields are required");
      return;
    }

    try {
      setAdjustLoading(true);
      setError("");

      const response = await fetch("/api/inventory/adjust", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          product_id: adjustProductId,
          adjustment: parseInt(adjustmentValue),
          reason: adjustReason,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail?.error?.message || "Adjustment failed");
      }

      // Refresh data
      setAdjustProductId("");
      setAdjustmentValue("");
      setAdjustReason("");
      await fetchLowStockProducts();

      if (selectedProduct) {
        await fetchInventoryLog(selectedProduct);
      }

      alert("Adjustment successful!");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setAdjustLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDelta = (delta: number) => {
    const prefix = delta >= 0 ? "+" : "";
    const colorClass = delta > 0 ? "text-emerald-600" : delta < 0 ? "text-rose-600" : "text-slate-600";
    return <span className={colorClass}>{prefix}{delta}</span>;
  };

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex justify-between items-end mb-2">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.inventory.title}</h1>
          <p className="text-slate-500 mt-1">{ARABIC.inventory.subtitle}</p>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl mb-4 border border-rose-200 animate-slide-up flex items-center shadow-sm">
          <svg className="w-5 h-5 me-3 text-rose-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Low Stock Products */}
        <div className="glass p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute top-0 start-0 -mt-10 -ms-10 w-32 h-32 bg-amber-100/40 rounded-full blur-3xl pointer-events-none"></div>
          
          <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
            <svg className="w-5 h-5 me-2 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            {ARABIC.inventory.lowStockAlerts}
          </h2>

          {loading && !selectedProduct ? (
            <div className="flex justify-center py-8">
              <svg className="animate-spin w-8 h-8 text-amber-500/50" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          ) : lowStockProducts.length === 0 ? (
            <div className="text-center py-10 text-slate-400">
              <div className="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
              </div>
              <p className="font-medium">{ARABIC.inventory.allStockHealthy}</p>
            </div>
          ) : (
            <div className="space-y-3">
              {lowStockProducts.map((product) => (
                <div
                  key={product.id}
                  className={`group border border-transparent rounded-xl p-4 cursor-pointer transition-all ${selectedProduct === product.id ? 'bg-amber-50 border-amber-200 shadow-sm' : 'bg-slate-50/50 hover:bg-slate-50 hover:border-slate-200'}`}
                  onClick={() => fetchInventoryLog(product.id)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className={`font-semibold ${selectedProduct === product.id ? 'text-amber-900' : 'text-slate-800 group-hover:text-amber-700'}`}>{product.name}</div>
                      <div className="text-xs text-slate-500 mt-1 font-mono">{product.sku || ARABIC.products.sku || 'بدون رمز'}</div>
                    </div>
                    <div className="text-start">
                      <div className={`inline-flex items-center justify-center px-3 py-1 rounded-full text-sm font-bold ${product.stock_quantity === 0 ? "bg-rose-100 text-rose-700" : "bg-amber-100 text-amber-700"}`}>
                        {product.stock_quantity} {ARABIC.inventory.left || 'متبقي'}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Inventory Log */}
        <div className="glass p-6 rounded-2xl">
          <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center border-b border-slate-100 pb-3">
            <svg className="w-5 h-5 me-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
            {selectedProduct ? ARABIC.inventory.inventoryLog : ARABIC.inventory.selectProduct}
          </h2>

          {!selectedProduct ? (
            <div className="text-center py-12 text-slate-400">
              <svg className="w-12 h-12 text-slate-200 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122"></path></svg>
              <p>{ARABIC.inventory.clickProductToView || 'انقر على منتج لعرض سجل المخزون'}</p>
            </div>
          ) : loading ? (
            <div className="flex justify-center py-8">
              <svg className="animate-spin w-8 h-8 text-indigo-500/50" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8 text-slate-400">{ARABIC.inventory.noLogEntries || 'لا توجد سجلات'}</div>
          ) : (
            <div className="space-y-4 max-h-[400px] overflow-y-auto pe-2">
              {logs.map((log) => (
                <div key={log.id} className="relative ps-6 pb-4 border-s-2 border-indigo-100 last:border-s-0 last:pb-0 group">
                  <div className="absolute w-3 h-3 bg-indigo-500 rounded-full -start-[7px] top-1.5 ring-4 ring-white group-hover:scale-125 transition-transform"></div>
                  <div className="bg-slate-50/50 p-3 rounded-xl hover:bg-slate-50 transition-colors">
                    <div className="flex justify-between items-start mb-1">
                      <div className="font-semibold text-lg">{formatDelta(log.delta)}</div>
                      <div className="text-xs text-slate-400 font-medium bg-white px-2 py-1 rounded-md shadow-sm">{formatDateTime(log.created_at)}</div>
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <div className="text-slate-600">{log.reason}</div>
                      <div className="font-semibold text-slate-700 bg-slate-200/50 px-2 py-0.5 rounded">{ARABIC.inventory.balance || 'الرصيد'}: {log.balance_after}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-10">
        {/* Restock Form */}
        <div className="glass p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute bottom-0 start-0 -mb-10 -ms-10 w-40 h-40 bg-blue-100/50 rounded-full blur-3xl pointer-events-none"></div>
          <h2 className="text-lg font-semibold text-slate-800 mb-5 flex items-center">
            <span className="w-8 h-8 rounded-lg bg-blue-100 text-blue-600 flex items-center justify-center me-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
            </span>
            {ARABIC.inventory.supplyRestock}
          </h2>
          <form onSubmit={handleRestock} className="space-y-4 relative z-10">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{ARABIC.inventory.selectProduct}</label>
                <ProductSelector
                  value={restockProductId}
                  onChange={setRestockProductId}
                  placeholder={ARABIC.inventory.selectProduct || 'اختر المنتج'}
                />
              </div>
              <div className="col-span-1">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{ARABIC.inventory.quantity || 'الكمية'}</label>
                <input
                  type="number"
                  min="1"
                  value={restockQuantity}
                  onChange={(e) => setRestockQuantity(e.target.value)}
                  className="w-full bg-white border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all p-3 shadow-sm"
                  placeholder="0"
                  required
                />
              </div>
              <div className="col-span-1 flex items-end">
                <button
                  type="submit"
                  disabled={restockLoading}
                  className="w-full h-[46px] px-4 py-2 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 disabled:opacity-50 transition-all shadow-sm shadow-blue-200"
                >
                  {restockLoading ? ARABIC.common.loading : ARABIC.inventory.submitRestock || 'إرسال إعادة التخزين'}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Adjustment Form */}
        <div className="glass p-6 rounded-2xl relative overflow-hidden">
          <div className="absolute bottom-0 start-0 -mb-10 -ms-10 w-40 h-40 bg-orange-100/50 rounded-full blur-3xl pointer-events-none"></div>
          <h2 className="text-lg font-semibold text-slate-800 mb-5 flex items-center">
            <span className="w-8 h-8 rounded-lg bg-orange-100 text-orange-600 flex items-center justify-center me-3">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
            </span>
            {ARABIC.inventory.manualAdjustment}
          </h2>
          <form onSubmit={handleAdjust} className="space-y-4 relative z-10">
            <div className="grid grid-cols-2 gap-4">
              <div className="col-span-2">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{ARABIC.inventory.selectProduct}</label>
                <ProductSelector
                  value={adjustProductId}
                  onChange={setAdjustProductId}
                  placeholder={ARABIC.inventory.selectProduct || 'اختر المنتج'}
                />
              </div>
              <div className="col-span-1">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{ARABIC.inventory.adjustment || 'التعديل'} (±)</label>
                <input
                  type="number"
                  value={adjustmentValue}
                  onChange={(e) => setAdjustmentValue(e.target.value)}
                  className="w-full bg-white border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all p-3 shadow-sm"
                  placeholder="-5 أو +5"
                  required
                />
              </div>
              <div className="col-span-1">
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{ARABIC.inventory.reason || 'السبب'}</label>
                <input
                  type="text"
                  value={adjustReason}
                  onChange={(e) => setAdjustReason(e.target.value)}
                  className="w-full bg-white border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-orange-500/20 focus:border-orange-500 transition-all p-3 shadow-sm"
                  placeholder={ARABIC.inventory.enterReason || 'أدخل السبب'}
                  required
                />
              </div>
              <div className="col-span-2 mt-2">
                <button
                  type="submit"
                  disabled={adjustLoading}
                  className="w-full px-4 py-2.5 bg-orange-500 text-white font-medium rounded-xl hover:bg-orange-600 disabled:opacity-50 transition-all shadow-sm shadow-orange-200"
                >
                  {adjustLoading ? ARABIC.common.loading : ARABIC.inventory.confirmAdjustment || 'تأكيد التعديل'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}