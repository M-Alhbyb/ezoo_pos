"use client";

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { ARABIC } from '@/lib/constants/arabic';
import { formatCurrency, formatDate } from '@/lib/utils/format';
import { getCustomer, getCustomerLedger, recordCustomerPayment, CustomerDetail, LedgerEntry } from '@/lib/api/customers';
import CustomerPaymentModal from '@/components/customers/PaymentModal';
import { ExportButtonGroup } from '@/components/reports/ExportButtonGroup';
import SaleDetailModal from '@/components/pos/SaleDetailModal';

export default function CustomerDetailPage() {
  const params = useParams();
  const router = useRouter();
  const customerId = params.id as string;

  const [customer, setCustomer] = useState<CustomerDetail | null>(null);
  const [ledger, setLedger] = useState<LedgerEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [isSaleDetailModalOpen, setIsSaleDetailModalOpen] = useState(false);
  const [isReturnAction, setIsReturnAction] = useState(false);
  const [selectedSaleId, setSelectedSaleId] = useState<string | null>(null);

  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  useEffect(() => {
    loadCustomer();
  }, [customerId, startDate, endDate]);

  async function loadCustomer() {
    try {
      setLoading(true);
      const [customerData, ledgerData] = await Promise.all([
        getCustomer(customerId),
        getCustomerLedger(customerId, 1, 2000, startDate || undefined, endDate || undefined),
      ]);
      setCustomer(customerData);
      setLedger(ledgerData.entries);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }

  async function handlePayment(data: { amount: number; payment_method: string; note?: string }) {
    await recordCustomerPayment(customerId, data);
    await loadCustomer();
    setIsPaymentModalOpen(false);
  }

  if (loading && !customer) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400">
        <svg className="animate-spin w-8 h-8 mb-4 text-indigo-500" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span className="font-medium">{ARABIC.common.loading}</span>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-xl font-bold text-slate-800">{ARABIC.customers.noCustomers}</h2>
        <button onClick={() => router.back()} className="mt-4 text-blue-600 hover:underline">
          {ARABIC.common.back}
        </button>
      </div>
    );
  }

  const availableCredit = Number(customer.credit_limit) - Number(customer.summary.balance);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
          <div className="w-12 h-12 rounded-2xl bg-blue-600 text-white flex items-center justify-center text-xl font-bold shadow-lg shadow-blue-100">
            {customer.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{customer.name}</h1>
            <p className="text-slate-500 flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
              </svg>
              {customer.phone || ARABIC.common.none}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2 bg-white p-1.5 rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="bg-transparent border-none text-xs font-bold text-slate-600 focus:ring-0 cursor-pointer"
            />
            <span className="text-slate-300 text-[10px]">●</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="bg-transparent border-none text-xs font-bold text-slate-600 focus:ring-0 cursor-pointer"
            />
          </div>

          <button
            onClick={() => router.push(`/pos?customerId=${customerId}`)}
            className="flex items-center px-5 py-2.5 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-700 transition-all shadow-md shadow-blue-100 text-sm"
          >
            <svg className="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
            </svg>
            {ARABIC.sales.newSale || "بيع منتجات"}
          </button>

          <button
            onClick={() => {
              const latestSale = ledger.find(e => e.type === 'SALE' && e.reference_id);
              if (latestSale) {
                setSelectedSaleId(latestSale.reference_id!);
                setIsReturnAction(true);
                setIsSaleDetailModalOpen(true);
              } else {
                setError("لا توجد عمليات بيع لهذا العميل لإرجاعها");
              }
            }}
            className="flex items-center px-5 py-2.5 bg-rose-100 text-rose-700 font-bold rounded-2xl hover:bg-rose-200 transition-all border border-rose-200 text-sm"
          >
            <svg className="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 15L12 19L8 15M12 19V5"></path>
            </svg>
            {ARABIC.pos.returnItems || "إرجاع منتجات"}
          </button>

          <button
            onClick={() => setIsPaymentModalOpen(true)}
            className="flex items-center px-5 py-2.5 bg-emerald-600 text-white font-bold rounded-2xl hover:bg-emerald-700 transition-all shadow-md shadow-emerald-100 text-sm"
          >
            <svg className="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            {ARABIC.customers.recordPayment}
          </button>

          {/* New Dynamic Export Group */}
          <div className="border-s border-slate-200 ps-3 ms-1 hidden md:block">
            <ExportButtonGroup 
              reportType={`customers/${customerId}`}
              startDate={startDate}
              endDate={endDate}
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl mb-4 border border-rose-200 flex items-center shadow-sm">
          <svg className="w-5 h-5 me-3 text-rose-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path>
          </svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass p-6 rounded-2xl border-s-4 border-s-blue-500">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.customers.totalSales}</div>
          <div className="text-2xl font-bold text-slate-800">{formatCurrency(customer.summary.total_sales)}</div>
        </div>
        <div className="glass p-6 rounded-2xl border-s-4 border-s-emerald-500">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.customers.totalPayments}</div>
          <div className="text-2xl font-bold text-slate-800">{formatCurrency(customer.summary.total_payments)}</div>
        </div>
        <div className="glass p-6 rounded-2xl border-s-4 border-s-amber-500">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.customers.totalReturns}</div>
          <div className="text-2xl font-bold text-slate-800">{formatCurrency(customer.summary.total_returns)}</div>
        </div>
        <div className={`glass p-6 rounded-2xl border-s-4 ${Number(customer.summary.balance) > 0 ? 'border-s-rose-500' : 'border-s-emerald-500'}`}>
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.customers.balance}</div>
          <div className={`text-2xl font-bold ${Number(customer.summary.balance) > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
            {formatCurrency(customer.summary.balance)}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glass p-6 rounded-2xl">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.customers.creditLimit}</div>
          <div className="text-2xl font-bold text-slate-800">{formatCurrency(customer.credit_limit)}</div>
        </div>
        <div className={`glass p-6 rounded-2xl ${availableCredit < 0 ? 'border-s-rose-500 border-s-4' : 'border-s-emerald-500 border-s-4'}`}>
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">{ARABIC.customers.availableCredit}</div>
          <div className={`text-2xl font-bold ${availableCredit < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
            {formatCurrency(availableCredit)}
          </div>
        </div>
      </div>

      {customer.address && (
        <div className="glass p-6 rounded-2xl text-start">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">{ARABIC.customers.address}</h3>
          <p className="text-slate-700 leading-relaxed">{customer.address}</p>
        </div>
      )}

      {customer.notes && (
        <div className="glass p-6 rounded-2xl text-start">
          <h3 className="text-sm font-bold text-slate-400 uppercase tracking-wider mb-2">{ARABIC.customers.notes}</h3>
          <p className="text-slate-700 leading-relaxed">{customer.notes}</p>
        </div>
      )}

      <div className="glass rounded-2xl overflow-hidden shadow-sm">
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
          <h2 className="text-xl font-bold text-slate-800 font-heading">{ARABIC.customers.ledger}</h2>
          <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            {ledger.length} {ARABIC.numbers.items}
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-start border-collapse">
            <thead>
              <tr className="bg-slate-50/30">
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">{ARABIC.customers.date}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">{ARABIC.customers.type}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.customers.amount}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">{ARABIC.customers.note}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-center">{ARABIC.common.actions || "الإجراءات"}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white/50">
              {ledger.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-50/80 transition-colors">
                  <td className="px-6 py-4 text-sm text-slate-600">
                    {formatDate(entry.created_at)}
                    <div className="text-[10px] text-slate-400 mt-0.5">
                      {new Date(entry.created_at).toLocaleTimeString('ar-SA')}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                      entry.type === 'SALE' ? 'bg-blue-50 text-blue-700 border border-blue-100' :
                      entry.type === 'PAYMENT' ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' :
                      'bg-rose-50 text-rose-700 border border-rose-100'
                    }`}>
                      {ARABIC.customers.types[entry.type as keyof typeof ARABIC.customers.types] || entry.type}
                    </span>
                  </td>
                  <td className={`px-6 py-4 text-end font-bold font-mono ${
                    entry.type === 'PAYMENT' ? 'text-emerald-600' :
                    entry.type === 'SALE' ? 'text-rose-600' : 'text-slate-700'
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
                  <td className="px-6 py-4 text-center">
                    {entry.type === 'SALE' && entry.reference_id && (
                      <div className="flex justify-center gap-2">
                        <button
                          onClick={() => {
                            setSelectedSaleId(entry.reference_id);
                            setIsReturnAction(false);
                            setIsSaleDetailModalOpen(true);
                          }}
                          className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors shadow-sm border border-blue-100"
                          title="التفاصيل والطباعة"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
              {ledger.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-12 text-center text-slate-400">
                    <div className="flex flex-col items-center">
                      <svg className="w-12 h-12 mb-3 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                      </svg>
                      <div className="font-medium">لا توجد حركات مسجلة بعد</div>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <CustomerPaymentModal
        isOpen={isPaymentModalOpen}
        onClose={() => setIsPaymentModalOpen(false)}
        onSubmit={handlePayment}
      />

      <SaleDetailModal
        isOpen={isSaleDetailModalOpen}
        onClose={() => {
          setIsSaleDetailModalOpen(false);
          setIsReturnAction(false);
        }}
        saleId={selectedSaleId}
        onSaleReversed={loadCustomer}
        initialReturnMode={isReturnAction}
      />
    </div>
  );
}