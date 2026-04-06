'use client';

import React, { useState, useEffect } from 'react';
import { Briefcase } from 'lucide-react';
import { BarChart } from '../../components/charts/BarChart';
import { DashboardLayout } from '../../components/dashboard/DashboardLayout';
import { QuickDateRanges } from '../../components/dashboard/DatePicker';
import { getProjectsDashboard } from '../../lib/api/dashboard';
import { transformProjectChartData } from '../../lib/utils/chart-utils';
import { ProjectChartData } from '../../lib/api/dashboard';

export default function ProjectsDashboardPage() {
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [chartData, setChartData] = useState<{ name: string; profit: number; margin: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalProfit, setTotalProfit] = useState<number>(0);
  const [avgMargin, setAvgMargin] = useState<number>(0);

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
      const response = await getProjectsDashboard(startDate, endDate);
      
      if (!response.success) {
        setError(response.error || 'Failed to load dashboard data');
        setChartData([]);
        return;
      }

      if (response.data) {
        const transformedData = transformProjectChartData(
          response.data.project_names,
          response.data.profits,
          response.data.profit_margins,
          response.data.project_ids
        );
        
        const barData = transformedData.map(item => ({
          name: item.name,
          profit: item.profit,
          margin: item.margin
        }));
        
        setChartData(barData);
        
        const total = transformedData.reduce((sum, item) => sum + item.profit, 0);
        const avgMarginValue = transformedData.reduce((sum, item) => sum + item.margin, 0) / transformedData.length;
        
        setTotalProfit(total);
        setAvgMargin(avgMarginValue);
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

  const bars = [
    { dataKey: 'profit', color: '#8884d8', name: 'Profit' }
  ];

  return (
    <DashboardLayout
      title="Projects Dashboard"
      description="Project profit distribution with margin comparison"
      dashboardType="projects"
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
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-purple-600" />
              <h4 className="text-sm font-medium text-purple-900">Total Profit</h4>
            </div>
            <p className="text-3xl font-bold text-purple-600 mt-2">
              ${totalProfit.toFixed(2)}
            </p>
          </div>
          
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="text-sm font-medium text-blue-900">Average Margin</h4>
            <p className="text-3xl font-bold text-blue-600 mt-2">
              {avgMargin.toFixed(2)}%
            </p>
          </div>
        </div>

        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Profit Distribution</h3>
          </div>
        </div>

        <BarChart
          data={chartData}
          bars={bars}
          height={450}
          loading={loading}
          emptyMessage="No project data available for the selected date range"
          showGrid={true}
          showLegend={false}
          isCurrency={true}
          decimalPlaces={2}
        />

        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Chart Features</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Hover over bars to see project name and profit amount</li>
            <li>• X-axis shows project names with angled labels for readability</li>
            <li>• Values displayed with full monetary precision</li>
            <li>• Click legend to toggle visibility (coming soon)</li>
          </ul>
        </div>
      </div>

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 mt-6">
        <h4 className="text-sm font-semibold text-purple-900 mb-2">Data Accuracy</h4>
        <p className="text-sm text-purple-800">
          Project profits are calculated from immutable snapshots with full decimal precision.
          Margins represent profit as percentage of selling price.
        </p>
      </div>
    </DashboardLayout>
  );
}