'use client';

import React, { useState, useEffect } from 'react';
import { TrendingUp } from 'lucide-react';
import { LineChart, LineConfig } from '../../components/charts/LineChart';
import { DashboardLayout } from '../../components/dashboard/DashboardLayout';
import { QuickDateRanges } from '../../components/dashboard/DatePicker';
import { getSalesDashboard } from '../../lib/api/dashboard';
import { transformSalesChartData } from '../../lib/utils/chart-utils';
import { SalesChartData } from '../../lib/api/dashboard';

export default function SalesDashboardPage() {
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [chartData, setChartData] = useState<{ date: string; revenue: number; profit: number; vat: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalPoints, setTotalPoints] = useState<number>(0);

  useEffect(() => {
    const today = new Date();
    const firstDayOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
    setStartDate(firstDayOfMonth.toISOString().split('T')[0]);
    setEndDate(today.toISOString().split('T')[0]);
  }, []);

 useEffect(() => {
    if (startDate && endDate) {
      fetchDashboardData();
    }
  }, [startDate, endDate]);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getSalesDashboard(startDate, endDate);
      
      if (!response.success) {
        setError(response.error || 'Failed to load dashboard data');
        setChartData([]);
        return;
      }

      if (response.data) {
        const transformedData = transformSalesChartData(
          response.data.dates,
          response.data.revenue,
          response.data.profit,
          response.data.vat
        );
        setChartData(transformedData);
        setTotalPoints(response.total_points || 0);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      setChartData([]);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickRangeSelect = (start: string, end: string) => {
    setStartDate(start);
    setEndDate(end);
  };

  const lines: LineConfig[] = [
    { dataKey: 'revenue', color: '#8884d8', name: 'Revenue' },
    { dataKey: 'profit', color: '#82ca9d', name: 'Profit' },
    { dataKey: 'vat', color: '#ffc658', name: 'VAT' }
  ];

  return (
    <DashboardLayout
      title="Sales Dashboard"
      description="Interactive sales trends with daily revenue, profit, and VAT visualization"
      dashboardType="sales"
      startDate={startDate}
      endDate={endDate}
      onStartDateChange={setStartDate}
      onEndDateChange={setEndDate}
      loading={loading}
      error={error}
      showExport={true}
    >
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Quick Select</h3>
          <p className="text-sm text-gray-600 mt-1 mb-3">Choose a preset date range</p>
          <QuickDateRanges onRangeSelect={handleQuickRangeSelect} disabled={loading} />
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Sales Trends</h3>
          </div>
          {totalPoints > 0 && (
            <span className="text-sm text-gray-500">
              {totalPoints} data points
            </span>
          )}
        </div>

        <LineChart
          data={chartData}
          lines={lines}
          height={500}
          loading={loading}
          emptyMessage="No sales data available for the selected date range"
          showGrid={true}
          showLegend={true}
          isCurrency={true}
          decimalPlaces={4}
        />

        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Chart Features</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Hover over data points to see precise values(4 decimal places)</li>
            <li>• Click legend items to toggle line visibility</li>
            <li>• Maximum 1,000 data points per chart</li>
            <li>• Tooltips display exact monetary values</li>
          </ul>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
        <h4 className="text-sm font-semibold text-blue-900 mb-2">Data Accuracy</h4>
        <p className="text-sm text-blue-800">
          All monetary values are displayed with full decimal precision as stored in the database.
          No rounding or approximation is applied during aggregation or display.
        </p>
      </div>
    </DashboardLayout>
  );
}