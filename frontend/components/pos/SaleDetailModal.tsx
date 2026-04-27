import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import { getSale, reverseSale, SaleDetail } from "@/lib/api/sales";
import NumberInput from "@/components/shared/NumberInput";

interface SaleDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  saleId: string | null;
  onSaleReversed?: () => void;
  initialReturnMode?: boolean;
}

export default function SaleDetailModal({ 
  isOpen, 
  onClose, 
  saleId, 
  onSaleReversed,
  initialReturnMode = false 
}: SaleDetailModalProps) {
  const [sale, setSale] = useState<SaleDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [reversing, setReversing] = useState(false);
  
  // Return mode state
  const [isReturnMode, setIsReturnMode] = useState(initialReturnMode);
  const [returnQtys, setReturnQtys] = useState<Record<string, number>>({});
  const [reason, setReason] = useState("Manual Reversal");

  useEffect(() => {
    if (isOpen && saleId) {
      loadSale();
      setIsReturnMode(initialReturnMode);
    } else {
      setSale(null);
      setError("");
      setIsReturnMode(false);
      setReturnQtys({});
    }
  }, [isOpen, saleId]);

  async function loadSale() {
    try {
      setLoading(true);
      const data = await getSale(saleId!);
      setSale(data);
      
      // Initialize return quantities with remaining quantities
      const initialQtys: Record<string, number> = {};
      data.items.forEach(item => {
        initialQtys[item.product_id] = 0; // Start at 0 like supplier return
      });
      setReturnQtys(initialQtys);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleReverse() {
    const itemsToReverse = Object.entries(returnQtys)
      .filter(([_, qty]) => qty > 0)
      .map(([id, qty]) => ({ product_id: id, quantity: qty }));

    if (itemsToReverse.length === 0) {
      setError("يرجى تحديد كمية واحدة على الأقل للإرجاع");
      return;
    }

    const confirmMsg = isReturnMode 
      ? `هل أنت متأكد من إرجاع الكميات المحددة؟`
      : (ARABIC.pos.confirmReverse || "هل أنت متأكد من إلغاء هذه العملية وإرجاع المنتجات للمخزن؟");

    if (!confirm(confirmMsg)) return;
    
    try {
      setReversing(true);
      setError("");
      await reverseSale(saleId!, reason, itemsToReverse);
      if (onSaleReversed) onSaleReversed();
      onClose();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setReversing(false);
    }
  }

  const handlePrint = () => {
    window.print();
  };

  const updateReturnQty = (productId: string, val: number, max: number) => {
    const qty = Math.max(0, Math.min(max, val));
    setReturnQtys(prev => ({ ...prev, [productId]: qty }));
  };

  // Calculate projected return total
  const calculateReturnTotal = () => {
    if (!sale) return 0;
    let subtotal = 0;
    sale.items.forEach(item => {
      const qty = returnQtys[item.product_id] || 0;
      subtotal += qty * item.unit_price;
    });
    
    // Add proportional VAT if applicable
    if (sale.grand_total > 0 && sale.subtotal > 0) {
        const ratio = sale.grand_total / sale.subtotal;
        return subtotal * ratio;
    }
    return subtotal;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in text-start no-print">
      <div className="bg-white rounded-2xl w-full max-w-2xl overflow-hidden shadow-xl animate-scale-up max-h-[90vh] flex flex-col transition-all">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-xl font-semibold text-slate-800">
            {isReturnMode ? "إرجاع منتجات للعميل" : (ARABIC.pos.saleDetail || "تفاصيل العملية")}
          </h2>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6" id="printable-sale">
          {error && (
            <div className="p-4 bg-rose-50 text-rose-700 rounded-xl border border-rose-200 text-sm flex items-center">
              <svg className="w-4 h-4 me-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
              {error}
            </div>
          )}

          {loading && !sale ? (
            <div className="py-20 flex justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          ) : sale ? (
            <>
              {/* Info Header */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 flex justify-between items-center">
                <div>
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{ARABIC.pos.orderId || "رقم العملية"}</div>
                  <div className="text-blue-600 font-mono font-bold text-lg">#{sale.id.substring(0, 8).toUpperCase()}</div>
                </div>
                <div className="text-end">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{ARABIC.customers.date}</div>
                  <div className="text-slate-800 font-medium">{formatDate(sale.created_at)}</div>
                  <div className="text-xs text-slate-500">{new Date(sale.created_at).toLocaleTimeString('ar-SA')}</div>
                </div>
              </div>

              {/* Items Section */}
              <div className="space-y-3">
                <h3 className="text-sm font-bold text-slate-700">
                    {isReturnMode ? "المنتجات المباعة" : "قائمة المنتجات"}
                </h3>
                
                {isReturnMode ? (
                  // Return Mode: Card Layout (matches supplier)
                  <div className="space-y-3">
                    {sale.items.map((item, idx) => {
                      const remaining = item.remaining_quantity ?? item.quantity;
                      if (remaining <= 0) return null; // Don't show fully reversed items in return list
                      
                      return (
                        <div key={idx} className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl shadow-sm hover:border-rose-200 transition-colors group">
                          <div className="flex-1">
                            <div className="font-bold text-slate-800">{item.product_name}</div>
                            <div className="flex gap-4 mt-1">
                              <div className="text-xs text-slate-400">الكمية الأصلية: {item.quantity}</div>
                              <div className="text-xs font-bold text-emerald-600">المتوفر للإرجاع: {remaining}</div>
                            </div>
                            <div className="text-[10px] text-slate-500 mt-1 font-mono">{formatCurrency(item.unit_price)} / وحدة</div>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-end hidden sm:block">
                                <div className="text-[10px] text-slate-400 uppercase">الإجمالي</div>
                                <div className="font-bold text-rose-600 font-mono">
                                    {formatCurrency((returnQtys[item.product_id] || 0) * item.unit_price)}
                                </div>
                            </div>
                            <div className="w-24">
                              <NumberInput
                                value={returnQtys[item.product_id] || 0}
                                onChange={(val) => updateReturnQty(item.product_id, val, remaining)}
                                className="px-2 py-1 text-center font-bold text-rose-600 border-rose-100 bg-rose-50/30"
                              />
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  // View Mode: Table Layout (classic)
                  <div className="border border-slate-100 rounded-xl overflow-hidden shadow-sm">
                    <table className="w-full text-sm">
                      <thead className="bg-slate-50">
                        <tr>
                          <th className="px-4 py-3 text-start font-semibold text-slate-600">{ARABIC.pos.product}</th>
                          <th className="px-4 py-3 text-center font-semibold text-slate-600">{ARABIC.pos.qty}</th>
                          <th className="px-4 py-3 text-end font-semibold text-slate-600">{ARABIC.pos.price}</th>
                          <th className="px-4 py-3 text-end font-semibold text-slate-600">{ARABIC.pos.total}</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {sale.items.map((item, idx) => (
                          <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                            <td className="px-4 py-3 text-slate-800 font-medium">{item.product_name}</td>
                            <td className="px-4 py-3 text-center text-slate-600">{item.quantity}</td>
                            <td className="px-4 py-3 text-end text-slate-600 font-mono">{formatCurrency(item.unit_price)}</td>
                            <td className="px-4 py-3 text-end text-slate-800 font-bold font-mono">{formatCurrency(item.line_total)}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Totals Section */}
              <div className="space-y-4">
                {!isReturnMode ? (
                  <div className="space-y-2 pt-4 border-t border-slate-100">
                    <div className="flex justify-between text-sm">
                      <span className="text-slate-500">{ARABIC.pos.subtotal}</span>
                      <span className="text-slate-800 font-medium font-mono">{formatCurrency(sale.subtotal)}</span>
                    </div>
                    {sale.fees_total > 0 && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500">{ARABIC.pos.fees}</span>
                        <span className="text-slate-800 font-medium font-mono">{formatCurrency(sale.fees_total)}</span>
                      </div>
                    )}
                    {sale.vat_total > 0 && (
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-500">{ARABIC.pos.vat}</span>
                        <span className="text-slate-800 font-medium font-mono">{formatCurrency(sale.vat_total)}</span>
                      </div>
                    )}
                    <div className="flex justify-between text-lg font-bold pt-2 border-t border-slate-200">
                      <span className="text-slate-800">{ARABIC.pos.total}</span>
                      <span className="text-blue-600 font-mono">{formatCurrency(sale.grand_total)}</span>
                    </div>
                  </div>
                ) : (
                  <div className="p-5 bg-rose-50 rounded-2xl border border-rose-100 space-y-4 shadow-inner">
                    <div className="flex justify-between items-center text-rose-800">
                        <span className="font-bold">إجمالي المبلغ المسترد المتوقع:</span>
                        <span className="text-2xl font-black font-mono">{formatCurrency(calculateReturnTotal())}</span>
                    </div>
                    <div>
                        <label className="block text-[10px] font-bold text-rose-400 uppercase tracking-widest mb-1.5">سبب الإرجاع</label>
                        <input 
                            type="text"
                            value={reason}
                            onChange={(e) => setReason(e.target.value)}
                            className="w-full bg-white border border-rose-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:ring-4 focus:ring-rose-500/10 focus:border-rose-500 transition-all font-medium"
                            placeholder="أدخل سبب الإرجاع..."
                        />
                    </div>
                  </div>
                )}

                {/* Meta Info (Payments/Notes) */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 pt-4 border-t border-slate-100">
                    <div>
                        <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">{ARABIC.pos.payments || "المدفوعات"}</label>
                        <div className="flex flex-wrap gap-2">
                            {sale.payments.map((p, idx) => (
                            <div key={idx} className="px-3 py-1.5 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-bold border border-emerald-100 flex items-center">
                                <span className="me-2">{p.payment_method_name}:</span>
                                <span>{formatCurrency(p.amount)}</span>
                            </div>
                            ))}
                        </div>
                    </div>
                    {sale.note && (
                        <div>
                            <label className="text-xs font-bold text-slate-400 uppercase tracking-widest block mb-2">{ARABIC.customers.notes}</label>
                            <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-100 italic">"{sale.note}"</p>
                        </div>
                    )}
                </div>
              </div>
            </>
          ) : null}
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-slate-100 bg-slate-50/50 flex justify-between gap-3">
          <div className="flex gap-2">
             {!isReturnMode && (
               <button
                onClick={handlePrint}
                disabled={!sale || loading}
                className="px-5 py-2.5 bg-slate-800 text-white text-sm font-bold rounded-xl hover:bg-slate-900 transition-all flex items-center shadow-lg shadow-slate-200 disabled:opacity-50"
              >
                <svg className="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 00-2 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2-2h-2m14 6h.01M5 10H5.01"></path></svg>
                {ARABIC.common.print || "طباعة"}
              </button>
             )}
            
            {sale && !sale.is_reversal && (
              <button
                onClick={isReturnMode ? handleReverse : () => setIsReturnMode(true)}
                disabled={reversing || loading}
                className="px-8 py-2.5 bg-rose-600 text-white text-sm font-bold rounded-xl hover:bg-rose-700 transition-all flex items-center shadow-lg shadow-rose-100 disabled:opacity-50"
              >
                <svg className="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"></path></svg>
                {reversing ? ARABIC.common.saving : (isReturnMode ? "تأكيد الإرجاع" : (ARABIC.pos.returnItems || "إرجاع منتجات"))}
              </button>
            )}

            {isReturnMode && (
                <button
                    onClick={() => setIsReturnMode(false)}
                    className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
                >
                    {ARABIC.common.cancel}
                </button>
            )}
          </div>
          
          {!isReturnMode && (
            <button
                onClick={onClose}
                className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
                {ARABIC.common.close || "إغلاق"}
            </button>
          )}
        </div>
      </div>

      <style jsx global>{`
        @media print {
          body * {
            visibility: hidden;
          }
          #printable-sale, #printable-sale * {
            visibility: visible;
          }
          #printable-sale {
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            padding: 20px;
          }
          .no-print {
            display: none !important;
          }
        }
      `}</style>
    </div>
  );
}
