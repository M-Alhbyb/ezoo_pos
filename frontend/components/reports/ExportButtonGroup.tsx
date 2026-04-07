'use client';

import React, { useState } from 'react';
import { FileText, FileSpreadsheet, FileDown } from 'lucide-react';
import { ARABIC } from '@/lib/constants/arabic';

export interface ExportButtonGroupProps {
  reportType: 'sales' | 'projects' | 'partners' | 'inventory';
  startDate: string;
  endDate: string;
  onExportStart?: () => void;
  onExportComplete?: () => void;
  onExportError?: (error: string) => void;
  disabled?: boolean;
}

export function ExportButtonGroup({
  reportType,
  startDate,
  endDate,
  onExportStart,
  onExportComplete,
  onExportError,
  disabled = false
}: ExportButtonGroupProps) {
  const [exportingFormat, setExportingFormat] = useState<string | null>(null);

  const handleExport = async (format: 'pdf' | 'csv' | 'xlsx') => {
    if (!startDate || !endDate) {
      onExportError?.(ARABIC.reports.selectDateRange || 'اختر نطاق التاريخ');
      return;
    }

    setExportingFormat(format);
    onExportStart?.();

    try {
      const params = new URLSearchParams({
        format: format,
        start_date: startDate,
        end_date: endDate
      });

      const acceptHeader = format === 'pdf' ? 'application/pdf' :
                           format === 'csv' ? 'text/csv' :
                           'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';

      const response = await fetch(`/api/reports/${reportType}/export?${params}`, {
        method: 'GET',
        headers: {
          'Accept': acceptHeader
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || ARABIC.reports.export.exportFailed);
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get('content-disposition');
      
      let extension = format === 'xlsx' ? 'xlsx' : format;
      let filename = `${reportType}_report_${startDate}_${endDate}.${extension}`;

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
      const errorMessage = error instanceof Error ? error.message : ARABIC.common.error;
      onExportError?.(errorMessage);
    } finally {
      setExportingFormat(null);
    }
  };

  return (
    <div className="flex flex-wrap gap-3">
      <button
        onClick={() => handleExport('csv')}
        disabled={disabled || exportingFormat !== null}
        className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white font-medium rounded-xl hover:bg-emerald-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors shadow-sm shadow-emerald-200"
      >
        {exportingFormat === 'csv' ? (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
        ) : (
          <FileDown className="w-4 h-4" />
        )}
        <span>{ARABIC.reports.export.csv}</span>
      </button>

      <button
        onClick={() => handleExport('xlsx')}
        disabled={disabled || exportingFormat !== null}
        className="flex items-center gap-2 px-4 py-2 bg-green-700 text-white font-medium rounded-xl hover:bg-green-800 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors shadow-sm shadow-green-300"
      >
        {exportingFormat === 'xlsx' ? (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
        ) : (
          <FileSpreadsheet className="w-4 h-4" />
        )}
        <span>{ARABIC.reports.export.excel}</span>
      </button>
      
      <button
        onClick={() => handleExport('pdf')}
        disabled={disabled || exportingFormat !== null}
        className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white font-medium rounded-xl hover:bg-red-700 disabled:bg-slate-300 disabled:cursor-not-allowed transition-colors shadow-sm shadow-red-200"
      >
        {exportingFormat === 'pdf' ? (
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
        ) : (
          <FileText className="w-4 h-4" />
        )}
        <span>{ARABIC.reports.export.pdf}</span>
      </button>
    </div>
  );
}
