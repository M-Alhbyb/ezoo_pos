"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";
import NumberInput from "@/components/shared/NumberInput";

interface FeePresetManagerProps {
  locationId?: number;
  onChange?: () => void;
}

interface PresetsByFeeType {
  shipping: number[];
  installation: number[];
  custom: number[];
}

const FEE_TYPES = [
  { value: "shipping", label: ARABIC.pos.shipping },
  { value: "installation", label: ARABIC.pos.installation },
  { value: "custom", label: ARABIC.pos.custom },
] as const;

export default function FeePresetManager({ 
  locationId = 1, 
  onChange 
}: FeePresetManagerProps) {
  const [presets, setPresets] = useState<PresetsByFeeType>({
    shipping: [],
    installation: [],
    custom: [],
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [selectedFeeType, setSelectedFeeType] = useState<"shipping" | "installation" | "custom">("shipping");
  const [editPresets, setEditPresets] = useState<number[]>([]);

  useEffect(() => {
    fetchPresets();
  }, [locationId]);

  const fetchPresets = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/settings/fee-presets?location_id=${locationId}`);
      if (!response.ok) throw new Error("Failed to fetch fee presets");
      const data = await response.json();
      setPresets(data.presets_by_fee_type);
      setEditPresets(data.presets_by_fee_type[selectedFeeType] || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFeeTypeChange = (feeType: "shipping" | "installation" | "custom") => {
    setSelectedFeeType(feeType);
    setEditPresets(presets[feeType] || []);
    setError("");
  };

  const handlePresetChange = (index: number, numValue: number) => {
    const newPresets = [...editPresets];
    newPresets[index] = numValue;
    setEditPresets(newPresets);
  };

  const handleAddPreset = () => {
    if (editPresets.length >= 8) {
      setError(ARABIC.common.error);
      return;
    }
    setEditPresets([...editPresets, 0]);
  };

  const handleRemovePreset = (index: number) => {
    const newPresets = editPresets.filter((_, i) => i !== index);
    setEditPresets(newPresets);
  };

  const validatePresets = (): string | null => {
    if (editPresets.length > 8) {
      return ARABIC.common.error;
    }
    if (editPresets.some(p => p < 0)) {
      return ARABIC.common.error;
    }
    return null;
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validationError = validatePresets();
    if (validationError) {
      setError(validationError);
      return;
    }

    try {
      setSaving(true);
      setError("");
      
      const uniquePresets = Array.from(new Set(editPresets.filter(p => p > 0)));
      const sortedPresets = uniquePresets.sort((a, b) => a - b);
      
      const response = await fetch("/api/settings/fee-presets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          location_id: locationId,
          fee_type: selectedFeeType,
          presets: sortedPresets,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || ARABIC.common.error);
      }

      setPresets(prev => ({
        ...prev,
        [selectedFeeType]: sortedPresets,
      }));
      setEditPresets(sortedPresets);
      
      if (onChange) {
        onChange();
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-4">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-full mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 text-start">
      <div>
        <h2 className="text-lg font-bold text-slate-800 mb-2">{ARABIC.settings.feePresets}</h2>
        <p className="text-sm text-slate-500 mb-4">
          {ARABIC.settings.feePresetsDescription}
        </p>
      </div>

      <div className="flex gap-2 border-b border-slate-100">
        {FEE_TYPES.map((type) => (
          <button
            key={type.value}
            onClick={() => handleFeeTypeChange(type.value)}
            className={`px-4 py-3 text-sm font-bold transition-all relative ${
              selectedFeeType === type.value
                ? "text-blue-600 after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-blue-600"
                : "text-slate-400 hover:text-slate-600"
            }`}
          >
            {type.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="p-3 text-sm text-rose-600 bg-rose-50 border border-rose-100 rounded-xl">
          {error}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-4">
        <div>
          <label className="block text-xs font-bold text-slate-400 uppercase mb-3">
            {ARABIC.settings.presetAmounts} {FEE_TYPES.find(t => t.value === selectedFeeType)?.label}
          </label>
          <div className="space-y-3">
            {editPresets.map((preset, index) => (
              <div key={index} className="flex items-center gap-3 bg-slate-50 p-2 rounded-2xl border border-slate-100 w-fit">
                <NumberInput
                  value={preset}
                  onChange={(val) => handlePresetChange(index, val)}
                  className="w-32 py-1.5 rounded-lg text-sm"
                  containerClassName="w-32"
                />
                <button
                  type="button"
                  onClick={() => handleRemovePreset(index)}
                  className="p-2 text-rose-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                </button>
              </div>
            ))}
          </div>
        </div>

        {editPresets.length < 8 && (
          <button
            type="button"
            onClick={handleAddPreset}
            className="flex items-center gap-2 px-4 py-2 border-2 border-dashed border-slate-200 rounded-xl hover:border-blue-300 hover:text-blue-600 text-slate-400 text-sm font-bold transition-all"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
            {ARABIC.settings.addPreset}
          </button>
        )}

        <div className="flex items-center gap-4 pt-4 border-t border-slate-50">
          <button
            type="submit"
            disabled={saving}
            className="px-8 py-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 text-sm font-bold shadow-lg shadow-blue-100 disabled:opacity-50 transition-all"
          >
            {saving ? ARABIC.common.saving : ARABIC.common.save}
          </button>
          
          {saving === false && editPresets.length > 0 && presets[selectedFeeType]?.length > 0 && (
            <span className="text-sm font-bold text-emerald-600 flex items-center gap-1">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path></svg>
              {ARABIC.common.success}
            </span>
          )}
        </div>
      </form>

      <div className="p-5 bg-blue-50/30 border border-blue-100 rounded-2xl">
        <h3 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-3">{ARABIC.settings.currentPresets}</h3>
        <div className="flex flex-wrap gap-2">
          {editPresets
            .filter(p => p > 0)
            .sort((a, b) => a - b)
            .map((preset, index) => (
              <span
                key={index}
                className="px-4 py-1.5 bg-white border border-blue-100 rounded-lg text-sm font-bold text-blue-700 shadow-sm"
              >
                {formatCurrency(preset)}
              </span>
            ))}
          {editPresets.filter(p => p > 0).length === 0 && (
            <span className="text-sm text-slate-400 italic">
              {ARABIC.settings.noPresets}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}