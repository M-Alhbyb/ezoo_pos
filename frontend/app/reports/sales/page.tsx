'use client';

import React, { useState, useEffect } from 'react';
import { Calendar, TrendingUp } from 'lucide-react';
import { ExportPDFButton } from '../../components/reports/ExportPDFButton';
import { ExportExcelButton } from '../../components/reports/ExportExcelButton';
import { ExportProgressModal } from '../../components/reports/ExportProgressModal';

export default function SalesReportPage() {
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [isExporting, setIsExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState(0);
  const [exportError, setExportError] = useState<string | null>(null);
  const [showProgress, setShowProgress] = useState(false);

  useEffect(() => {
    const today = new Date();
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    setStartDate(firstDayOfMonth.toISOString().split('T')[0]);
    setEndDate(today.toISOString().split('T')[0]);
  }, []);

  const handleExportStart = () => {
    setIsExporting(true);
    setShowProgress(true);
    setExportProgress(0);
    setExportError(null);
  };

  const handleExportComplete = () => {
    setIsExporting(false);
    setExportProgress(100);
    setTimeout(() => setShowProgress(false), 1000);
  };

  const handleExportError = (error: string) => {
    setExportError(error);
    setIsExporting(false);
    setShowProgress(false);
  };

  const handleCancelExport = () => {
    setIsExporting(false);
    setShowProgress(false);
    setExportProgress(0);
  };

  return (
    <div className="container mx-auto p-6" dir="rtl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">تقرير المبيعات</h1>
        <p className="text-gray-600">تصدير بيانات المبيعات بصيغة Excel أو PDF</p>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          اختيار النطاق الزمني
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">تاريخ البدء</label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">تاريخ الانتهاء</label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex gap-4">
          <ExportExcelButton
            reportType="sales"
            startDate={startDate}
            endDate={endDate}
            onExportStart={handleExportStart}
            onExportComplete={handleExportComplete}
            onExportError={handleExportError}
            disabled={!startDate || !endDate || isExporting}
          />
          
          <ExportPDFButton
            reportType="sales"
            startDate={startDate}
            endDate={endDate}
            onExportStart={handleExportStart}
            onExportComplete={handleExportComplete}
            onExportError={handleExportError}
            disabled={!startDate || !endDate || isExporting}
          />
        </div>

        {exportError && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{exportError}</p>
          </div>
        )}
      </div>

      <ExportProgressModal
        isOpen={showProgress}
        progress={exportProgress}
        onCancel={handleCancelExport}
      />

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">مميزات التصدير</h3>
        <ul className="text-blue-800 space-y-2">
          <li>• تصدير Excel متوافق مع كافة الأنظمة</li>
          <li>• معالجة النصوص العربية بشكل صحيح</li>
          <li>• تقارير PDF جاهزة للطباعة</li>
          <li>• الحد الأقصى: 50,000 سجل (Excel)، 10,000 سجل (PDF)</li>
        </ul>
      </div>
    </div>
  );
}