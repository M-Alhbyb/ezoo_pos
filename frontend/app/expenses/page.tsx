"use client";
import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDate } from "@/lib/utils/format";

interface Expense {
  id: string;
  description: string;
  amount: string;
  category: string;
  date: string;
  created_at: string;
}

export default function ExpensesPage() {
  const [expenses, setExpenses] = useState<Expense[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<Expense | undefined>(undefined);
  const [formData, setFormData] = useState({ description: "", amount: "", category: "", date: "" });

  useEffect(() => {
    fetchExpenses();
  }, []);

  const fetchExpenses = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/expenses");
      if (!response.ok) throw new Error("Failed to fetch expenses");
      
      const data = await response.json();
      setExpenses(data.items);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (expenseId: string) => {
    if (!confirm(ARABIC.common.confirmDelete)) return;
    try {
      const response = await fetch(`/api/expenses/${expenseId}`, {
        method: "DELETE",
      });
      
      if (!response.ok) throw new Error("Failed to delete expense");
      
      setExpenses(expenses.filter(e => e.id !== expenseId));
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleEditExpense = (expense: Expense) => {
    setEditingExpense(expense);
    setFormData({
      description: expense.description,
      amount: expense.amount,
      category: expense.category,
      date: expense.date,
    });
    setIsModalOpen(true);
  };

  const handleAddExpense = () => {
    setEditingExpense(undefined);
    setFormData({ description: "", amount: "", category: "", date: new Date().toISOString().split('T')[0] });
    setIsModalOpen(true);
  };

  const handleSaveExpense = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const url = editingExpense 
        ? `/api/expenses/${editingExpense.id}` 
        : "/api/expenses";
      const method = editingExpense ? "PATCH" : "POST";

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to save expense");
      }

      await fetchExpenses();
      setIsModalOpen(false);
      setFormData({ description: "", amount: "", category: "", date: "" });
    } catch (err: any) {
      alert(err.message);
    }
  };

  const totalExpenses = expenses.reduce((sum, exp) => sum + parseFloat(exp.amount), 0);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.expenses.title}</h1>
          <p className="text-slate-500 mt-1">{ARABIC.expenses.subtitle}</p>
        </div>
        <button 
          onClick={handleAddExpense}
          className="flex items-center px-4 py-2.5 bg-primary text-white font-medium rounded-xl hover:bg-blue-600 transition-all shadow-sm shadow-blue-200"
        >
          <svg className="w-5 h-5 ms-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
          {ARABIC.expenses.addExpense}
        </button>
      </div>

      <div className="glass p-6 rounded-2xl border border-slate-200/50">
        <div className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-2">{ARABIC.expenses.amount}</div>
        <div className="text-3xl font-bold text-slate-800">{formatCurrency(totalExpenses.toString())}</div>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl mb-4 border border-rose-200 animate-slide-up flex items-center shadow-sm">
          <svg className="w-5 h-5 ms-3 text-rose-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
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
        ) : expenses.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-start border-collapse animate-fade-in">
              <thead>
                <tr className="bg-slate-50/50 border-b border-slate-200">
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.expenses.description}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.expenses.category}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.expenses.amount}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.expenses.date}</th>
                  <th className="px-6 py-4 text-end text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.common.actions}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white/50">
                {expenses.map((expense) => (
                  <tr key={expense.id} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="px-6 py-4">
                      <div className="font-medium text-slate-800">{expense.description}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-800">
                        {expense.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-end font-medium text-slate-800">{formatCurrency(expense.amount)}</td>
                    <td className="px-6 py-4 text-slate-600">{formatDate(expense.date)}</td>
                    <td className="px-6 py-4 text-end opacity-0 group-hover:opacity-100 transition-opacity">
                      <div className="flex justify-end gap-1">
                        <button
                          onClick={() => handleEditExpense(expense)}
                          className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                          title={ARABIC.expenses.editExpense}
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                        </button>
                        <button
                          onClick={() => handleDelete(expense.id)}
                          className="p-2 text-rose-500 hover:bg-rose-50 rounded-lg transition-colors"
                          title={ARABIC.expenses.deleteExpense}
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-24 text-slate-400 animate-fade-in">
            <svg className="w-16 h-16 mb-4 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9 14l6-6m-5 .5a.5.5 0 11-1 0 .5.5 0 011 0zm6.5 6a.5.5 0 11-1 0 .5.5 0 011 0zM6 18L18 6M6 6l12 12"></path></svg>
            <div className="text-lg font-medium text-slate-600 mb-1">{ARABIC.expenses.noExpenses}</div>
          </div>
        )}
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
          <div 
            className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity animate-in fade-in duration-300"
            onClick={() => setIsModalOpen(false)}
          />
          
          <div className="relative w-full max-w-md bg-white/90 backdrop-blur-md rounded-3xl shadow-2xl border border-white/20 overflow-hidden animate-in zoom-in-95 fade-in duration-300">
            <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-white/50">
              <div>
                <h2 className="text-2xl font-bold text-slate-800 tracking-tight">
                  {editingExpense ? ARABIC.expenses.editExpense : ARABIC.expenses.addExpense}
                </h2>
              </div>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400 hover:text-slate-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <form onSubmit={handleSaveExpense} className="p-8 space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-700">{ARABIC.expenses.description}</label>
                <input
                  type="text"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
                  dir="rtl"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-slate-700">{ARABIC.expenses.amount}</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  value={formData.amount}
                  onChange={(e) => setFormData({ ...formData, amount: e.target.value })}
                  className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none text-end"
                  dir="ltr"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-slate-700">{ARABIC.expenses.category}</label>
                <input
                  type="text"
                  value={formData.category}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
                  dir="rtl"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-slate-700">{ARABIC.expenses.date}</label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
                  dir="ltr"
                  required
                />
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-slate-200 rounded-xl hover:bg-slate-50 text-slate-600"
                >
                  {ARABIC.common.cancel}
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary text-white rounded-xl hover:bg-primary-dark"
                >
                  {ARABIC.common.save}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}