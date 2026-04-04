"use client";

import { useState, useEffect } from "react";

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
    const color = delta > 0 ? "text-green-600" : delta < 0 ? "text-red-600" : "text-gray-600";
    return <span className={color}>{prefix}{delta}</span>;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Inventory Management</h1>

      {error && (
        <div className="bg-red-100 text-red-700 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Low Stock Products */}
        <div className="border rounded p-4">
          <h2 className="text-xl font-semibold mb-4">Low Stock Products</h2>

          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : lowStockProducts.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No low stock products</div>
          ) : (
            <div className="space-y-2">
              {lowStockProducts.map((product) => (
                <div
                  key={product.id}
                  className="border rounded p-3 hover:bg-gray-50 cursor-pointer"
                  onClick={() => fetchInventoryLog(product.id)}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-medium">{product.name}</div>
                      {product.sku && <div className="text-sm text-gray-500">SKU: {product.sku}</div>}
                    </div>
                    <div className={`text-lg font-bold ${product.stock_quantity === 0 ? "text-red-600" : "text-orange-600"}`}>
                      {product.stock_quantity}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Inventory Log */}
        <div className="border rounded p-4">
          <h2 className="text-xl font-semibold mb-4">
            {selectedProduct ? "Inventory Log" : "Select a Product"}
          </h2>

          {!selectedProduct ? (
            <div className="text-center py-8 text-gray-500">
              Click on a product to view its inventory log
            </div>
          ) : loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : logs.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No inventory log entries</div>
          ) : (
            <div className="space-y-3">
              {logs.map((log) => (
                <div key={log.id} className="border-b pb-3">
                  <div className="flex justify-between items-start">
                    <div>
                      <div className="font-medium">{formatDelta(log.delta)}</div>
                      <div className="text-sm text-gray-600">{log.reason}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-500">{formatDate(log.created_at)}</div>
                      <div className="text-sm font-medium">Balance: {log.balance_after}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Restock Form */}
      <div className="mt-8 border rounded p-4">
        <h2 className="text-xl font-semibold mb-4">Restock Product</h2>
        <form onSubmit={handleRestock} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Product ID</label>
            <input
              type="text"
              value={restockProductId}
              onChange={(e) => setRestockProductId(e.target.value)}
              placeholder="Enter product UUID"
              className="border rounded px-3 py-2 w-full"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Quantity</label>
            <input
              type="number"
              min="1"
              value={restockQuantity}
              onChange={(e) => setRestockQuantity(e.target.value)}
              className="border rounded px-3 py-2 w-full"
              required
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={restockLoading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 w-full"
            >
              {restockLoading ? "Processing..." : "Restock"}
            </button>
          </div>
        </form>
      </div>

      {/* Adjustment Form */}
      <div className="mt-6 border rounded p-4">
        <h2 className="text-xl font-semibold mb-4">Adjust Stock</h2>
        <form onSubmit={handleAdjust} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Product ID</label>
            <input
              type="text"
              value={adjustProductId}
              onChange={(e) => setAdjustProductId(e.target.value)}
              placeholder="Enter product UUID"
              className="border rounded px-3 py-2 w-full"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Adjustment (+/-)</label>
            <input
              type="number"
              value={adjustmentValue}
              onChange={(e) => setAdjustmentValue(e.target.value)}
              className="border rounded px-3 py-2 w-full"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Reason</label>
            <input
              type="text"
              value={adjustReason}
              onChange={(e) => setAdjustReason(e.target.value)}
              className="border rounded px-3 py-2 w-full"
              placeholder="e.g., Damaged items"
              required
            />
          </div>
          <div className="flex items-end">
            <button
              type="submit"
              disabled={adjustLoading}
              className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50 w-full"
            >
              {adjustLoading ? "Processing..." : "Adjust"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}