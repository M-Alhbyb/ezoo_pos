"use client";

import { useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import { LedgerEntry } from "@/lib/api/customers";

interface LedgerTableProps {
  entries: LedgerEntry[];
  showFilters?: boolean;
  onEntryClick?: (entry: LedgerEntry) => void;
}

export default function LedgerTable({ entries, showFilters = true, onEntryClick }: LedgerTableProps) {
  const [typeFilter, setTypeFilter] = useState<string | null>(null);
  const [dateFilter, setDateFilter] = useState<string | null>(null);

  const filteredEntries = entries.filter(entry => {
    if (typeFilter && entry.type !== typeFilter) return false;
    if (dateFilter) {
      const entryDate = new Date(entry.created_at).toISOString().split('T')[0];
      if (entryDate !== dateFilter) return false;
    }
    return true;
  });

  return (
    <div className="space-y-4">
      {showFilters && (
        <div className="flex gap-4 flex-wrap">
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
              التصفية حسب النوع
            </label>
            <select
              value={typeFilter || ""}
              onChange={(e) => setTypeFilter(e.target.value || null)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm"
            >
              <option value="">الكل</option>
              <option value="SALE">بيع</option>
              <option value="PAYMENT">دفعة</option>
              <option value="RETURN">مرتجع</option>
            </select>
          </div>
          <div>
            <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">
              التاريخ
            </label>
            <input
              type="date"
              value={dateFilter || ""}
              onChange={(e) => setDateFilter(e.target.value || null)}
              className="px-3 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm"
            />
          </div>
          {(typeFilter || dateFilter) && (
            <div className="flex items-end">
              <button
                onClick={() => { setTypeFilter(null); setDateFilter(null); }}
                className="px-4 py-2 text-sm text-rose-600 hover:bg-rose-50 rounded-xl"
              >
                مسح الفلاتر
              </button>
            </div>
          )}
        </div>
      )}

      <div className="overflow-x-auto">
        <table className="w-full text-start border-collapse">
          <thead>
            <tr className="bg-slate-50/30">
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">التاريخ</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">النوع</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">المبلغ</th>
              <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-start">ملاحظة</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white/50">
            {filteredEntries.map((entry) => (
              <tr
                key={entry.id}
                onClick={() => onEntryClick?.(entry)}
                className={`hover:bg-slate-50/80 transition-colors ${onEntryClick ? 'cursor-pointer' : ''}`}
              >
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
                  entry.type === 'PAYMENT' || entry.type === 'RETURN' ? 'text-emerald-600' : 'text-rose-600'
                }`}>
                  {entry.type === 'PAYMENT' || entry.type === 'RETURN' ? '-' : ''}
                  {formatCurrency(entry.amount)}
                </td>
                <td className="px-6 py-4 text-sm text-slate-500 max-w-xs truncate">
                  {entry.note || <span className="text-slate-300 italic">-</span>}
                  {entry.payment_method && (
                    <div className="text-[10px] text-slate-400 mt-1">
                      {entry.payment_method}
                    </div>
                  )}
                </td>
              </tr>
            ))}
            {filteredEntries.length === 0 && (
              <tr>
                <td colSpan={4} className="p-12 text-center text-slate-400">
                  <div className="flex flex-col items-center">
                    <svg className="w-12 h-12 mb-3 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                    </svg>
                    <div className="font-medium">لا توجد حركات مسجلة</div>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}