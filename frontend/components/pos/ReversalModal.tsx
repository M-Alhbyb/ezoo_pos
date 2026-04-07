/**
 * ReversalModal Component
 * 
 * Modal for entering reversal reason and confirming sale reversal.
 * Task: T090
 */

"use client";

import { useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";

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
      setError(ARABIC.common.required || 'هذا الحقل مطلوب');
      return;
    }

    try {
      setLoading(true);
      setError("");
      await onConfirm(saleId, reason);
      setReason("");
      onClose();
    } catch (err: any) {
      setError(err.message || ARABIC.common.error || 'حدث خطأ');
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
        <h2 className="text-xl font-bold mb-4">{ARABIC.pos.reverseSale || 'إلغاء البيع'}</h2>

        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
          <p className="text-sm text-yellow-800">
            <strong>{ARABIC.common.warning || 'تحذير'}:</strong> {ARABIC.pos.reversalWarning || 'سيؤدي هذا إلى إلغاء البيع وإرجاع جميع العناصر إلى المخزون. لا يمكن التراجع عن هذا الإجراء.'}
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium mb-1">
              {ARABIC.pos.reversalReason || 'سبب الإلغاء'} <span className="text-red-600">*</span>
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="border rounded px-3 py-2 w-full"
              rows={3}
              placeholder={ARABIC.pos.enterReversalReason || 'أدخل سبب إلغاء هذا البيع...'}
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
              className="px-4 py-2 border rounded hover:bg-slate-50"
              disabled={loading}
            >
              {ARABIC.common.cancel || 'إلغاء'}
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
              disabled={loading || !reason.trim()}
            >
              {loading ? ARABIC.common.loading : ARABIC.pos.confirmReversal || 'تأكيد إلغاء البيع'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}