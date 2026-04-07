"use client";

import { useState } from "react";
import PaymentMethodManager from "@/components/settings/PaymentMethodManager";
import SystemSettingsManager from "@/components/settings/SystemSettingsManager";
import FeePresetManager from "@/components/settings/FeePresetManager";
import { ARABIC } from "@/lib/constants/arabic";

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<"payment" | "presets" | "general">("payment");

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.settings.title}</h1>
        <p className="text-slate-500 mt-1">{ARABIC.settings.subtitle}</p>
      </div>

      <div className="flex gap-1 bg-slate-200/50 p-1 rounded-xl w-fit">
        <button
          onClick={() => setActiveTab("payment")}
          className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
            activeTab === "payment"
              ? "bg-white text-primary shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-white/50"
          }`}
        >
          {ARABIC.settings.paymentMethods}
        </button>
        
        <button
          onClick={() => setActiveTab("presets")}
          className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
            activeTab === "presets"
              ? "bg-white text-primary shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-white/50"
          }`}
        >
          {ARABIC.settings.feePresets}
        </button>
        
        <button
          onClick={() => setActiveTab("general")}
          className={`px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
            activeTab === "general"
              ? "bg-white text-primary shadow-sm"
              : "text-slate-600 hover:text-slate-900 hover:bg-white/50"
          }`}
        >
          {ARABIC.settings.systemSettings}
        </button>
      </div>

      <div className="mt-6">
        {activeTab === "payment" ? (
          <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            <PaymentMethodManager />
          </div>
        ) : activeTab === "presets" ? (
          <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            <FeePresetManager locationId={1} />
          </div>
        ) : (
          <div className="animate-in fade-in slide-in-from-bottom-2 duration-300">
            <SystemSettingsManager />
          </div>
        )}
      </div>
    </div>
  );
}
