/**
 * ConfirmButton Component
 * 
 * Button to submit sale with validation.
 * Task: T075
 */

"use client";

interface ConfirmButtonProps {
  onConfirm: () => Promise<void>;
  disabled: boolean;
  loading: boolean;
}

export default function ConfirmButton({ onConfirm, disabled, loading }: ConfirmButtonProps) {
  const handleConfirm = async () => {
    if (disabled || loading) return;

    const confirmed = window.confirm(
      "Are you sure you want to complete this sale? This action cannot be undone."
    );

    if (confirmed) {
      await onConfirm();
    }
  };

  return (
    <button
      onClick={handleConfirm}
      disabled={disabled || loading}
      className={`
        w-full py-4 text-lg font-medium rounded
        ${disabled || loading
          ? "bg-gray-300 text-gray-500 cursor-not-allowed"
          : "bg-green-600 text-white hover:bg-green-700"
        }
      `}
    >
      {loading ? "Processing..." : "Confirm Sale"}
    </button>
  );
}