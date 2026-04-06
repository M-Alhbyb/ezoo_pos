'use client';

import React, { useState } from 'react';
import { FileText, Download } from 'lucide-react';
import { ExportFormat } from '../../lib/utils/export-utils';

export interface ExportPDFButtonProps {
  reportType: 'sales' | 'projects' | 'partners' | 'inventory';
  startDate: string;
  endDate: string;
  onExportStart?: () => void;
  onExportComplete?: () => void;
  onExportError?: (error: string) => void;
  disabled?: boolean;
}

export function ExportPDFButton({
  reportType,
  startDate,
  endDate,
  onExportStart,
  onExportComplete,
  onExportError,
  disabled = false
}: ExportPDFButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    if (!startDate || !endDate) {
      onExportError?.('Please select a date range');
      return;
    }

    setIsExporting(true);
    onExportStart?.();

    try {
      const params = new URLSearchParams({
        format: 'pdf',
        start_date: startDate,
        end_date: endDate
      });

      const response = await fetch(`/api/reports/${reportType}/export?${params}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/pdf'
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Export failed');
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `${reportType}_report_${startDate}_${endDate}.pdf`;

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="(.+)"/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1];
        }
      }

      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

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
      className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
    >
      {isExporting ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          <span>Exporting...</span>
        </>
      ) : (
        <>
          <FileText className="w-4 h-4" />
          <span>Export as PDF</span>
        </>
      )}
    </button>
  );
}