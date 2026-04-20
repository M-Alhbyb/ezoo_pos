import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";

interface DistributeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { start_date?: string; end_date?: string; project_ids?: string[] }) => Promise<void>;
  loading: boolean;
}

export default function DistributeModal({ isOpen, onClose, onSubmit, loading }: DistributeModalProps) {
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (isOpen) {
      setStartDate("");
      setEndDate("");
      setError("");
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      const payload: any = {};
      if (startDate) payload.start_date = new Date(startDate).toISOString();
      if (endDate) payload.end_date = new Date(endDate).toISOString();
      
      await onSubmit(payload);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in">
      <div className="bg-white rounded-2xl w-full max-w-md overflow-hidden shadow-xl animate-scale-up">
        <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <h2 className="text-xl font-semibold text-slate-800">{ARABIC.partners.distributeProfits}</h2>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="mb-6 p-3 bg-rose-50 text-rose-700 rounded-xl text-sm border border-rose-200 flex items-center">
              <span className="font-medium">{error}</span>
            </div>
          )}
          
          <div className="mb-6 p-4 bg-indigo-50 border border-indigo-100 rounded-xl text-sm text-indigo-800">
            {ARABIC.partners.distributionNote || 'يتم إنشاء التوزيعات من المشاريع المكتملة غير الموزعة. يمكنك تصفية حسب نطاق التاريخ اختيارياً.'}
          </div>

          <div className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">{ARABIC.partners.startDate || 'من تاريخ'} ({ARABIC.common.optional || 'اختياري'})</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-medium text-slate-800"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">{ARABIC.partners.endDate || 'إلى تاريخ'} ({ARABIC.common.optional || 'اختياري'})</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all font-medium text-slate-800"
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
              className="px-5 py-2.5 bg-indigo-600 text-white text-sm font-medium rounded-xl hover:bg-indigo-700 transition-all shadow-sm shadow-indigo-200 flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? ARABIC.common.loading : ARABIC.partners.runDistribution || 'تشغيل التوزيع'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}