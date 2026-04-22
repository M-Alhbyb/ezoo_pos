"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ARABIC } from '@/lib/constants/arabic';
import { formatCurrency } from '@/lib/utils/format';
import { getCustomers, createCustomer, CustomerWithBalance } from '@/lib/api/customers';
import CustomerModal from '@/components/customers/CustomerModal';

export default function CustomersPage() {
  const router = useRouter();
  const [customers, setCustomers] = useState<CustomerWithBalance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    loadCustomers();
  }, []);

  async function loadCustomers() {
    try {
      setLoading(true);
      const data = await getCustomers();
      setCustomers(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(data: { name: string; phone: string; address?: string; notes?: string; credit_limit?: number }) {
    await createCustomer(data);
    await loadCustomers();
    setIsModalOpen(false);
  }

  if (loading) {
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

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-800 font-heading">{ARABIC.customers.title}</h1>
          <p className="text-slate-500 mt-1">{ARABIC.customers.subtitle}</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="flex items-center px-6 py-3 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-100"
        >
          <svg className="w-5 h-5 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
          </svg>
          {ARABIC.customers.addCustomer}
        </button>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl border border-rose-200 flex items-center shadow-sm">
          <svg className="w-5 h-5 me-3 text-rose-500" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path>
          </svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      <div className="glass rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-start border-collapse">
            <thead>
              <tr className="bg-slate-50/30">
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">{ARABIC.customers.customerName}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">{ARABIC.customers.phone}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.customers.balance}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.customers.creditLimit}</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.customers.availableCredit}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white/50">
              {customers.map((customer) => (
                <tr
                  key={customer.id}
                  onClick={() => router.push(`/customers/${customer.id}`)}
                  className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                >
                  <td className="px-6 py-4 text-sm font-bold text-slate-800">{customer.name}</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{customer.phone || '-'}</td>
                  <td className={`px-6 py-4 text-end font-bold font-mono ${Number(customer.balance) > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                    {formatCurrency(customer.balance)}
                  </td>
                  <td className="px-6 py-4 text-end text-slate-600 font-mono">{formatCurrency(customer.credit_limit)}</td>
                  <td className="px-6 py-4 text-end font-bold font-mono">
                    {formatCurrency(Number(customer.credit_limit) - Number(customer.balance))}
                  </td>
                </tr>
              ))}
              {customers.length === 0 && (
                <tr>
                  <td colSpan={5} className="p-12 text-center text-slate-400">
                    <div className="flex flex-col items-center">
                      <svg className="w-12 h-12 mb-3 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M12 4a9.96 9.96 0 00-6.938 2.808M12 4a9.96 9.96 0 016.938 2.808"></path>
                      </svg>
                      <div className="font-medium">{ARABIC.customers.noCustomers}</div>
                      <button onClick={() => setIsModalOpen(true)} className="mt-3 text-blue-600 hover:underline text-sm">
                        {ARABIC.customers.addCustomerStart}
                      </button>
                    </div>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <CustomerModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}