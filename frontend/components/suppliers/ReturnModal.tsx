import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatDate } from "@/lib/utils/format";
import { getPurchase, PurchaseWithItems } from "@/lib/api/purchases";
import NumberInput from "@/components/shared/NumberInput";

interface ReturnItem {
  product_id: string;
  quantity: number;
}

interface ReturnModalProps {
  isOpen: boolean;
  onClose: () => void;
  purchaseId: string;
  onSubmit: (data: { items: ReturnItem[], note?: string }) => Promise<void>;
  loading?: boolean;
}

export default function ReturnModal({ isOpen, onClose, purchaseId, onSubmit, loading: externalLoading }: ReturnModalProps) {
  const [purchase, setPurchase] = useState<PurchaseWithItems | null>(null);
  const [returnQuantities, setReturnQuantities] = useState<Record<string, number>>({});
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen && purchaseId) {
      fetchPurchase();
      setNote("");
      setError("");
    }
  }, [isOpen, purchaseId]);

  const fetchPurchase = async () => {
    try {
      setLoading(true);
      const data = await getPurchase(purchaseId);
      setPurchase(data);
      const initialQtys: Record<string, number> = {};
      data.items.forEach(item => {
        initialQtys[item.product_id] = 0;
      });
      setReturnQuantities(initialQtys);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const items = Object.entries(returnQuantities)
      .filter(([_, qty]) => qty > 0)
      .map(([productId, qty]) => ({ product_id: productId, quantity: qty }));

    if (items.length === 0) {
      setError("يرجى تحديد كمية واحدة على الأقل للإرجاع");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await onSubmit({ items, note: note || undefined });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const updateQty = (productId: string, qty: number, max: number) => {
    setReturnQuantities({
      ...returnQuantities,
      [productId]: Math.min(Math.max(0, qty), max)
    });
  };

  const isLoading = loading || externalLoading;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in text-start">
      <div className="bg-white rounded-2xl w-full max-w-xl overflow-hidden shadow-xl animate-scale-up flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-xl font-semibold text-slate-800">إرجاع منتجات للمورد</h2>
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

          {loading && !purchase ? (
            <div className="flex justify-center py-10 text-slate-400 italic">جاري تحميل بيانات الفاتورة...</div>
          ) : (
            <div className="space-y-6">
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex justify-between items-center">
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase">رقم الفاتورة</div>
                  <div className="font-mono text-blue-600">#{purchaseId.substring(0, 8)}</div>
                </div>
                <div className="text-end">
                  <div className="text-[10px] font-bold text-slate-400 uppercase">التاريخ</div>
                  <div className="text-slate-600 text-sm">{purchase && formatDate(purchase.created_at)}</div>
                </div>
              </div>

              <div className="space-y-3">
                <h3 className="text-sm font-bold text-slate-700">المنتجات المشتراة</h3>
                {purchase?.items.map((item) => (
                  <div key={item.id} className="flex items-center justify-between p-3 bg-white border border-slate-200 rounded-xl shadow-sm">
                    <div className="flex-1">
                      <div className="font-bold text-slate-800 text-sm">
                        {item.product_name || item.product_id}
                      </div>
                      <div className="text-[10px] text-slate-400 font-mono">
                        {item.product_sku && `SKU: ${item.product_sku}`}
                      </div>
                      <div className="flex gap-4 mt-1">
                        <div className="text-xs text-slate-400">الكمية الأصلية: {item.quantity}</div>
                        <div className={`text-xs font-bold ${item.current_stock === 0 ? 'text-rose-500' : 'text-emerald-600'}`}>
                          المتوفر حالياً: {item.current_stock ?? 0}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="w-24">
                        <NumberInput
                          value={returnQuantities[item.product_id] || 0}
                          onChange={(val) => updateQty(item.product_id, val, item.quantity)}
                          className="px-2 py-1 text-center font-bold text-rose-600"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">{ARABIC.suppliers.note}</label>
                <input
                  type="text"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-rose-500 focus:border-rose-500 transition-all font-medium text-slate-800"
                  placeholder="سبب الإرجاع..."
                />
              </div>
            </div>
          )}
        </form>

        <div className="px-6 py-4 border-t border-slate-100 bg-slate-50/50 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
          >
            {ARABIC.common.cancel}
          </button>
          <button
            onClick={handleSubmit}
            disabled={isLoading || !purchase}
            className="px-8 py-2.5 bg-rose-600 text-white text-sm font-bold rounded-xl hover:bg-rose-700 transition-all shadow-lg shadow-rose-100 flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {isLoading ? ARABIC.common.saving : 'تأكيد الإرجاع'}
          </button>
        </div>
      </div>
    </div>
  );
}
