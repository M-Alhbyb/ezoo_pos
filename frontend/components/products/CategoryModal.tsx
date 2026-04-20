"use client";

import { useEffect, useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";

interface Category {
  id?: string;
  name: string;
  color?: string | null;
}

interface CategoryModalProps {
  category?: Category;
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; color: string | null }) => Promise<void>;
}

export default function CategoryModal({
  category,
  isOpen,
  onClose,
  onSubmit,
}: CategoryModalProps) {
  const [name, setName] = useState(category?.name || "");
  const [color, setColor] = useState<string | null>(category?.color || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (isOpen) {
      setName(category?.name || "");
      setColor(category?.color || null);
      setError("");
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen, category]);

  if (!isOpen || !mounted) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError(ARABIC.forms.required);
      return;
    }

    try {
      setLoading(true);
      setError("");
      await onSubmit({ name, color });
      onClose();
    } catch (err: any) {
      setError(err.message || ARABIC.errors.saveFailed);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 sm:p-6">
      <div 
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity animate-in fade-in duration-300"
        onClick={onClose}
      />
      
      <div className="relative w-full max-w-md bg-white/90 backdrop-blur-md rounded-3xl shadow-2xl border border-white/20 overflow-hidden animate-in zoom-in-95 fade-in duration-300">
        <div className="px-8 py-6 border-b border-slate-100 flex justify-between items-center bg-white/50">
          <div>
            <h2 className="text-2xl font-bold text-slate-800 tracking-tight">
              {category ? ARABIC.categories.editCategory : ARABIC.categories.addCategory}
            </h2>
            <p className="text-slate-500 text-sm mt-0.5">
              {category ? ARABIC.common.updateDetails : ARABIC.common.createNew}
            </p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400 hover:text-slate-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="p-8 space-y-6">
          {error && (
            <div className="p-3 rounded-xl bg-rose-50 border border-rose-100 text-rose-600 text-sm font-medium animate-shake">
              {error}
            </div>
          )}
          
          <div className="space-y-2">
            <label className="text-sm font-semibold text-slate-700 block ms-1">
              {ARABIC.categories.categoryName} <span className="text-rose-500">*</span>
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={ARABIC.categories.categoryName}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all outline-none text-slate-800 placeholder-slate-400 font-medium"
              required
              autoFocus
              dir="rtl"
            />
          </div>
          
          <div className="space-y-3">
            <label className="text-sm font-semibold text-slate-700 block ms-1">
              {ARABIC.categories.categoryColor}
            </label>
            <div className="grid grid-cols-5 gap-3">
              {[
                { name: "Blue", bg: "bg-blue-50/60", hex: "bg-blue-50/60" },
                { name: "Emerald", bg: "bg-emerald-50/60", hex: "bg-emerald-50/60" },
                { name: "Amber", bg: "bg-amber-50/60", hex: "bg-amber-50/60" },
                { name: "Rose", bg: "bg-rose-50/60", hex: "bg-rose-50/60" },
                { name: "Indigo", bg: "bg-indigo-50/60", hex: "bg-indigo-50/60" },
                { name: "Cyan", bg: "bg-cyan-50/60", hex: "bg-cyan-50/60" },
                { name: "Orange", bg: "bg-orange-50/60", hex: "bg-orange-50/60" },
                { name: "Teal", bg: "bg-teal-50/60", hex: "bg-teal-50/60" },
                { name: "Fuchsia", bg: "bg-fuchsia-50/60", hex: "bg-fuchsia-50/60" },
                { name: "Slate", bg: "bg-slate-100/50", hex: "bg-slate-100/50" },
              ].map((c) => (
                <button
                  key={c.hex}
                  type="button"
                  onClick={() => setColor(c.bg)}
                  className={`h-10 rounded-xl ${c.bg} border-2 transition-all flex items-center justify-center ${
                    color === c.bg ? "border-indigo-500 scale-110 shadow-sm" : "border-transparent hover:scale-105"
                  }`}
                  title={c.name}
                >
                  {color === c.bg && (
                    <div className="w-2 h-2 rounded-full bg-indigo-500" />
                  )}
                </button>
              ))}
              <button
                type="button"
                onClick={() => setColor(null)}
                className={`h-10 rounded-xl bg-white border-2 transition-all text-[10px] font-bold text-slate-400 ${
                  color === null ? "border-indigo-500 scale-110 shadow-sm" : "border-slate-100 hover:border-slate-200"
                }`}
              >
                Auto
              </button>
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-6 py-3 border border-slate-200 text-slate-600 font-semibold rounded-xl hover:bg-slate-50 transition-all"
            >
              {ARABIC.common.cancel}
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading && (
                <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              )}
              {category ? ARABIC.common.update : ARABIC.common.save}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
