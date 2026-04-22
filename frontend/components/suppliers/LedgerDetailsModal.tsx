import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import { getPurchase, PurchaseWithItems } from "@/lib/api/purchases";

interface LedgerDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  entry: {
    id: string;
    type: string;
    amount: number;
    created_at: string;
    note?: string;
    reference_id?: string;
  } | null;
}

export default function LedgerDetailsModal({ isOpen, onClose, entry }: LedgerDetailsModalProps) {
  const [purchase, setPurchase] = useState<PurchaseWithItems | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen && entry?.reference_id && (entry.type === 'PURCHASE' || entry.type === 'RETURN')) {
      fetchPurchaseDetails(entry.reference_id);
    } else {
      setPurchase(null);
      setError("");
    }
  }, [isOpen, entry]);

  const fetchPurchaseDetails = async (id: string) => {
    try {
      setLoading(true);
      setError("");
      const data = await getPurchase(id);
      setPurchase(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !entry) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-[60] animate-fade-in text-start">
      <div className="bg-white rounded-2xl w-full max-w-2xl overflow-hidden shadow-xl animate-scale-up flex flex-col max-h-[90vh]">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-xl font-bold text-slate-800">تفاصيل {ARABIC.suppliers.types[entry.type as keyof typeof ARABIC.suppliers.types] || entry.type}</h2>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-6 bg-slate-50 p-4 rounded-2xl border border-slate-100">
            <div>
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">التاريخ</div>
              <div className="text-sm font-bold text-slate-700">{formatDate(entry.created_at)}</div>
              <div className="text-[10px] text-slate-400">{new Date(entry.created_at).toLocaleTimeString('ar-SA')}</div>
            </div>
            <div className="text-end">
              <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">المبلغ</div>
              <div className={`text-sm font-bold ${entry.type === 'PAYMENT' ? 'text-emerald-600' : 'text-slate-800'}`}>
                {formatCurrency(entry.amount)}
              </div>
            </div>
          </div>

          {/* Type Specific Content */}
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12 text-slate-400 italic">
              <svg className="animate-spin w-8 h-8 mb-3 text-blue-500" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              جاري تحميل التفاصيل...
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-50 text-rose-600 rounded-xl text-sm border border-rose-100">{error}</div>
          ) : purchase ? (
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
                المنتجات
              </h3>
              <div className="border border-slate-100 rounded-2xl overflow-hidden">
                <table className="w-full text-sm">
                  <thead className="bg-slate-50">
                    <tr className="text-slate-500 font-bold uppercase text-[10px]">
                      <th className="px-4 py-3 text-start">المنتج</th>
                      <th className="px-4 py-3 text-center">الكمية</th>
                      <th className="px-4 py-3 text-end">سعر الوحدة</th>
                      <th className="px-4 py-3 text-end">الإجمالي</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {purchase.items.map((item, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                        <td className="px-4 py-3">
                          <div className="font-bold text-slate-700">{item.product_name || "منتج غير معروف"}</div>
                          <div className="text-[10px] text-slate-400 font-mono">{item.product_sku}</div>
                        </td>
                        <td className="px-4 py-3 text-center font-bold text-slate-600">{item.quantity}</td>
                        <td className="px-4 py-3 text-end text-slate-500 font-mono">{formatCurrency(item.unit_cost)}</td>
                        <td className="px-4 py-3 text-end font-bold text-slate-700 font-mono">{formatCurrency(item.total_cost)}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-slate-50/80 font-bold">
                    <tr>
                      <td colSpan={3} className="px-4 py-3 text-end text-slate-500">الإجمالي الكلي:</td>
                      <td className="px-4 py-3 text-end text-blue-600 font-mono">{formatCurrency(purchase.total_amount)}</td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          ) : entry.type === 'PAYMENT' ? (
            <div className="bg-emerald-50/50 p-6 rounded-2xl border border-emerald-100 border-dashed flex flex-col items-center text-center">
              <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mb-3">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
              </div>
              <h3 className="font-bold text-emerald-800 mb-1">دفعة مالية</h3>
              <p className="text-sm text-emerald-600">{entry.note || "لا توجد ملاحظات لهذه الدفعة"}</p>
            </div>
          ) : null}

          {entry.note && entry.type !== 'PAYMENT' && (
            <div className="space-y-2">
              <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider">ملاحظات</h3>
              <div className="p-4 bg-slate-50 rounded-xl text-slate-600 text-sm border border-slate-100 italic">
                "{entry.note}"
              </div>
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-slate-100 bg-slate-50/50 flex justify-end">
          <button
            onClick={onClose}
            className="px-6 py-2.5 bg-slate-800 text-white text-sm font-bold rounded-xl hover:bg-slate-900 transition-all shadow-lg shadow-slate-100"
          >
            {ARABIC.common.close}
          </button>
        </div>
      </div>
    </div>
  );
}
