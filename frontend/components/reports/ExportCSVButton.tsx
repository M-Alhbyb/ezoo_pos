'use client';

import React, { useState } from 'react';
import { FileText, Download } from 'lucide-react';
import { exportReport } from '../../lib/utils/export-utils';

export interface ExportCSVButtonProps {
  reportType: 'sales' | 'projects' | 'partners' | 'inventory';
  startDate: string;
  endDate: string;
  onExportStart?: () => void;
  onExportComplete?: () => void;
  onExportError?: (error: string) => void;
  disabled?: boolean;
}

export function ExportCSVButton({
  reportType,
  startDate,
  endDate,
  onExportStart,
  onExportComplete,
  onExportError,
  disabled = false
}: ExportCSVButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    if (!startDate || !endDate) {
      onExportError?.('Please select a date range');
      return;
    }

    setIsExporting(true);
    onExportStart?.();

    try {
      await exportReport(reportType, 'csv', startDate, endDate);
      onExportComplete?.();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      onExportError?.(errorMessage);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={disabled || isExporting}
      className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
    >
      {isExporting ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span>Exporting...</span>
        </>
      ) : (
        <>
          <FileText className="w-4 h-4" />
          <span>Export as CSV</span>
        </>
      )}
    </button>
  );
}