"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDate } from "@/lib/utils/format";
import { getSuppliers, createSupplier, SupplierWithBalance } from "@/lib/api/suppliers";
import SupplierModal from "@/components/suppliers/SupplierModal";

export default function SuppliersPage() {
  const [suppliers, setSuppliers] = useState<SupplierWithBalance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    loadSuppliers();
  }, []);

  const loadSuppliers = async () => {
    try {
      setLoading(true);
      const data = await getSuppliers();
      setSuppliers(data);
    } catch (err: any) {
      setError(err.message || ARABIC.common.error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddSupplier = async (data: any) => {
    try {
      await createSupplier(data);
      await loadSuppliers();
      setIsModalOpen(false);
    } catch (err: any) {
      throw new Error(err.message || ARABIC.common.error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.suppliers.title}</h1>
          <p className="text-slate-500 mt-1">{ARABIC.suppliers.subtitle}</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center px-4 py-2.5 bg-primary text-white font-medium rounded-xl hover:bg-blue-600 transition-all shadow-sm shadow-blue-200"
        >
          <svg className="w-5 h-5 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
          {ARABIC.suppliers.addSupplier}
        </button>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl mb-4 border border-rose-200 animate-slide-up flex items-center shadow-sm">
          <svg className="w-5 h-5 me-3 text-rose-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      <div className="glass rounded-2xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400">
            <svg className="animate-spin w-8 h-8 mb-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="font-medium">{ARABIC.common.loading}</span>
          </div>
        ) : suppliers.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-start border-collapse animate-fade-in">
              <thead>
                <tr className="bg-slate-50/50 border-b border-slate-200">
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.suppliers.supplierName}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.suppliers.phone}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.suppliers.balance}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.common.createdAt}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white/50">
                {suppliers.map((supplier) => (
                  <tr key={supplier.id} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="px-6 py-4 font-medium text-slate-800">
                      <Link href={`/suppliers/${supplier.id}`} className="flex items-center gap-3 hover:text-primary transition-colors">
                        <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center text-xs">
                          {supplier.name.charAt(0).toUpperCase()}
                        </div>
                        {supplier.name}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-end font-medium text-slate-600">
                      {supplier.phone || "-"}
                    </td>
                    <td className={`px-6 py-4 text-end font-bold ${Number(supplier.balance) > 0 ? 'text-rose-600' : 'text-emerald-600'}`}>
                      {formatCurrency(supplier.balance)}
                    </td>
                    <td className="px-6 py-4 text-end text-sm text-slate-500">
                      {formatDate(supplier.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-24 text-slate-400 animate-fade-in">
            <svg className="w-16 h-16 mb-4 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
            <div className="text-lg font-medium text-slate-600 mb-1">{ARABIC.suppliers.noSuppliers}</div>
            <p className="text-sm">{ARABIC.suppliers.addSupplierStart}</p>
          </div>
        )}
      </div>

      <SupplierModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleAddSupplier}
      />
    </div>
  );
}