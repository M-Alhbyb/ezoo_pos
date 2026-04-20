/**
 * FeeEditor Component
 * 
 * Add/edit fixed or percentage fees to the sale.
 * Task: T072
 */

"use client";

import { useState } from "react";

interface Fee {
  fee_type: "shipping" | "installation" | "custom";
  fee_label: string;
  fee_value_type: "fixed" | "percent";
  fee_value: number;
}

interface FeeEditorProps {
  fees: Fee[];
  onFeesChange: (fees: Fee[]) => void;
}

const FEE_TYPES = [
  { value: "shipping", label: "Shipping" },
  { value: "installation", label: "Installation" },
  { value: "custom", label: "Custom" },
] as const;

export default function FeeEditor({ fees, onFeesChange }: FeeEditorProps) {
  const [showForm, setShowForm] = useState(false);
  const [newFee, setNewFee] = useState<Fee>({
    fee_type: "shipping",
    fee_label: "",
    fee_value_type: "fixed",
    fee_value: 0,
  });

  const handleAddFee = () => {
    if (newFee.fee_label && newFee.fee_value > 0) {
      onFeesChange([...fees, newFee]);
      setNewFee({
        fee_type: "shipping",
        fee_label: "",
        fee_value_type: "fixed",
        fee_value: 0,
      });
      setShowForm(false);
    }
  };

  const handleRemoveFee = (index: number) => {
    const newFees = fees.filter((_, i) => i !== index);
    onFeesChange(newFees);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="font-medium">Additional Fees</h3>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            className="text-blue-600 hover:text-blue-800 text-sm"
          >
            + Add Fee
          </button>
        )}
      </div>

      {fees.length > 0 && (
        <div className="space-y-2">
          {fees.map((fee, index) => (
            <div key={index} className="flex justify-between items-center border rounded p-3">
              <div>
                <div className="font-medium">{fee.fee_label}</div>
                <div className="text-sm text-gray-500">
                  {fee.fee_value_type === "percent" ? `${fee.fee_value}% of subtotal` : `$${fee.fee_value.toFixed(2)} fixed`}
                </div>
              </div>
              <button
                onClick={() => handleRemoveFee(index)}
                className="text-red-600 hover:text-red-800 text-sm"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <div className="border rounded p-4 space-y-3">
          <div>
            <label className="block text-sm font-medium mb-1">Fee Type</label>
            <select
              value={newFee.fee_type}
              onChange={(e) => setNewFee({ ...newFee, fee_type: e.target.value as any })}
              className="border rounded px-3 py-2 w-full"
            >
              {FEE_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Label</label>
            <input
              type="text"
              value={newFee.fee_label}
              onChange={(e) => setNewFee({ ...newFee, fee_label: e.target.value })}
              placeholder="e.g., Express Shipping"
              className="border rounded px-3 py-2 w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">Value Type</label>
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="fee_value_type"
                  value="fixed"
                  checked={newFee.fee_value_type === "fixed"}
                  onChange={(e) => setNewFee({ ...newFee, fee_value_type: "fixed" })}
                  className="mr-2"
                />
                Fixed Amount ($)
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="fee_value_type"
                  value="percent"
                  checked={newFee.fee_value_type === "percent"}
                  onChange={(e) => setNewFee({ ...newFee, fee_value_type: "percent" })}
                  className="mr-2"
                />
                Percentage (%)
              </label>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-1">
              {newFee.fee_value_type === "fixed" ? "Amount ($)" : "Percentage (%)"}
            </label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={newFee.fee_value}
              onChange={(e) => setNewFee({ ...newFee, fee_value: parseFloat(e.target.value) || 0 })}
              className="border rounded px-3 py-2 w-full"
            />
          </div>

          <div className="flex justify-end space-x-2">
            <button
              onClick={() => setShowForm(false)}
              className="px-4 py-2 border rounded hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleAddFee}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Add Fee
            </button>
          </div>
        </div>
      )}
    </div>
  );
}