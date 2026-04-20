"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";

interface Setting {
  id: string;
  key: string;
  value: string;
  description: string;
}

export default function SystemSettingsManager() {
  const [settings, setSettings] = useState<Setting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/settings");
      if (!response.ok) throw new Error("Failed to fetch settings");
      const data = await response.json();
      setSettings(data.items);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (key: string, value: string) => {
    try {
      setSaving(key);
      const response = await fetch(`/api/settings/${key}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ value }),
      });

      if (!response.ok) throw new Error("Failed to update setting");
      
      setSettings(prev => prev.map(s => s.key === key ? { ...s, value } : s));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(null);
    }
  };

  if (loading && settings.length === 0) {
    return <div className="p-8 text-center text-slate-500">{ARABIC.common.loading}</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-slate-800">{ARABIC.settings.systemSettings}</h2>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-100 text-rose-600 rounded-xl text-sm flex items-center">
          <svg className="w-5 h-5 ms-3" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {settings.map((setting) => (
          <div key={setting.id} className="glass p-6 rounded-2xl border border-slate-200/50 hover:border-primary/20 transition-all group">
            <div className="flex justify-between items-start mb-2">
              <label className="text-sm font-bold text-slate-700 uppercase tracking-wider">{setting.key.replace(/_/g, ' ')}</label>
              {saving === setting.key && (
                <span className="text-[10px] text-primary flex items-center animate-pulse">
                  <svg className="w-3 h-3 ms-1 animate-spin" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  {ARABIC.common.saving}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500 mb-4">{setting.description}</p>
            
            {setting.key === "vat_enabled" ? (
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleUpdate(setting.key, setting.value === "true" ? "false" : "true")}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 focus:ring-offset-2 ${
                    setting.value === "true" ? "bg-primary" : "bg-slate-200"
                  }`}
                >
                  <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    setting.value === "true" ? "translate-x-6" : "translate-x-1"
                  }`} />
                </button>
                <span className="text-sm font-medium text-slate-600">{setting.value === "true" ? ARABIC.common.activate : ARABIC.common.deactivate}</span>
              </div>
            ) : setting.key === "vat_type" ? (
              <select
                value={setting.value}
                onChange={(e) => handleUpdate(setting.key, e.target.value)}
                className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
              >
                <option value="percent">{ARABIC.settings.vatRate}</option>
                <option value="fixed">{ARABIC.common.fixed}</option>
              </select>
            ) : (
              <input
                type="text"
                value={setting.value}
                onChange={(e) => setSettings(prev => prev.map(s => s.key === setting.key ? { ...s, value: e.target.value } : s))}
                onBlur={(e) => handleUpdate(setting.key, e.target.value)}
                className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none group-hover:bg-white"
                dir={setting.key.includes('name') || setting.key.includes('ar') ? 'rtl' : 'ltr'}
              />
            )}
          </div>
        ))}
      </div>
      {settings.length === 0 && (
        <div className="py-12 text-center text-slate-400 italic">{ARABIC.common.none}</div>
      )}
    </div>
  );
}
