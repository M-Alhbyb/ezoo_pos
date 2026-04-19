"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDateTime } from "@/lib/utils/format";
import { ArrowRight, User, TrendingUp, Calendar, Info, Receipt, X, ExternalLink, Hash, Package, Tag, CreditCard } from "lucide-react";
import SaleDetailModal from "@/components/reports/SaleDetailModal";

interface Distribution {
  id: string;
  amount: string;
  distributed_at: string;
}

interface WalletTransaction {
  id: string;
  amount: number;
  transaction_type: string;
  description: string;
  balance_after: number;
  reference_id: string | null;
  reference_type: string | null;
  created_at: string;
}

interface Partner {
  id: number;
  name: string;
  share_percentage: number;
  investment_amount: string;
  created_at: string;
  distributions: Distribution[];
}

interface Product {
  id: string;
  name: string;
  sku: string;
  selling_price: number;
  stock_quantity: number;
  category_name: string;
}

export default function PartnerHistoryPage({ params }: { params: { partnerId: string } }) {
  const { partnerId } = params;
  const [partner, setPartner] = useState<Partner | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [transactions, setTransactions] = useState<WalletTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  // Modal states
  const [selectedTransaction, setSelectedTransaction] = useState<WalletTransaction | null>(null);
  const [isSaleModalOpen, setIsSaleModalOpen] = useState(false);
  const [isManualModalOpen, setIsManualModalOpen] = useState(false);

  useEffect(() => {
    fetchPartner();
    fetchTransactions();
    fetchProducts();
  }, [partnerId]);

  const fetchPartner = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/partners/${partnerId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(ARABIC.partners.partnerNotFound || 'الشريك غير موجود');
        }
        throw new Error(ARABIC.common.error);
      }

      const data = await response.json();
      setPartner(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchTransactions = async () => {
    try {
      const response = await fetch(`/api/partners/${partnerId}/wallet/transactions`);
      if (response.ok) {
        const data = await response.json();
        setTransactions(data.transactions);
      }
    } catch (err) {
      console.error("Failed to fetch partner transactions", err);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await fetch(`/api/products?partner_id=${partnerId}&page_size=100`);
      if (response.ok) {
        const data = await response.json();
        setProducts(data.items);
      }
    } catch (err) {
      console.error("Failed to fetch partner products", err);
    }
  };

  const handleTransactionClick = (tx: WalletTransaction) => {
    setSelectedTransaction(tx);
    if (tx.transaction_type === 'sale_profit' && tx.reference_id) {
      setIsSaleModalOpen(true);
    } else {
      setIsManualModalOpen(true);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <Link href="/partners" className="text-sm text-primary hover:text-primary/80 mb-2 inline-flex items-center gap-1">
            <ArrowRight className="w-4 h-4 rtl:rotate-180" />
            {ARABIC.partners.title}
          </Link>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.partners.partnerHistory || 'سجل الشريك'}</h1>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl border border-rose-200 flex items-center">
          <ArrowRight className="w-5 h-5 me-3 text-rose-500" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
          <p className="text-slate-500 mt-4">{ARABIC.common.loading}</p>
        </div>
      ) : partner ? (
        <>
          {/* Partner Header */}
          <div className="glass p-6 rounded-2xl">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-16 h-16 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-2xl">
                {partner.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-800">{partner.name}</h2>
                <p className="text-sm text-slate-500 font-mono">{partner.id}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
              <div className="bg-slate-50 p-4 rounded-xl">
                <p className="text-xs font-semibold text-slate-500 uppercase">{ARABIC.partners.sharePercentage}</p>
                <p className="text-2xl font-bold text-indigo-600">{parseFloat(partner.share_percentage.toString()).toFixed(2)}%</p>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl">
                <p className="text-xs font-semibold text-slate-500 uppercase">{ARABIC.partners.investmentAmount}</p>
                <p className="text-2xl font-bold text-slate-800">{formatCurrency(partner.investment_amount)}</p>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl">
                <p className="text-xs font-semibold text-slate-500 uppercase">{ARABIC.common.createdAt}</p>
                <p className="text-lg font-medium text-slate-800">{formatDateTime(partner.created_at)}</p>
              </div>
            </div>
          </div>

          {/* Distribution History */}
          <div className="glass rounded-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-500" />
                {ARABIC.partners.distributionHistory || 'سجل العمليات'}
              </h3>
            </div>
            {!transactions || transactions.length === 0 ? (
              <div className="p-8 text-center text-slate-400">
                <Calendar className="w-12 h-12 mx-auto mb-3 text-slate-200" />
                <p>{ARABIC.partners.noDistributions || 'لا توجد معاملات بعد'}</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-100">
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">{ARABIC.common.status || 'العملية'}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">{'الوصف'}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{'المبلغ'}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{'الرصيد بعد'}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{ARABIC.common.createdAt}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {transactions.map((tx) => (
                      <tr 
                        key={tx.id} 
                        className="hover:bg-slate-50/50 cursor-pointer transition-colors group"
                        onClick={() => handleTransactionClick(tx)}
                      >
                        <td className="px-6 py-4 font-medium text-slate-800">
                          <div className="flex items-center gap-2">
                            <span className={`w-2 h-2 rounded-full ${tx.transaction_type === 'sale_profit' ? 'bg-emerald-500' : 'bg-blue-500'}`}></span>
                            {tx.transaction_type === 'sale_profit' ? 'ارباح مبيعات' : 'تعديل يدوي'}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-600 max-w-[300px] truncate" title={tx.description || ""}>
                          {tx.description}
                        </td>
                        <td className={`px-6 py-4 text-end font-semibold ${tx.amount > 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                          {tx.amount > 0 ? '+' : ''}{formatCurrency(tx.amount)}
                        </td>
                        <td className="px-6 py-4 text-end font-bold text-slate-900">
                          {formatCurrency(tx.balance_after)}
                        </td>
                        <td className="px-6 py-4 text-end text-sm text-slate-500">
                          <div className="flex items-center justify-end gap-2">
                            {formatDateTime(tx.created_at)}
                            <ExternalLink className="w-3 h-3 text-slate-300 group-hover:text-primary transition-colors" />
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Assigned Products Section */}
          <div className="glass rounded-2xl overflow-hidden mt-8">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-blue-500" />
                {ARABIC.partners.assignedProducts}
              </h3>
              <div className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-bold">
                {products.length} {ARABIC.nav.products}
              </div>
            </div>
            {products.length === 0 ? (
              <div className="p-8 text-center text-slate-400">
                <p>{ARABIC.reports.noData}</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-100">
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">{ARABIC.products.productName}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-center">{ARABIC.products.category}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{ARABIC.products.stockQuantity}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{ARABIC.products.sellingPrice}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {products.map((product) => (
                      <tr key={product.id} className="hover:bg-slate-50/50">
                        <td className="px-6 py-4">
                          <div className="font-medium text-slate-800">{product.name}</div>
                          <div className="text-[10px] text-slate-400 font-mono">{product.sku}</div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className="bg-slate-100 px-2 py-1 rounded-lg text-xs font-medium text-slate-600">
                            {product.category_name}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-end">
                           <span className={`font-bold ${product.stock_quantity <= 5 ? "text-rose-500" : "text-slate-700"}`}>
                            {product.stock_quantity}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-end font-bold text-slate-900">{formatCurrency(product.selling_price)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      ) : null}

      {/* Sale Detail Modal */}
      {selectedTransaction && selectedTransaction.reference_id && (
        <SaleDetailModal 
          isOpen={isSaleModalOpen}
          onClose={() => setIsSaleModalOpen(false)}
          saleId={selectedTransaction.reference_id}
        />
      )}

      {/* Manual Adjustment Modal */}
      {selectedTransaction && isManualModalOpen && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <div 
            className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
            onClick={() => setIsManualModalOpen(false)}
          />
          <div className="relative w-full max-w-lg bg-white rounded-[2rem] shadow-2xl border border-white/20 overflow-hidden animate-in zoom-in-95 fade-in duration-300">
            <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-100 text-blue-600 rounded-2xl">
                  <Info className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-slate-800">تفاصيل العملية</h2>
                  <p className="text-xs text-slate-500 font-medium">تعديل يدوي للرصيد</p>
                </div>
              </div>
              <button 
                onClick={() => setIsManualModalOpen(false)}
                className="p-2 hover:bg-slate-200 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-slate-400" />
              </button>
            </div>
            <div className="p-8 space-y-6">
              <div className="space-y-4">
                <div className="bg-slate-50 p-4 rounded-2xl space-y-2">
                  <div className="flex justify-between items-center text-xs font-bold text-slate-400 uppercase tracking-wider">
                    <span>القيمة</span>
                    <span>التاريخ</span>
                  </div>
                  <div className="flex justify-between items-end">
                    <span className={`text-2xl font-black ${selectedTransaction.amount > 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                      {selectedTransaction.amount > 0 ? '+' : ''}{formatCurrency(selectedTransaction.amount)}
                    </span>
                    <span className="text-sm font-bold text-slate-600">{formatDateTime(selectedTransaction.created_at)}</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <h3 className="text-xs font-black text-slate-400 uppercase tracking-widest flex items-center gap-2">
                    <Package className="w-3 h-3" />
                    الوصف
                  </h3>
                  <div className="p-4 bg-blue-50/50 border border-blue-100/50 rounded-2xl text-slate-700 font-medium leading-relaxed">
                    {selectedTransaction.description}
                  </div>
                </div>

                <div className="bg-slate-900 p-4 rounded-2xl flex justify-between items-center">
                  <span className="text-sm font-bold text-slate-400">الرصيد بعد العملية</span>
                  <span className="text-xl font-black text-white tracking-tight">{formatCurrency(selectedTransaction.balance_after)}</span>
                </div>
              </div>
            </div>
            <div className="px-8 py-6 bg-slate-50/50 border-t border-slate-100 flex justify-end">
              <button
                onClick={() => setIsManualModalOpen(false)}
                className="px-6 py-2.5 bg-slate-900 text-white font-bold rounded-xl hover:bg-slate-800 active:scale-95 transition-all"
              >
                إغلاق
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}