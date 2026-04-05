"use client";

import { useState, useEffect } from "react";

// T037: TypeScript props interface for FeePresetManager
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
  { value: "shipping", label: "Shipping" },
  { value: "installation", label: "Installation" },
  { value: "custom", label: "Custom" },
] as const;

// T036: FeePresetManager component for settings page
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

  // T038: fetchPresets async function to load presets via API
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

  // T040: Fee type selector handler
  const handleFeeTypeChange = (feeType: "shipping" | "installation" | "custom") => {
    setSelectedFeeType(feeType);
    setEditPresets(presets[feeType] || []);
    setError("");
  };

  // T041: Preset input UI handlers
  const handlePresetChange = (index: number, value: string) => {
    const numValue = parseFloat(value) || 0;
    const newPresets = [...editPresets];
    newPresets[index] = numValue;
    setEditPresets(newPresets);
  };

  const handleAddPreset = () => {
    if (editPresets.length >= 8) {
      setError("Maximum 8 presets allowed per fee type");
      return;
    }
    setEditPresets([...editPresets, 0]);
  };

  const handleRemovePreset = (index: number) => {
    const newPresets = editPresets.filter((_, i) => i !== index);
    setEditPresets(newPresets);
  };

  // T042: Validation UI
  const validatePresets = (): string | null => {
    if (editPresets.length > 8) {
      return "Maximum 8 presets allowed";
    }
    if (editPresets.some(p => p < 0)) {
      return "Preset amounts must be non-negative";
    }
    return null;
  };

  // T043: savePresets async function to POST to API
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
      
      // Filter out zero values and deduplicate
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
        throw new Error(data.detail || "Failed to save presets");
      }

      // Update local state
      setPresets(prev => ({
        ...prev,
        [selectedFeeType]: sortedPresets,
      }));
      setEditPresets(sortedPresets);
      
      // Notify parent
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
        <h2 className="text-lg font-medium mb-2">Fee Presets</h2>
        <p className="text-sm text-gray-600 mb-4">
          Configure quick-amount buttons for each fee type. Maximum 8 presets per fee type.
        </p>
      </div>

      {/* T040: Fee type selector (tabs) */}
      <div className="flex space-x-2 border-b">
        {FEE_TYPES.map((type) => (
          <button
            key={type.value}
            onClick={() => handleFeeTypeChange(type.value)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              selectedFeeType === type.value
                ? "border-b-2 border-blue-600 text-blue-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {type.label}
          </button>
        ))}
      </div>

      {/* Error message */}
      {error && (
        <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded">
          {error}
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-4">
        {/* T041: Preset inputs */}
        <div>
          <label className="block text-sm font-medium mb-2">
            Preset Amounts for {FEE_TYPES.find(t => t.value === selectedFeeType)?.label}
          </label>
          <div className="space-y-2">
            {editPresets.map((preset, index) => (
              <div key={index} className="flex items-center space-x-2">
                <input
                  type="number"
                  min="0"
                  step="0.01"
                  value={preset || ""}
                  onChange={(e) => handlePresetChange(index, e.target.value)}
                  className="border rounded px-3 py-2 w-32"
                  placeholder="Amount"
                />
                <button
                  type="button"
                  onClick={() => handleRemovePreset(index)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Add preset button */}
        {editPresets.length < 8 && (
          <button
            type="button"
            onClick={handleAddPreset}
            className="px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 text-sm"
          >
            + Add Preset
          </button>
        )}

        {/* T044: Save button with loading indicator */}
        <div className="flex items-center space-x-3">
          <button
            type="submit"
            disabled={saving}
            className={`px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm ${
              saving ? "opacity-50 cursor-not-allowed" : ""
            }`}
          >
            {saving ? "Saving..." : "Save Presets"}
          </button>
          
          {/* Success feedback after save */}
          {saving === false && editPresets.length > 0 && presets[selectedFeeType]?.length > 0 && (
            <span className="text-sm text-green-600">
              Presets saved successfully
            </span>
          )}
        </div>
      </form>

      {/* Current saved presets preview */}
      <div className="mt-6 p-4 bg-gray-50 rounded">
        <h3 className="text-sm font-medium mb-2">Current Presets</h3>
        <div className="flex flex-wrap gap-2">
          {editPresets
            .filter(p => p > 0)
            .sort((a, b) => a - b)
            .map((preset, index) => (
              <span
                key={index}
                className="px-3 py-1 bg-white border rounded text-sm"
              >
                ${preset.toFixed(2)}
              </span>
            ))}
          {editPresets.filter(p => p > 0).length === 0 && (
            <span className="text-sm text-gray-500 italic">
              No presets configured
            </span>
          )}
        </div>
      </div>
    </div>
  );
}