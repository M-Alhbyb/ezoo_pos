'use client';

import React, { ReactNode } from 'react';
import { DatePicker } from './DatePicker';
import { ExportButton } from './ExportButton';
import { ExportFormat } from '../../lib/utils/export-utils';

export interface DashboardLayoutProps {
  title: string;
  description?: string;
  dashboardType?: 'sales' | 'projects' | 'partners' | 'inventory';
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
  children: ReactNode;
  loading?: boolean;
  error?: string | null;
  showExport?: boolean;
}

export function DashboardLayout({
  title,
  description,
  dashboardType,
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  children,
  loading = false,
  error = null,
  showExport = true
}: DashboardLayoutProps) {
  const handleExportStart = (format: ExportFormat) => {
    console.log(`Starting ${format} export...`);
  };

  const handleExportComplete = () => {
    console.log('Export completed successfully');
  };

  const handleExportError = (error: string) => {
    console.error('Export error:', error);
  };

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">{title}</h1>
        {description && (
          <p className="text-gray-600">{description}</p>
        )}
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex-1">
            <h2 className="text-lg font-semibold text-gray-900 mb-3">Filter by Date Range</h2>
            <DatePicker
              startDate={startDate}
              endDate={endDate}
              onStartDateChange={onStartDateChange}
              onEndDateChange={onEndDateChange}
              disabled={loading}
            />
          </div>
          
          {showExport && dashboardType && (
            <div className="flex-shrink-0">
              <ExportButton
                dashboardType={dashboardType}
                startDate={startDate}
                endDate={endDate}
                onExportStart={handleExportStart}
                onExportComplete={handleExportComplete}
                onExportError={handleExportError}
                disabled={loading}
              />
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex">
            <svg className="w-5 h-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error loading data</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard data...</p>
          </div>
        </div>
      )}

      {!loading && !error && children}
    </div>
  );
}