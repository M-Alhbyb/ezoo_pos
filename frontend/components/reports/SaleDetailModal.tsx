"use client";

import { useEffect, useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";
import { X, Calendar, CreditCard, Hash, Package, Tag, Receipt, Info, TrendingUp } from "lucide-react";

interface SaleItem {
  product_name: string;
  quantity: number;
  unit_price: number;
  line_total: number;
}

interface SaleFee {
  fee_label: string;
  calculated_amount: number;
}

interface Sale {
  id: string;
  payment_method_name: string;
  items: SaleItem[];
  subtotal: number;
  fees: SaleFee[];
  fees_total: number;
  vat_total: number | null;
  grand_total: number;
  profit: number;
  note: string | null;
  created_at: string;
}

interface SaleDetailModalProps {
  saleId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function SaleDetailModal({ saleId, isOpen, onClose }: SaleDetailModalProps) {
  const [sale, setSale] = useState<Sale | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (isOpen && saleId) {
      fetchSaleDetails(saleId);
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
      setSale(null);
      setError("");
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen, saleId]);

  const fetchSaleDetails = async (id: string) => {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`/api/sales/${id}`);
      if (!response.ok) throw new Error("Failed to fetch sale details");
      const data = await response.json();
      setSale(data);
    } catch (err: any) {
      setError(err.message || "Error");
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen || !mounted) return null;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 sm:p-6 lg:p-8">
      <div 
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-md transition-opacity animate-in fade-in duration-500"
        onClick={onClose}
      />
      
      <div className="relative w-full max-w-2xl bg-white rounded-[2rem] shadow-2xl border border-white/20 overflow-hidden animate-in zoom-in-95 fade-in slide-in-from-bottom-8 duration-500">
        {/* Header */}
        <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-gradient-to-r from-slate-50 to-white">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-100 text-indigo-600 rounded-2xl shadow-sm">
              <Receipt className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-2xl font-black text-slate-800 tracking-tight">
                {ARABIC.reports.transactionDetails}
              </h2>
              <p className="text-slate-500 text-sm font-semibold flex items-center gap-1">
                <Hash className="w-3 h-3" />
                {saleId?.substring(0, 8).toUpperCase()}...
              </p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-3 hover:bg-slate-100 rounded-full transition-all text-slate-400 hover:text-slate-600 active:scale-95"
          >
            <X className="w-6 h-6" />
          </button>
        </div>
        
        <div className="max-h-[70vh] overflow-y-auto custom-scrollbar">
          {loading ? (
            <div className="p-20 flex flex-col items-center justify-center space-y-4">
              <div className="animate-spin h-10 w-10 border-4 border-indigo-600 border-t-transparent rounded-full" />
              <p className="text-slate-500 font-bold animate-pulse">{ARABIC.common.loading || 'جاري التحميل...'}</p>
            </div>
          ) : error ? (
            <div className="p-12 text-center space-y-4">
              <div className="inline-flex p-4 bg-rose-50 text-rose-500 rounded-full">
                <Info className="w-8 h-8" />
              </div>
              <p className="text-rose-600 font-bold text-lg">{error}</p>
            </div>
          ) : sale && (
            <div className="p-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {/* Info Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-center gap-3">
                  <div className="p-2 bg-white rounded-xl shadow-sm text-slate-400">
                    <Calendar className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-[10px] uppercase tracking-wider font-bold text-slate-400">{ARABIC.reports.sales.date}</p>
                    <p className="text-sm font-bold text-slate-700">
                      {new Date(sale.created_at).toLocaleString('ar-EG', { dateStyle: 'medium', timeStyle: 'short' })}
                    </p>
                  </div>
                </div>
                <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-center gap-3">
                  <div className="p-2 bg-white rounded-xl shadow-sm text-slate-400">
                    <CreditCard className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="text-[10px] uppercase tracking-wider font-bold text-slate-400">{ARABIC.reports.paymentMethod}</p>
                    <p className="text-sm font-bold text-slate-700">{sale.payment_method_name}</p>
                  </div>
                </div>
              </div>

              {/* Items Table */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Package className="w-4 h-4 text-emerald-500" />
                  <h3 className="text-sm font-black text-slate-400 uppercase tracking-widest">{ARABIC.pos.items}</h3>
                </div>
                <div className="rounded-2xl border border-slate-100 overflow-hidden">
                  <table className="w-full text-sm text-start" dir="rtl">
                    <thead className="bg-slate-50 text-slate-500 font-bold border-b border-slate-100 text-[11px] uppercase">
                      <tr>
                        <th className="px-4 py-3 text-start">{ARABIC.pos.product}</th>
                        <th className="px-4 py-3 text-center">{ARABIC.pos.quantity}</th>
                        <th className="px-4 py-3 text-end">{ARABIC.pos.total}</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {sale.items.map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-50/50 transition-colors">
                          <td className="px-4 py-3">
                            <p className="font-bold text-slate-700">{item.product_name}</p>
                            <p className="text-[10px] text-slate-400 font-semibold">{formatCurrency(item.unit_price)}</p>
                          </td>
                          <td className="px-4 py-3 text-center font-black text-slate-500">
                            <span className="bg-slate-100 px-2 py-0.5 rounded-lg">{item.quantity}</span>
                          </td>
                          <td className="px-4 py-3 text-end font-bold text-slate-700">{formatCurrency(item.line_total)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Financials Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4">
                <div className="space-y-4">
                  {sale.fees.length > 0 && (
                    <div className="space-y-2">
                       <div className="flex items-center gap-2">
                        <Tag className="w-4 h-4 text-amber-500" />
                        <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{ARABIC.pos.fees}</h3>
                      </div>
                      <div className="space-y-2">
                        {sale.fees.map((fee, idx) => (
                          <div key={idx} className="flex justify-between text-sm">
                            <span className="text-slate-500 font-medium">{fee.fee_label}</span>
                            <span className="text-slate-700 font-bold">{formatCurrency(fee.calculated_amount)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {sale.note && (
                    <div className="p-4 bg-amber-50 rounded-2xl border border-amber-100">
                      <p className="text-[10px] font-black text-amber-600/60 uppercase tracking-widest mb-1">{ARABIC.pos.note}</p>
                      <p className="text-sm font-medium text-amber-800 italic">"{sale.note}"</p>
                    </div>
                  )}
                </div>

                <div className="p-6 rounded-3xl bg-slate-50 border border-slate-100 flex flex-col justify-between space-y-6">
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-slate-500 font-bold">{ARABIC.pos.subtotal}</span>
                      <span className="text-slate-700 font-black tracking-tight">{formatCurrency(sale.subtotal)}</span>
                    </div>
                    {sale.fees_total > 0 && (
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500 font-bold">{ARABIC.pos.fees}</span>
                        <span className="text-slate-700 font-black tracking-tight">{formatCurrency(sale.fees_total)}</span>
                      </div>
                    )}
                    {sale.vat_total !== null && (
                      <div className="flex justify-between items-center text-sm">
                        <span className="text-slate-500 font-bold">{ARABIC.pos.vat}</span>
                        <span className="text-slate-700 font-black tracking-tight">{formatCurrency(sale.vat_total)}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="pt-4 border-t border-slate-200">
                    <div className="flex justify-between items-end mb-4">
                        <span className="text-slate-800 font-black text-lg">{ARABIC.pos.total}</span>
                        <span className="text-3xl font-black text-indigo-600 tracking-tighter">{formatCurrency(sale.grand_total)}</span>
                    </div>
                    <div className="flex items-center gap-2 p-3 bg-emerald-100/50 rounded-2xl border border-emerald-100">
                        <TrendingUp className="w-4 h-4 text-emerald-600" />
                        <span className="text-xs font-bold text-emerald-700">{ARABIC.reports.sales.netProfit}:</span>
                        <span className="text-xs font-black text-emerald-700 ms-auto">{formatCurrency(sale.profit)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Footer */}
        <div className="p-6 text-center bg-white border-t border-slate-50">
          <button
            onClick={onClose}
            className="px-8 py-3 bg-slate-900 text-white font-black rounded-xl hover:bg-slate-800 transition-all shadow-xl shadow-slate-200 active:scale-95"
          >
            {ARABIC.common.close || 'إغلاق'}
          </button>
        </div>
      </div>
    </div>
  );
}
