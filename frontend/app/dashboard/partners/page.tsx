'use client';

import React, { useState, useEffect } from 'react';
import { Users } from 'lucide-react';
import { PieChart } from '@/components/charts/PieChart';
import { DashboardLayout } from '@/components/dashboard/DashboardLayout';
import { QuickDateRanges } from '@/components/dashboard/DatePicker';
import { getPartnersDashboard } from '@/lib/api/dashboard';
import { transformPartnerChartData } from '@/lib/utils/chart-utils';
import { PartnerChartData } from '@/lib/api/dashboard';

export default function PartnersDashboardPage() {
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [chartData, setChartData] = useState<{ name: string; value: number }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalDividends, setTotalDividends] = useState<number>(0);

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
      const response = await getPartnersDashboard(startDate, endDate);
      
      if (!response.success) {
        setError(response.error || 'Failed to load dashboard data');
        setChartData([]);
        return;
      }

      if (response.data) {
        const transformedData = transformPartnerChartData(
          response.data.partner_names,
          response.data.dividend_amounts,
          response.data.share_percentages,
          response.data.partner_ids
        );
        
        const pieData = transformedData.map(item => ({
          name: item.name,
          value: item.amount
        }));
        
        setChartData(pieData);
        setTotalDividends(pieData.reduce((sum, item) => sum + item.value, 0));
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

  return (
    <DashboardLayout
      title="Partners Dashboard"
      description="Partner dividend distribution with percentage breakdown"
      dashboardType="partners"
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
            <Users className="w-5 h-5 text-green-600" />
            <h3 className="text-lg font-semibold text-gray-900">Dividend Distribution</h3>
          </div>
          {totalDividends > 0 && (
            <div className="text-right">
              <p className="text-sm text-gray-500">Total Dividends</p>
              <p className="text-2xl font-bold text-green-600">
                ${totalDividends.toFixed(2)}
              </p>
            </div>
          )}
        </div>

        <PieChart
          data={chartData}
          height={500}
          loading={loading}
          emptyMessage="No partner data available for the selected date range"
          showLegend={true}
          isCurrency={true}
          decimalPlaces={2}
        />

        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Chart Features</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>• Hover over segments to see partner name and dividend amount</li>
            <li>• Segments show percentage of total dividends</li>
            <li>• Click legend items to toggle segment visibility</li>
            <li>• Values displayed with full monetary precision</li>
          </ul>
        </div>
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-6 mt-6">
        <h4 className="text-sm font-semibold text-green-900 mb-2">Data Accuracy</h4>
        <p className="text-sm text-green-800">
          All dividend amounts are calculated from immutable distribution records with full decimal precision.
          Percentages represent each partner's share of the total distribution.
        </p>
      </div>
    </DashboardLayout>
  );
}