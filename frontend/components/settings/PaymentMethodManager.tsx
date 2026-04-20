"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";

interface PaymentMethod {
  id: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export default function PaymentMethodManager() {
  const [methods, setMethods] = useState<PaymentMethod[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const [newName, setNewName] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");

  useEffect(() => {
    fetchMethods();
  }, []);

  const fetchMethods = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/settings/payment-methods");
      if (!response.ok) throw new Error("Failed to fetch payment methods");
      const data = await response.json();
      setMethods(data.items);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;

    try {
      const response = await fetch("/api/settings/payment-methods", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName, is_active: true }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to add payment method");
      }

      setNewName("");
      setIsAdding(false);
      fetchMethods();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const handleToggleStatus = async (id: string, currentStatus: boolean) => {
    try {
      const response = await fetch(`/api/settings/payment-methods/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_active: !currentStatus }),
      });

      if (!response.ok) throw new Error("Failed to update status");
      fetchMethods();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const startEdit = (method: PaymentMethod) => {
    setEditingId(method.id);
    setEditName(method.name);
  };

  const handleUpdate = async (id: string) => {
    if (!editName.trim()) return;

    try {
      const response = await fetch(`/api/settings/payment-methods/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: editName }),
      });

      if (!response.ok) throw new Error("Failed to update payment method");
      setEditingId(null);
      fetchMethods();
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (loading && methods.length === 0) {
    return <div className="p-8 text-center text-slate-500">{ARABIC.common.loading}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-slate-800">{ARABIC.settings.paymentMethods}</h2>
        <button
          onClick={() => setIsAdding(true)}
          className="px-4 py-2 bg-primary text-white rounded-xl text-sm font-semibold hover:bg-primary-dark transition-all shadow-md shadow-primary/20 flex items-center"
        >
          <svg className="w-4 h-4 ms-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 4v16m8-8H4"></path></svg>
          {ARABIC.settings.addPaymentMethod}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-100 text-rose-600 rounded-xl text-sm flex items-center">
          <svg className="w-5 h-5 ms-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
          {error}
        </div>
      )}

      <div className="glass overflow-hidden rounded-2xl border border-slate-200/50">
        <table className="w-full text-start border-collapse">
          <thead>
            <tr className="bg-slate-50/50 border-b border-slate-200">
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">{ARABIC.settings.methodName}</th>
              <th className="px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-wider">{ARABIC.settings.isActive}</th>
              <th className="px-6 py-4 text-end text-xs font-bold text-slate-500 uppercase tracking-wider">{ARABIC.common.actions}</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {isAdding && (
              <tr className="bg-blue-50/30">
                <td className="px-6 py-4" colSpan={2}>
                  <form onSubmit={handleAdd} className="flex gap-2">
                    <input
                      autoFocus
                      type="text"
                      className="flex-1 bg-white border border-blue-200 text-slate-800 text-sm rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-blue-500/20 outline-none"
                      placeholder={ARABIC.settings.methodName}
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      dir="rtl"
                    />
                    <button type="submit" className="px-3 py-1.5 bg-blue-600 text-white text-xs font-bold rounded-lg hover:bg-blue-700">{ARABIC.common.save}</button>
                    <button type="button" onClick={() => setIsAdding(false)} className="px-3 py-1.5 bg-slate-200 text-slate-600 text-xs font-bold rounded-lg hover:bg-slate-300">{ARABIC.common.cancel}</button>
                  </form>
                </td>
                <td></td>
              </tr>
            )}
            {methods.map((method) => (
              <tr key={method.id} className="hover:bg-slate-50/50 transition-colors group">
                <td className="px-6 py-4">
                  {editingId === method.id ? (
                    <div className="flex gap-2">
                      <input
                        autoFocus
                        type="text"
                        className="flex-1 bg-white border border-blue-200 text-slate-800 text-sm rounded-lg px-3 py-1.5 focus:ring-2 focus:ring-blue-500/20 outline-none"
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleUpdate(method.id)}
                        dir="rtl"
                      />
                      <button onClick={() => handleUpdate(method.id)} className="text-blue-600 hover:text-blue-800">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                      </button>
                      <button onClick={() => setEditingId(null)} className="text-slate-400 hover:text-slate-600">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                      </button>
                    </div>
                  ) : (
                    <span className={`font-medium ${method.is_active ? "text-slate-800" : "text-slate-400 line-through"}`}>
                      {method.name}
                    </span>
                  )}
                </td>
                <td className="px-6 py-4">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    method.is_active ? "bg-emerald-100 text-emerald-800" : "bg-slate-100 text-slate-800"
                  }`}>
                    {method.is_active ? ARABIC.products.active : ARABIC.products.inactive}
                  </span>
                </td>
                <td className="px-6 py-4 text-end">
                  <div className="flex justify-end gap-3">
                    <button
                      onClick={() => startEdit(method)}
                      className="text-slate-400 hover:text-blue-600 transition-colors"
                      title={ARABIC.common.edit}
                    >
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                    </button>
                    <button
                      onClick={() => handleToggleStatus(method.id, method.is_active)}
                      className={`${method.is_active ? "text-slate-400 hover:text-rose-600" : "text-slate-400 hover:text-emerald-600"} transition-colors`}
                      title={method.is_active ? ARABIC.common.deactivate : ARABIC.common.activate}
                    >
                      {method.is_active ? (
                       <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path></svg>
                      ) : (
                       <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                      )}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {methods.length === 0 && !isAdding && (
          <div className="py-12 text-center text-slate-400 italic">{ARABIC.common.noPaymentMethods}</div>
        )}
      </div>
    </div>
  );
}
