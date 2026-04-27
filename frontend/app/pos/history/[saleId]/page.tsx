"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDateTime } from "@/lib/utils/format";
import { ArrowRight, Package, Receipt, AlertTriangle, AlertCircle, Printer } from "lucide-react";
import { printInvoice } from "@/lib/utils/print-utils";

interface SaleDetail {
  id: string;
  payment_method_id: string;
  payment_method_name: string;
  items: Array<{
    product_id: string;
    product_name: string;
    quantity: number;
    unit_price: string;
    line_total: string;
  }>;
  subtotal: string;
  fees: Array<{
    fee_type: string;
    fee_label: string;
    fee_value_type: string;
    fee_value: string;
    calculated_amount: string;
  }>;
  fees_total: string;
  vat_enabled: boolean;
  vat_rate: string | null;
  vat_amount: string | null;
  total: string;
  note: string | null;
  reversed: boolean;
  reversal: {
    id: string;
    reason: string;
    created_at: string;
  } | null;
  created_at: string;
}

export default function SaleDetailPage({ params }: { params: { saleId: string } }) {
  const { saleId } = params;
  const [sale, setSale] = useState<SaleDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchSaleDetail();
  }, [saleId]);

  const fetchSaleDetail = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/sales/${saleId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(ARABIC.pos.saleNotFound || 'لم يتم العثور على البيع');
        }
        throw new Error("Failed to fetch sale details");
      }

      const data = await response.json();
      setSale(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <Link href="/pos/history" className="text-sm text-primary hover:text-primary/80 mb-2 inline-flex items-center gap-1">
            <ArrowRight className="w-4 h-4 rtl:rotate-180" />
            {ARABIC.pos.saleHistory}
          </Link>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.pos.saleDetails}</h1>
        </div>
        
        {sale && (
          <button 
            onClick={() => printInvoice(sale.id)}
            className="flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-2xl hover:bg-primary/90 transition-all shadow-md active:scale-95 font-semibold"
          >
            <Printer className="w-5 h-5" />
            <span>{ARABIC.pos.print || 'طباعة الإيصال'}</span>
          </button>
        )}
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl border border-rose-200 flex items-center">
          <AlertTriangle className="w-5 h-5 me-3 text-rose-500" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
          <p className="text-slate-500 mt-4">{ARABIC.common.loading}</p>
        </div>
      ) : sale ? (
        <div className="space-y-6">
          {sale.reversed && (
            <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl border border-rose-200 flex items-center gap-3">
              <AlertCircle className="w-5 h-5 text-rose-500" />
              <div>
                <p className="font-medium">{ARABIC.pos.saleCancelled}</p>
                {sale.reversal && (
                  <p className="text-sm mt-1">{ARABIC.pos.reversalReason}: {sale.reversal.reason}</p>
                )}
              </div>
            </div>
          )}

          <div className="glass p-6 rounded-2xl">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 bg-blue-100 rounded-xl">
                <Receipt className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-slate-800">{ARABIC.pos.receipt || 'إيصال'}</h2>
                <p className="text-sm text-slate-500 font-mono">{sale.id}</p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div>
                <p className="text-sm text-slate-500">{ARABIC.pos.paymentMethod}</p>
                <p className="font-semibold text-slate-800">{sale.payment_method_name}</p>
              </div>
              <div>
                <p className="text-sm text-slate-500">{ARABIC.common.createdAt}</p>
                <p className="font-semibold text-slate-800">{formatDateTime(sale.created_at)}</p>
              </div>
            </div>

            {sale.note && (
              <div className="mb-6 p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-500">{ARABIC.pos.note || 'ملاحظة'}</p>
                <p className="text-slate-800">{sale.note}</p>
              </div>
            )}
          </div>

          <div className="glass p-6 rounded-2xl">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">{ARABIC.pos.items || 'المنتجات'}</h3>
            <div className="space-y-3">
              {sale.items.map((item, index) => (
                <div key={index} className="flex justify-between items-center py-3 border-b border-slate-100 last:border-b-0">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-slate-100 rounded-lg">
                      <Package className="w-4 h-4 text-slate-500" />
                    </div>
                    <div>
                      <p className="font-medium text-slate-800">{item.product_name}</p>
                      <p className="text-sm text-slate-500">{item.quantity} × {formatCurrency(item.unit_price)}</p>
                    </div>
                  </div>
                  <p className="font-semibold text-slate-800">{formatCurrency(item.line_total)}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="glass p-6 rounded-2xl">
            <h3 className="text-lg font-semibold text-slate-800 mb-4">{ARABIC.pos.financialBreakdown || 'التفصيل المالي'}</h3>
            
            <div className="space-y-3">
              <div className="flex justify-between items-center py-2">
                <p className="text-slate-600">{ARABIC.pos.subtotal}</p>
                <p className="font-medium text-slate-800">{formatCurrency(sale.subtotal)}</p>
              </div>

              {sale.fees.length > 0 && (
                <div className="py-3 border-t border-slate-100">
                  <p className="text-sm text-slate-500 mb-2">{ARABIC.pos.fees}</p>
                  {sale.fees.map((fee, index) => (
                    <div key={index} className="flex justify-between items-center py-1">
                      <p className="text-slate-600">
                        {fee.fee_label}
                        {fee.fee_value_type === "percent" && (
                          <span className="text-xs text-slate-400 ms-1">({fee.fee_value}%)</span>
                        )}
                      </p>
                      <p className="text-slate-800">{formatCurrency(fee.calculated_amount)}</p>
                    </div>
                  ))}
                  <div className="flex justify-between items-center pt-2 mt-2 border-t border-slate-100">
                    <p className="font-medium text-slate-600">{ARABIC.pos.totalFees}</p>
                    <p className="font-medium text-slate-800">{formatCurrency(sale.fees_total)}</p>
                  </div>
                </div>
              )}

              {sale.vat_enabled && sale.vat_amount && (
                <div className="flex justify-between items-center py-2">
                  <p className="text-slate-600">{ARABIC.pos.vat} ({sale.vat_rate}%)</p>
                  <p className="text-slate-800">{formatCurrency(sale.vat_amount)}</p>
                </div>
              )}

              <div className="flex justify-between items-center py-4 border-t border-slate-200 mt-3">
                <p className="text-lg font-bold text-slate-800">{ARABIC.pos.grandTotal}</p>
                <p className="text-xl font-black text-slate-900">{formatCurrency(sale.total)}</p>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}