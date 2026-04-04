/**
 * ReversalModal Component
 * 
 * Modal for entering reversal reason and confirming sale reversal.
 * Task: T090
 */

"use client";

import { useState } from "react";

interface ReversalModalProps {
  saleId: string | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (saleId: string, reason: string) => Promise<void>;
}

export default function ReversalModal({ saleId, isOpen, onClose, onConfirm }: ReversalModalProps) {
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen || !saleId) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!reason.trim()) {
      setError("Reason is required");
      return;
    }

    try {
      setLoading(true);
      setError("");
      await onConfirm(saleId, reason);
      setReason("");
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to reverse sale");
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setReason("");
    setError("");
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h2 className="text-xl font-bold mb-4">Reverse Sale</h2>

        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-800">
            <strong>Warning:</strong> This will reverse the sale and restore all items to inventory.
            This action cannot be undone.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">
              Reason for Reversal <span className="text-red-600">*</span>
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="border rounded px-3 py-2 w-full"
              rows={3}
              placeholder="Enter the reason for reversing this sale..."
              required
            />
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-red-700 text-sm">
              {error}
            </div>
          )}

          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 border rounded hover:bg-gray-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              disabled={loading || !reason.trim()}
            >
              {loading ? "Reversing..." : "Confirm Reversal"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}