'use client';

import React from 'react';
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { formatDecimal, formatCurrency, formatPercentage } from '../../lib/utils/chart-utils';

export interface BarChartDataPoint {
  name: string;
  value?: number;
  [key: string]: string | number | undefined;
}

export interface BarChartProps {
  data: BarChartDataPoint[];
  bars: { dataKey: string; color: string; name: string }[];
  height?: number;
  loading?: boolean;
  emptyMessage?: string;
  showGrid?: boolean;
  showLegend?: boolean;
  isCurrency?: boolean;
  isPercentage?: boolean;
  decimalPlaces?: number;
}

export function BarChart({
  data,
  bars,
  height = 400,
  loading = false,
  emptyMessage = 'No data available',
  showGrid = true,
  showLegend = true,
  isCurrency = true,
  isPercentage = false,
  decimalPlaces = 4
}: BarChartProps) {
  if (loading) {
    return (
      <div 
        style={{ height }} 
        className="flex items-center justify-center bg-gray-50 rounded-lg"
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading chart data...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div 
        style={{ height }} 
        className="flex items-center justify-center bg-gray-50 rounded-lg"
      >
        <div className="text-center">
          <svg 
            className="mx-auto h-12 w-12 text-gray-400" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" 
            />
          </svg>
          <p className="mt-2 text-gray-600">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  const formatTooltipValue = (value: number) => {
    const formatted = formatDecimal(value, decimalPlaces);
    if (isCurrency) {
      return `$${formatted}`;
    }
    if (isPercentage) {
      return `${formatted}%`;
    }
    return formatted;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBarChart data={data}>
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
        <XAxis 
          dataKey="name" 
          tick={{ fontSize: 12 }}
          stroke="#9ca3af"
          angle={-45}
          textAnchor="end"
          height={80}
        />
        <YAxis 
          tick={{ fontSize: 12 }}
          stroke="#9ca3af"
          tickFormatter={(value) => {
            if (isPercentage) return `${formatDecimal(value, 1)}%`;
            return isCurrency ? `$${formatDecimal(value, 0)}` : formatDecimal(value, 0);
          }}
        />
        <Tooltip 
          formatter={(value: number) => formatTooltipValue(value)}
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
        />
        {showLegend && (
          <Legend 
            wrapperStyle={{ paddingTop: '20px' }}
          />
        )}
        {bars.map((bar) => (
          <Bar
            key={bar.dataKey}
            dataKey={bar.dataKey}
            fill={bar.color}
            name={bar.name}
          />
        ))}
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}