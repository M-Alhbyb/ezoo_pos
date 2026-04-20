'use client';

import React, { useState } from 'react';
import { FileSpreadsheet, Download } from 'lucide-react';
import { exportReport } from '../../lib/utils/export-utils';
import { ARABIC } from '../../lib/constants/arabic';

export interface ExportExcelButtonProps {
  reportType: 'sales' | 'projects' | 'partners' | 'inventory';
  startDate: string;
  endDate: string;
  onExportStart?: () => void;
  onExportComplete?: () => void;
  onExportError?: (error: string) => void;
  disabled?: boolean;
}

export function ExportExcelButton({
  reportType,
  startDate,
  endDate,
  onExportStart,
  onExportComplete,
  onExportError,
  disabled = false
}: ExportExcelButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    if (!startDate || !endDate) {
      onExportError?.(ARABIC.reports.selectDateRange);
      return;
    }

    setIsExporting(true);
    onExportStart?.();

    try {
      await exportReport(reportType, 'xlsx', startDate, endDate);
      onExportComplete?.();
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : ARABIC.common.error;
      onExportError?.(errorMessage);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={disabled || isExporting}
      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
    >
      {isExporting ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span>{ARABIC.reports.export.exporting}</span>
        </>
      ) : (
        <>
          <FileSpreadsheet className="w-4 h-4" />
          <span>{ARABIC.reports.export.excel}</span>
        </>
      )}
    </button>
  );
}