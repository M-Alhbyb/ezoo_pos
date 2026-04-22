"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ARABIC } from '@/lib/constants/arabic';
import { formatCurrency, formatDate } from '@/lib/utils/format';
import { getSupplier, recordPayment, getSupplierStatement } from '@/lib/api/suppliers';
import { createPurchase, returnItems } from '@/lib/api/purchases';
import type { SupplierDetail, SupplierStatement } from '@/lib/api/suppliers';
import PaymentModal from '@/components/suppliers/PaymentModal';
import PurchaseModal from '@/components/suppliers/PurchaseModal';
import ReturnModal from '@/components/suppliers/ReturnModal';
import LedgerDetailsModal from '@/components/suppliers/LedgerDetailsModal';

export default function SupplierDetailPage() {
  const params = useParams();
  const router = useRouter();
  const supplierId = params.id as string;
  
  const [supplier, setSupplier] = useState<SupplierDetail | null>(null);
  const [statement, setStatement] = useState<SupplierStatement | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [isPurchaseModalOpen, setIsPurchaseModalOpen] = useState(false);
  const [isReturnModalOpen, setIsReturnModalOpen] = useState(false);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [selectedPurchaseId, setSelectedPurchaseId] = useState<string>("");
  const [selectedEntry, setSelectedEntry] = useState<any>(null);

  useEffect(() => {
    loadSupplier();
  }, [supplierId]);

  async function loadSupplier() {
    try {
      setLoading(true);
      const [detail, stmt] = await Promise.all([
        getSupplier(supplierId),
        getSupplierStatement(supplierId),
      ]);
      setSupplier(detail);
      setStatement(stmt);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load supplier');
    } finally {
      setLoading(false);
    }
  }

  async function handlePayment(data: { amount: number; note?: string }) {
    await recordPayment(supplierId, data);
    await loadSupplier();
    setIsPaymentModalOpen(false);
  }

  async function handlePurchase(data: { items: any[] }) {
    await createPurchase({
      supplier_id: supplierId,
      items: data.items
    });
    await loadSupplier();
    setIsPurchaseModalOpen(false);
  }

  async function handleReturn(data: { items: any[], note?: string }) {
    await returnItems(selectedPurchaseId, data);
    await loadSupplier();
    setIsReturnModalOpen(false);
  }

  const openReturnModal = (purchaseId: string) => {
    setSelectedPurchaseId(purchaseId);
    setIsReturnModalOpen(true);
  };

  const openDetailsModal = (entry: any) => {
    setSelectedEntry(entry);
    setIsDetailsModalOpen(true);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400">
        <svg className="animate-spin w-8 h-8 mb-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span className="font-medium">{ARABIC.common.loading}</span>
      </div>
    );
  }

  if (!supplier) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-xl font-bold text-slate-800">المورد غير موجود</h2>
        <button onClick={() => router.back()} className="mt-4 text-blue-600 hover:underline">
          {ARABIC.common.back}
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8">
        <div>
          <div className="flex items-center gap-4 mb-2">
            <button 
              onClick={() => router.back()}
              className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path></svg>
            </button>
            <div className="w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center text-xl font-bold shadow-lg shadow-blue-100">
              {supplier.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{supplier.name}</h1>
              <p className="text-slate-500 flex items-center gap-2">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
                {supplier.phone || "لا يوجد رقم"}
              </p>
            </div>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-3">
          <button 
            onClick={() => setIsPurchaseModalOpen(true)}
            className="flex items-center px-6 py-3 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-100"
          >
            <svg className="w-5 h-5 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
            شراء منتجات
          </button>

          <button 
            onClick={() => {
              // If there are purchases, we could show a list, but for now we'll suggest using the table
              // Or just show an alert if no purchases exist
              const firstPurchase = statement?.ledger.find(e => e.type === 'PURCHASE');
              if (firstPurchase?.reference_id) {
                openReturnModal(firstPurchase.reference_id);
              } else {
                setError("لا توجد فواتير شراء سابقة لهذا المورد لإجراء إرجاع منها");
              }
            }}
            className="flex items-center px-6 py-3 bg-rose-100 text-rose-700 font-bold rounded-2xl hover:bg-rose-200 transition-all border border-rose-200"
          >
            <svg className="w-5 h-5 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 15L12 19L8 15M12 19V5"></path></svg>
            إرجاع منتجات
          </button>
          
          <button 
            onClick={() => setIsPaymentModalOpen(true)}
            className="flex items-center px-6 py-3 bg-emerald-600 text-white font-bold rounded-2xl hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-100"
          >
            <svg className="w-5 h-5 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
            {ARABIC.suppliers.recordPayment}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl mb-4 border border-rose-200 flex items-center shadow-sm">
          <svg className="w-5 h-5 me-3 text-rose-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass p-6 rounded-2xl border-s-4 border-s-blue-500">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.suppliers.totalPurchases}</div>
          <div className="text-2xl font-bold text-slate-800">{formatCurrency(supplier.summary.total_purchases)}</div>
        </div>
        <div className="glass p-6 rounded-2xl border-s-4 border-s-emerald-500">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.suppliers.totalPayments}</div>
          <div className="text-2xl font-bold text-slate-800">{formatCurrency(supplier.summary.total_payments)}</div>
        </div>
        <div className="glass p-6 rounded-2xl border-s-4 border-s-amber-500">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.suppliers.totalReturns}</div>
          <div className="text-2xl font-bold text-slate-800">{formatCurrency(supplier.summary.total_returns)}</div>
        </div>
        <div className={`glass p-6 rounded-2xl border-s-4 ${Number(supplier.summary.balance) > 0 ? 'border-s-rose-500' : 'border-s-emerald-500'}`}>
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.suppliers.balance}</div>
          <div className={`text-2xl font-bold ${Number(supplier.summary.balance) > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
            {formatCurrency(supplier.summary.balance)}
          </div>
        </div>
      </div>

      {/* Notes */}
      {supplier.notes && (
        <div className="glass p-6 rounded-2xl text-start">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">{ARABIC.suppliers.notes}</h3>
          <p className="text-slate-700 leading-relaxed">{supplier.notes}</p>
        </div>
      )}

      {/* Ledger */}
      <div className="glass rounded-2xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-800 font-heading">{ARABIC.suppliers.ledger}</h2>
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            {statement?.ledger.length || 0} {ARABIC.numbers.items}
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-start border-collapse">
            <thead>
              <tr className="bg-slate-50/30">
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.suppliers.date}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.suppliers.type}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.suppliers.amount}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.suppliers.note}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">الإجراءات</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white/50">
              {statement?.ledger.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-50/80 transition-colors group">
                  <td className="px-6 py-4 text-sm text-slate-600">
                    {formatDate(entry.created_at)}
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      {new Date(entry.created_at).toLocaleTimeString('ar-SA')}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      entry.type === 'PURCHASE' ? 'bg-blue-50 text-blue-700 border border-blue-100' :
                      entry.type === 'PAYMENT' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' :
                      'bg-rose-50 text-rose-700 border border-rose-100'
                    }`}>
                      {ARABIC.suppliers.types[entry.type as keyof typeof ARABIC.suppliers.types] || entry.type}
                    </span>
                  </td>
                  <td className={`px-6 py-4 text-end font-bold font-mono ${
                    entry.type === 'PAYMENT' ? 'text-emerald-600' : 
                    entry.type === 'PURCHASE' ? 'text-rose-600' : 'text-slate-700'
                  }`}>
                    {entry.type === 'PAYMENT' || entry.type === 'RETURN' ? '-' : ''}
                    {formatCurrency(entry.amount)}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-500 max-w-xs truncate">
                    {entry.note || <span className="text-slate-300 italic">-</span>}
                    {entry.reference_id && (
                      <div className="text-[10px] text-blue-500 mt-1 font-mono">
                        #{entry.reference_id.substring(0, 8)}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 text-end">
                    <div className="flex justify-end gap-2">
                      <button 
                        onClick={() => openDetailsModal(entry)}
                        className="p-1.5 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors border border-transparent hover:border-blue-100"
                        title="عرض التفاصيل"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                      </button>

                      {entry.type === 'PURCHASE' && entry.reference_id && (
                        <button 
                          onClick={() => openReturnModal(entry.reference_id!)}
                          className="flex items-center gap-1.5 px-3 py-1.5 text-rose-600 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors border border-rose-100 text-[10px] font-bold uppercase"
                          title="إرجاع منتجات من هذه الفاتورة"
                        >
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 15L12 19L8 15M12 19V5"></path></svg>
                          إرجاع
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {(!statement?.ledger || statement.ledger.length === 0) && (
                <tr>
                  <td colSpan={5} className="p-12 text-center text-slate-400">
                    <div className="flex flex-col items-center">
                      <svg className="w-12 h-12 mb-3 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>
                      <div className="font-medium">لا توجد حركات مسجلة بعد</div>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <PaymentModal 
        isOpen={isPaymentModalOpen}
        onClose={() => setIsPaymentModalOpen(false)}
        onSubmit={handlePayment}
      />
      
      <PurchaseModal 
        isOpen={isPurchaseModalOpen}
        onClose={() => setIsPurchaseModalOpen(false)}
        onSubmit={handlePurchase}
      />
      
      {selectedPurchaseId && (
        <ReturnModal 
          isOpen={isReturnModalOpen}
          onClose={() => setIsReturnModalOpen(false)}
          purchaseId={selectedPurchaseId}
          onSubmit={handleReturn}
        />
      )}

      <LedgerDetailsModal
        isOpen={isDetailsModalOpen}
        onClose={() => setIsDetailsModalOpen(false)}
        entry={selectedEntry}
      />
    </div>
  );
}