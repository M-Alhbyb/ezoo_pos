import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";
import NumberInput from "@/components/shared/NumberInput";

interface Product {
  id: string;
  name: string;
  base_price: number;
  selling_price: number;
}

interface PurchaseItem {
  product_id: string;
  quantity: number;
  unit_cost: number;
  selling_price: number;
}

interface PurchaseModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { items: PurchaseItem[] }) => Promise<void>;
  loading?: boolean;
}

export default function PurchaseModal({ isOpen, onClose, onSubmit, loading: externalLoading }: PurchaseModalProps) {
  const [items, setItems] = useState<PurchaseItem[]>([{ product_id: '', quantity: 1, unit_cost: 0, selling_price: 0 }]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      setItems([{ product_id: '', quantity: 1, unit_cost: 0, selling_price: 0 }]);
      setError("");
      fetchProducts();
    }
  }, [isOpen]);

  const fetchProducts = async () => {
    try {
      const res = await fetch('/api/products');
      if (!res.ok) throw new Error('Failed to fetch products');
      const data = await res.json();
      setProducts(data.items || []);
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const validItems = items.filter(i => i.product_id && i.quantity > 0);
    if (validItems.length === 0) {
      setError("يرجى إضافة منتج واحد على الأقل");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await onSubmit({ items: validItems });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addItem = () => {
    setItems([...items, { product_id: '', quantity: 1, unit_cost: 0, selling_price: 0 }]);
  };

  const removeItem = (index: number) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const handleProductSelect = (index: number, productId: string) => {
    const product = products.find(p => p.id === productId);
    const newItems = [...items];
    newItems[index] = {
      ...newItems[index],
      product_id: productId,
      unit_cost: product ? product.base_price : 0,
      selling_price: product ? product.selling_price : 0
    };
    setItems(newItems);
  };

  const updateItem = (index: number, field: keyof PurchaseItem, value: any) => {
    const newItems = [...items];
    (newItems[index] as any)[field] = value;
    setItems(newItems);
  };

  const total = items.reduce((sum, item) => sum + (item.quantity * item.unit_cost), 0);
  const isLoading = loading || externalLoading;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in text-start">
      <div className="bg-white rounded-2xl w-full max-w-4xl overflow-hidden shadow-xl animate-scale-up flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-xl font-semibold text-slate-800">فاتورة شراء جديدة</h2>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 overflow-y-auto flex-1">
          {error && (
            <div className="mb-6 p-3 bg-rose-50 text-rose-700 rounded-xl text-sm border border-rose-200 flex items-center">
              <svg className="w-4 h-4 me-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
              {error}
            </div>
          )}

          <div className="space-y-4">
            <div className="hidden md:grid grid-cols-12 gap-3 px-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
              <div className="col-span-5">المنتج</div>
              <div className="col-span-2">الكمية</div>
              <div className="col-span-2">التكلفة</div>
              <div className="col-span-2">سعر البيع</div>
              <div className="col-span-1"></div>
            </div>

            {items.map((item, index) => (
              <div key={index} className="grid grid-cols-1 md:grid-cols-12 gap-3 p-3 bg-slate-50 rounded-xl border border-slate-100 relative group animate-fade-in">
                <div className="md:col-span-5">
                  <label className="block md:hidden text-xs font-bold text-slate-500 mb-1">المنتج</label>
                  <select
                    required
                    value={item.product_id}
                    onChange={(e) => handleProductSelect(index, e.target.value)}
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all text-sm"
                  >
                    <option value="">اختر المنتج...</option>
                    {products.map(p => (
                      <option key={p.id} value={p.id}>{p.name}</option>
                    ))}
                  </select>
                </div>
                <div className="md:col-span-2">
                  <label className="block md:hidden text-xs font-bold text-slate-500 mb-1">الكمية</label>
                  <input
                    type="number"
                    required
                    min="1"
                    value={item.quantity}
                    onChange={(e) => updateItem(index, 'quantity', parseInt(e.target.value) || 0)}
                    className="w-full px-3 py-2 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all text-sm text-center"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block md:hidden text-xs font-bold text-slate-500 mb-1">سعر التكلفة</label>
                  <NumberInput
                    value={item.unit_cost}
                    onChange={(val) => updateItem(index, 'unit_cost', val)}
                    className="bg-white"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block md:hidden text-xs font-bold text-slate-500 mb-1">سعر البيع</label>
                  <NumberInput
                    value={item.selling_price}
                    onChange={(val) => updateItem(index, 'selling_price', val)}
                    className="bg-emerald-50 border-emerald-100 text-emerald-700 font-bold focus:ring-emerald-500"
                  />
                </div>
                <div className="md:col-span-1 flex items-end justify-center">
                  <button
                    type="button"
                    onClick={() => removeItem(index)}
                    className="p-2 text-rose-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                  </button>
                </div>
              </div>
            ))}

            <button
              type="button"
              onClick={addItem}
              className="w-full py-3 border-2 border-dashed border-slate-200 rounded-xl text-slate-400 hover:text-blue-500 hover:border-blue-200 hover:bg-blue-50 transition-all flex items-center justify-center gap-2 font-medium"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
              إضافة منتج آخر
            </button>
          </div>
        </form>

        <div className="px-6 py-4 border-t border-slate-100 bg-slate-50/50 flex justify-between items-center">
          <div className="text-start">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">الإجمالي الكلي</div>
            <div className="text-xl font-bold text-slate-800">{formatCurrency(total)}</div>
          </div>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              {ARABIC.common.cancel}
            </button>
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="px-8 py-2.5 bg-blue-600 text-white text-sm font-bold rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-100 flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isLoading ? ARABIC.common.saving : 'حفظ الفاتورة'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
