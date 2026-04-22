"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ARABIC } from '@/lib/constants/arabic';
import { formatCurrency } from '@/lib/utils/format';
import { getCustomerSummaryReport, CustomerReportResponse } from '@/lib/api/customers';

export default function CustomersReportPage() {
  const router = useRouter();
  const [report, setReport] = useState<CustomerReportResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadReport();
  }, []);

  async function loadReport() {
    try {
      setLoading(true);
      const data = await getCustomerSummaryReport();
      setReport(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load report');
    } finally {
      setLoading(false);
    }
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800">{ARABIC.customers.globalReport}</h1>
          <p className="text-slate-500 mt-1">{ARABIC.customers.subtitle}</p>
        </div>
        <button
          onClick={() => window.print()}
          className="flex items-center px-6 py-3 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-100"
        >
          <svg className="w-5 h-5 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"></path>
          </svg>
          {ARABIC.common.export}
        </button>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl border border-rose-200">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass p-6 rounded-2xl border-s-4 border-s-blue-500">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">
            عدد العملاء
          </div>
          <div className="text-3xl font-bold text-slate-800">{report?.total_customers || 0}</div>
        </div>
        <div className="glass p-6 rounded-2xl border-s-4 border-s-emerald-500">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">
            إجمالي المبيعات الآجلة
          </div>
          <div className="text-3xl font-bold text-slate-800">{formatCurrency(report?.total_debt || 0)}</div>
        </div>
        <div className="glass p-6 rounded-2xl border-s-4 border-s-rose-500">
          <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">
            متوسط الرصيد
          </div>
          <div className="text-3xl font-bold text-slate-800">
            {report?.total_customers ? formatCurrency(report.total_debt / report.total_customers) : formatCurrency(0)}
          </div>
        </div>
      </div>

      <div className="glass rounded-2xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-start border-collapse">
            <thead>
              <tr className="bg-slate-50/30">
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">العميل</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">الهاتف</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">الحد الائتماني</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">الرصيد</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">المتوفر</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white/50">
              {report?.customers.map((customer) => (
                <tr
                  key={customer.id}
                  onClick={() => router.push(`/customers/${customer.id}`)}
                  className="hover:bg-slate-50/80 transition-colors cursor-pointer"
                >
                  <td className="px-6 py-4 text-sm font-bold text-slate-800">{customer.name}</td>
                  <td className="px-6 py-4 text-sm text-slate-600">{customer.phone || '-'}</td>
                  <td className="px-6 py-4 text-end font-mono text-slate-600">{formatCurrency(customer.credit_limit)}</td>
                  <td className={`px-6 py-4 text-end font-bold font-mono ${customer.balance > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                    {formatCurrency(customer.balance)}
                  </td>
                  <td className="px-6 py-4 text-end font-mono text-slate-600">
                    {formatCurrency(customer.credit_limit - customer.balance)}
                  </td>
                </tr>
              ))}
              {(!report?.customers || report.customers.length === 0) && (
                <tr>
                  <td colSpan={5} className="p-12 text-center text-slate-400">
                    لا يوجد عملاء
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}