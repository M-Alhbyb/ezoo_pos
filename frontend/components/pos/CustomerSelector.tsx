"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { getCustomers, CustomerWithBalance } from "@/lib/api/customers";

interface CustomerSelectorProps {
  selectedCustomerId: string | null;
  onSelect: (customerId: string | null) => void;
  onBalanceCheck?: (customerId: string | null) => Promise<{ balance: number; credit_limit: number } | null>;
}

export default function CustomerSelector({ selectedCustomerId, onSelect, onBalanceCheck }: CustomerSelectorProps) {
  const [customers, setCustomers] = useState<CustomerWithBalance[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadCustomers();
  }, []);

  async function loadCustomers() {
    try {
      setLoading(true);
      const data = await getCustomers();
      setCustomers(data.filter(c => Number(c.credit_limit) > 0));
    } catch (e) {
      console.error("Failed to load customers:", e);
    } finally {
      setLoading(false);
    }
  }

  const filteredCustomers = customers.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.phone?.includes(search)
  );

  const selectedCustomer = customers.find(c => c.id === selectedCustomerId);

  const handleSelect = async (customerId: string | null) => {
    onSelect(customerId);
    setIsOpen(false);
    setSearch("");
  };

  return (
    <div className="relative">
      <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
        {ARABIC.customers.customerName}
      </label>
      
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-medium text-slate-800 text-start flex items-center justify-between"
      >
        {selectedCustomer ? (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm font-bold">
              {selectedCustomer.name.charAt(0)}
            </div>
            <div>
              <div className="font-bold">{selectedCustomer.name}</div>
              <div className="text-xs text-slate-500">
                الرصيد: {Number(selectedCustomer.balance).toFixed(2)} | الحد: {Number(selectedCustomer.credit_limit).toFixed(2)}
              </div>
            </div>
          </div>
        ) : (
          <span className="text-slate-400">{ARABIC.customers.selectCustomer || 'اختر عميل...'}</span>
        )}
        <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path>
        </svg>
      </button>

      {selectedCustomerId && selectedCustomer && (
        <div className="mt-2 p-3 bg-amber-50 border border-amber-200 rounded-xl">
          <div className="flex items-center justify-between text-sm">
            <span className="text-amber-700">{ARABIC.customers.availableCredit}:</span>
            <span className={`font-bold ${Number(selectedCustomer.credit_limit) - Number(selectedCustomer.balance) < 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
              {((Number(selectedCustomer.credit_limit) - Number(selectedCustomer.balance))).toFixed(2)} ج.س
            </span>
          </div>
        </div>
      )}

      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-slate-200 rounded-xl shadow-xl max-h-64 overflow-hidden">
          <div className="p-2 border-b border-slate-100">
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={ARABIC.common.search}
              className="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              autoFocus
            />
          </div>
          <div className="overflow-y-auto max-h-48">
            {loading ? (
              <div className="p-4 text-center text-slate-400">{ARABIC.common.loading}</div>
            ) : filteredCustomers.length === 0 ? (
              <div className="p-4 text-center text-slate-400">{ARABIC.customers.noCustomers}</div>
            ) : (
              filteredCustomers.map(customer => (
                <button
                  key={customer.id}
                  type="button"
                  onClick={() => handleSelect(customer.id)}
                  className="w-full px-4 py-3 text-start hover:bg-slate-50 flex items-center gap-3 border-b border-slate-50 last:border-0"
                >
                  <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm font-bold">
                    {customer.name.charAt(0)}
                  </div>
                  <div className="flex-1">
                    <div className="font-bold text-slate-800">{customer.name}</div>
                    <div className="text-xs text-slate-500">{customer.phone}</div>
                  </div>
                  <div className="text-end">
                    <div className={`text-sm font-bold ${Number(customer.balance) > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                      {Number(customer.balance).toFixed(2)}
                    </div>
                    <div className="text-xs text-slate-400">من {Number(customer.credit_limit).toFixed(2)}</div>
                  </div>
                </button>
              ))
            )}
          </div>
          {selectedCustomerId && (
            <button
              type="button"
              onClick={() => handleSelect(null)}
              className="w-full px-4 py-2 text-center text-rose-600 hover:bg-rose-50 border-t border-slate-100 text-sm font-medium"
            >
              {ARABIC.common.clearAll}
            </button>
          )}
        </div>
      )}
    </div>
  );
}