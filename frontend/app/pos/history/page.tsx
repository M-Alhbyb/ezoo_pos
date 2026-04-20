"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDateTime } from "@/lib/utils/format";
import { ArrowRight, Package, Receipt, AlertTriangle } from "lucide-react";

interface SaleSummary {
  id: string;
  payment_method_name: string;
  total: string;
  created_at: string;
  reversed: boolean;
}

export default function SaleHistoryPage() {
  const [sales, setSales] = useState<SaleSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  useEffect(() => {
    fetchSales();
  }, [page]);

  const fetchSales = async () => {
    try {
      setLoading(true);
      const offset = (page - 1) * pageSize;
      const response = await fetch(`/api/sales?page=${page}&page_size=${pageSize}`);
      
      if (!response.ok) {
        throw new Error("Failed to fetch sales");
      }

      const data = await response.json();
      setSales(data.items);
      setTotal(data.total);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.pos.saleHistory}</h1>
          <p className="text-slate-500 mt-1">{ARABIC.pos.saleHistory || 'عرض جميع المبيعات السابقة'}</p>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl border border-rose-200 flex items-center">
          <AlertTriangle className="w-5 h-5 me-3 text-rose-500" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      <div className="glass p-6 rounded-2xl">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
            <p className="text-slate-500 mt-4">{ARABIC.common.loading}</p>
          </div>
        ) : sales.length === 0 ? (
          <div className="text-center py-20">
            <Receipt className="w-16 h-16 text-slate-200 mx-auto mb-4" />
            <h3 className="text-lg font-bold text-slate-400">{ARABIC.pos.noSales || 'لا توجد مبيعات'}</h3>
            <p className="text-slate-400/60 mt-1">{ARABIC.pos.noSalesDesc || 'لم يتم تسجيل أي مبيعات بعد'}</p>
            <Link 
              href="/pos"
              className="mt-6 inline-flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-xl font-bold hover:bg-primary/90 transition-all"
            >
              {ARABIC.nav.pos}
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-start py-3 px-4 text-sm font-semibold text-slate-600">{ARABIC.pos.saleDetails || 'تفاصيل البيع'}</th>
                    <th className="text-start py-3 px-4 text-sm font-semibold text-slate-600">{ARABIC.pos.paymentMethod || 'طريقة الدفع'}</th>
                    <th className="text-start py-3 px-4 text-sm font-semibold text-slate-600">{ARABIC.pos.total || 'الإجمالي'}</th>
                    <th className="text-start py-3 px-4 text-sm font-semibold text-slate-600">{ARABIC.common.createdAt || 'تاريخ الإنشاء'}</th>
                    <th className="text-end py-3 px-4 text-sm font-semibold text-slate-600">{ARABIC.common.actions || 'الإجراءات'}</th>
                  </tr>
                </thead>
                <tbody>
                  {sales.map((sale) => (
                    <tr key={sale.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-blue-100 rounded-lg">
                            <Receipt className="w-4 h-4 text-blue-600" />
                          </div>
                          <div>
                            <p className="font-medium text-slate-800">{sale.id.slice(0, 8)}...</p>
                            {sale.reversed && (
                              <span className="text-xs text-rose-600 font-medium">({ARABIC.pos.saleCancelled || 'ملغي'})</span>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-slate-600">{sale.payment_method_name}</td>
                      <td className="py-4 px-4">
                        <span className={`font-bold ${sale.reversed ? 'text-slate-400 line-through' : 'text-slate-800'}`}>
                          {formatCurrency(sale.total)}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-slate-500 text-sm">{formatDateTime(sale.created_at)}</td>
                      <td className="py-4 px-4 text-end">
                        <Link
                          href={`/pos/history/${sale.id}`}
                          className="inline-flex items-center gap-1 text-sm font-bold text-primary hover:text-primary/80 transition-colors"
                        >
                          {ARABIC.pos.saleDetails || 'التفاصيل'}
                          <ArrowRight className="w-4 h-4" />
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="flex justify-between items-center mt-6 pt-4 border-t border-slate-200">
                <button
                  onClick={() => setPage(p => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-200 transition-colors"
                >
                  {ARABIC.common.back || 'رجوع'}
                </button>
                <p className="text-sm text-slate-500">
                  {page} / {totalPages}
                </p>
                <button
                  onClick={() => setPage(p => p + 1)}
                  disabled={page >= totalPages}
                  className="px-4 py-2 bg-slate-100 text-slate-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-200 transition-colors"
                >
                  {ARABIC.common.next || 'التالي'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}