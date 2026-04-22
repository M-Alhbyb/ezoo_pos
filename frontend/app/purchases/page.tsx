'use client';

import { useEffect, useState } from 'react';
import { getSupplier, Supplier } from '@/lib/api/suppliers';
import { getPurchases, createPurchase, Purchase, getPurchase, PurchaseWithItems } from '@/lib/api/purchases';

export default function PurchasesPage() {
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState('');
  const [items, setItems] = useState([{ product_id: '', quantity: 1, unit_cost: 0 }]);
  const [productList, setProductList] = useState<{ id: string; name: string }[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [purchasesData, suppliersData] = await Promise.all([
        getPurchases(),
        fetch('/api/suppliers').then(r => r.json()).then(d => d.suppliers || []),
      ]);
      setPurchases(purchasesData);
      setSuppliers(suppliersData);

      const productsData = await fetch('/api/products').then(r => r.json());
      setProductList(productsData.items || []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await createPurchase({
        supplier_id: selectedSupplier,
        items: items.filter(i => i.product_id && i.quantity > 0),
      });
      setShowForm(false);
      setSelectedSupplier('');
      setItems([{ product_id: '', quantity: 1, unit_cost: 0 }]);
      loadData();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to create purchase');
    }
  }

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Purchases</h1>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          {showForm ? 'Cancel' : 'New Purchase'}
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 mb-4 rounded">
          {error}
        </div>
      )}

      {showForm && (
        <form onSubmit={handleSubmit} className="bg-gray-50 p-4 mb-6 rounded">
          <div className="mb-4">
            <label className="block text-sm font-bold mb-2">Supplier</label>
            <select
              value={selectedSupplier}
              onChange={(e) => setSelectedSupplier(e.target.value)}
              className="w-full p-2 border rounded"
              required
            >
              <option value="">Select supplier</option>
              {suppliers.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
          <div className="mb-4">
            <label className="block text-sm font-bold mb-2">Items</label>
            {items.map((item, idx) => (
              <div key={idx} className="flex gap-2 mb-2">
                <select
                  value={item.product_id}
                  onChange={(e) => {
                    const newItems = [...items];
                    newItems[idx].product_id = e.target.value;
                    setItems(newItems);
                  }}
                  className="flex-1 p-2 border rounded"
                >
                  <option value="">Select product</option>
                  {productList.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
                <input
                  type="number"
                  placeholder="Qty"
                  value={item.quantity}
                  onChange={(e) => {
                    const newItems = [...items];
                    newItems[idx].quantity = parseInt(e.target.value) || 0;
                    setItems(newItems);
                  }}
                  className="w-20 p-2 border rounded"
                  min="1"
                />
                <input
                  type="number"
                  placeholder="Unit Cost"
                  value={item.unit_cost}
                  onChange={(e) => {
                    const newItems = [...items];
                    newItems[idx].unit_cost = parseFloat(e.target.value) || 0;
                    setItems(newItems);
                  }}
                  className="w-32 p-2 border rounded"
                  step="0.01"
                />
                <button
                  type="button"
                  onClick={() => setItems(items.filter((_, i) => i !== idx))}
                  className="text-red-600"
                >
                  Remove
                </button>
              </div>
            ))}
            <button
              type="button"
              onClick={() => setItems([...items, { product_id: '', quantity: 1, unit_cost: 0 }])}
              className="text-blue-600 text-sm"
            >
              + Add Item
            </button>
          </div>
          <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
            Create Purchase
          </button>
        </form>
      )}

      <table className="w-full bg-white shadow rounded">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-3 text-left">Date</th>
            <th className="p-3 text-left">Supplier</th>
            <th className="p-3 text-right">Total</th>
            <th className="p-3 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          {purchases.map((purchase) => (
            <tr key={purchase.id} className="border-t">
              <td className="p-3">{new Date(purchase.created_at).toLocaleDateString()}</td>
              <td className="p-3">{purchase.supplier_id}</td>
              <td className="p-3 text-right font-mono">
                {Number(purchase.total_amount).toFixed(2)}
              </td>
              <td className="p-3">{purchase.id.substring(0, 8)}</td>
            </tr>
          ))}
          {purchases.length === 0 && (
            <tr>
              <td colSpan={4} className="p-8 text-center text-gray-500">
                No purchases yet
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}