"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";

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

  const handlePresetChange = (index: number, value: string) => {
    const numValue = parseFloat(value) || 0;
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
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-medium mb-2">{ARABIC.settings.feePresets}</h2>
        <p className="text-sm text-gray-600 mb-4">
          {ARABIC.settings.feePresetsDescription}
        </p>
      </div>

      <div className="flex gap-2 border-b">
        {FEE_TYPES.map((type) => (
          <button
            key={type.value}
            onClick={() => handleFeeTypeChange(type.value)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              selectedFeeType === type.value
                ? "border-b-2 border-primary text-primary"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {type.label}
          </button>
        ))}
      </div>

      {error && (
        <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            {ARABIC.settings.presetAmounts} {FEE_TYPES.find(t => t.value === selectedFeeType)?.label}
          </label>
          <div className="space-y-2">
            {editPresets.map((preset, index) => (
              <div key={index} className="flex items-center gap-2">
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={preset || ""}
                  onChange={(e) => handlePresetChange(index, e.target.value)}
                  className="border rounded px-3 py-2 w-32 text-end"
                  placeholder={ARABIC.expenses.amount}
                  dir="ltr"
                />
                <button
                  type="button"
                  onClick={() => handleRemovePreset(index)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  {ARABIC.common.delete}
                </button>
              </div>
            ))}
          </div>
        </div>

        {editPresets.length < 8 && (
          <button
            type="button"
            onClick={handleAddPreset}
            className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 text-sm"
          >
            + {ARABIC.settings.addPreset}
          </button>
        )}

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={saving}
            className={`px-4 py-2 bg-primary text-white rounded hover:bg-primary-dark text-sm ${
              saving ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {saving ? ARABIC.common.saving : ARABIC.common.save}
          </button>
          
          {saving === false && editPresets.length > 0 && presets[selectedFeeType]?.length > 0 && (
            <span className="text-sm text-green-600">
              {ARABIC.common.success}
            </span>
          )}
        </div>
      </form>

      <div className="mt-6 p-4 bg-gray-50 rounded">
        <h3 className="text-sm font-medium mb-2">{ARABIC.settings.currentPresets}</h3>
        <div className="flex flex-wrap gap-2">
          {editPresets
            .filter(p => p > 0)
            .sort((a, b) => a - b)
            .map((preset, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-white border rounded text-sm"
              >
                {formatCurrency(preset.toString())}
              </span>
            ))}
          {editPresets.filter(p => p > 0).length === 0 && (
            <span className="text-sm text-gray-500 italic">
              {ARABIC.settings.noPresets}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}