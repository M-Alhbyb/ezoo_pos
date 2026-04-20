'use client';

import React from 'react';

interface ExportButtonProps {
  onClick?: () => void;
  disabled?: boolean;
  filename?: string;
  reportType?: string;
  startDate?: string;
  endDate?: string;
  onExportStart?: () => void;
  onExportComplete?: () => void;
  onExportError?: (error: string) => void;
}

export function ExportCSVButton({
  onClick,
  disabled,
  filename,
  reportType,
  startDate,
  endDate,
  onExportStart,
  onExportComplete,
  onExportError,
}: ExportButtonProps) {
  const handleClick = () => {
    if (onExportStart) onExportStart();
    if (onClick) onClick();
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled}
      className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
    >
      Export CSV
    </button>
  );
}