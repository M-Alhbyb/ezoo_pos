import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";

interface SupplierData {
  name: string;
  phone: string;
  notes: string;
}

interface SupplierModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: SupplierData) => Promise<void>;
}

export default function SupplierModal({ isOpen, onClose, onSubmit }: SupplierModalProps) {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      setName("");
      setPhone("");
      setNotes("");
      setError("");
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      await onSubmit({ name, phone, notes });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in text-start">
      <div className="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl animate-scale-up">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <h2 className="text-xl font-semibold text-slate-800">{ARABIC.suppliers.addSupplier}</h2>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="mb-6 p-3 bg-rose-50 text-rose-700 rounded-xl text-sm border border-rose-200 flex items-center">
              <svg className="w-4 h-4 me-2" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
              {error}
            </div>
          )}

          <div className="space-y-5 text-start">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">{ARABIC.suppliers.supplierName}</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-medium text-slate-800"
                placeholder="اسم الشركة أو المورد"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">{ARABIC.suppliers.phone}</label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-medium text-slate-800"
                placeholder="0123456789"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">{ARABIC.suppliers.notes}</label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-medium text-slate-800 h-24"
                placeholder="أي ملاحظات إضافية..."
              />
            </div>
          </div>

          <div className="mt-8 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-xl transition-colors"
            >
              {ARABIC.common.cancel}
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 bg-primary text-white text-sm font-medium rounded-xl hover:bg-blue-600 transition-all shadow-sm shadow-blue-200 flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? ARABIC.common.saving : ARABIC.suppliers.addSupplier}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
