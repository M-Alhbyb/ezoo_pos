'use client';

import React, { useState, useEffect } from 'react';
import { Package } from 'lucide-react';
import { StackedBarChart } from '../../components/charts/StackedBarChart';
import { DashboardLayout } from '../../components/dashboard/DashboardLayout';
import { QuickDateRanges } from '../../components/dashboard/DatePicker';
import { getInventoryDashboard } from '../../lib/api/dashboard';
import { transformInventoryChartData } from '../../lib/utils/chart-utils';

export default function InventoryDashboardPage() {
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [chartData, setChartData] = useState<{ name: string; sales: number; restocks: number; reversals: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalMovements, setTotalMovements] = useState<number>(0);

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
      const response = await getInventoryDashboard(startDate, endDate);
      
      if (!response.success) {
        setError(response.error || 'Failed to load dashboard data');
        setChartData([]);
        return;
      }

      if (response.data) {
        const transformedData = transformInventoryChartData(
          response.data.dates,
          response.data.sales,
          response.data.restocks,
          response.data.reversals
        );
        
        const barData = transformedData.map(item => ({
          name: item.date,
          sales: item.sales,
          restocks: item.restocks,
          reversals: item.reversals
        }));
        
        setChartData(barData);
        
        const total = transformedData.reduce((sum, item) => 
          sum + Math.abs(item.sales) + Math.abs(item.restocks) + Math.abs(item.reversals), 0
        );
        setTotalMovements(total);
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

  const stacks = [
    { dataKey: 'sales', color: '#8884d8', name: 'Sales' },
    { dataKey: 'restocks', color: '#82ca9d', name: 'Restocks' },
    { dataKey: 'reversals', color: '#ffc658', name: 'Reversals' }
  ];

  return (
    <DashboardLayout
      title="Inventory Dashboard"
      description="Inventory movement tracking by reason type"
      dashboardType="inventory"
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

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-purple-600" />
            <h4 className="text-sm font-medium text-purple-900">Total Movements</h4>
          </div>
          <p className="text-3xl font-bold text-purple-600 mt-2">
            {totalMovements.toLocaleString()}
          </p>
        </div>
        
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-green-900">Movements Shown</h4>
          <p className="text-xl font-bold text-green-600 mt-2">
            {chartData.length} days
          </p>
        </div>
        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900">Data Points</h4>
          <p className="text-xl font-bold text-blue-600 mt-2">
            ≤ 1000 limit
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Package className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Movement Distribution</h3>
          </div>
        </div>

        <StackedBarChart
          data={chartData}
          stacks={stacks}
          height={450}
          loading={loading}
          emptyMessage="No inventory movement data available for the selected date range"
          showGrid={true}
          showLegend={true}
        />

        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Chart Features</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Stacked bars show sales (purple), restocks (green), and reversals (yellow)</li>
            <li>• Hover over segments to see individual quantities</li>
            <li>• Negative values displayed as absolute numbers</li>
            <li>• Daily aggregation for time-series analysis</li>
          </ul>
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mt-6">
        <h4 className="text-sm font-semibold text-yellow-900 mb-2">Movement Types</h4>
        <ul className="text-sm text-yellow-800 space-y-1">
          <li>• <strong>Sales:</strong> Products sold to customers (decreases inventory)</li>
          <li>• <strong>Restocks:</strong> Products restocked from suppliers (increases inventory)</li>
          <li>• <strong>Reversals:</strong> Sale reversals and adjustments (increases inventory)</li>
        </ul>
      </div>
    </DashboardLayout>
  );
}