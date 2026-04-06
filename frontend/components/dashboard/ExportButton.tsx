'use client';

import React, { useState } from 'react';
import { Download, FileText, FileSpreadsheet, File } from 'lucide-react';
import { ExportFormat } from '../../lib/utils/export-utils';

export interface ExportButtonProps {
  dashboardType: 'sales' | 'projects' | 'partners' | 'inventory';
  startDate: string;
  endDate: string;
  onExportStart?: (format: ExportFormat) => void;
  onExportComplete?: () => void;
  onExportError?: (error: string) => void;
  disabled?: boolean;
}

export function ExportButton({
  dashboardType,
  startDate,
  endDate,
  onExportStart,
  onExportComplete,
  onExportError,
  disabled = false
}: ExportButtonProps) {
  const [selectedFormat, setSelectedFormat] = useState<ExportFormat>('csv');
  const [isExporting, setIsExporting] = useState(false);

  const handleExport = async () => {
    if (!startDate || !endDate) {
      onExportError?.('Please select a date range');
      return;
    }

    setIsExporting(true);
    onExportStart?.(selectedFormat);

    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        export: selectedFormat
      });

      const response = await fetch(`/api/dashboard/${dashboardType}?${params}`, {
        method: 'GET',
        headers: {
          'Accept': selectedFormat === 'csv' 
            ? 'text/csv' 
            : selectedFormat === 'xlsx' 
              ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
              : 'application/pdf'
        }
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Export failed');
      }

      const blob = await response.blob();
      const contentDisposition = response.headers.get('content-disposition');
      let filename = `${dashboardType}_dashboard_${startDate}_${endDate}.${selectedFormat}`;

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

  const formatIcons = {
    csv: FileText,
    xlsx: FileSpreadsheet,
    pdf: File
  };

  const FormatIcon = formatIcons[selectedFormat];

  return (
    <div className="flex items-center gap-2">
      <select
        value={selectedFormat}
        onChange={(e) => setSelectedFormat(e.target.value as ExportFormat)}
        disabled={disabled || isExporting}
        className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
      >
        <option value="csv">CSV</option>
        <option value="xlsx">Excel</option>
        <option value="pdf">PDF</option>
      </select>

      <button
        onClick={handleExport}
        disabled={disabled || isExporting}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {isExporting ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Exporting...</span>
          </>
        ) : (
          <>
            <Download className="w-4 h-4" />
            <span>Export</span>
          </>
        )}
      </button>
    </div>
  );
}