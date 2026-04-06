'use client';

import React from 'react';
import {
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { formatDecimal, formatCurrency, formatPercentage } from '../../lib/utils/chart-utils';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe', '#00C49F', '#FFBB28', '#FF8042', '#a4de6c', '#d0ed57'];

export interface PieChartDataPoint {
  name: string;
  value: number;
}

export interface PieChartProps {
  data: PieChartDataPoint[];
  height?: number;
  loading?: boolean;
  emptyMessage?: string;
  showLegend?: boolean;
  isCurrency?: boolean;
  decimalPlaces?: number;
}

export function PieChart({
  data,
  height = 400,
  loading = false,
  emptyMessage = 'No data available',
  showLegend = true,
  isCurrency = true,
  decimalPlaces = 2
}: PieChartProps) {
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
              d="M11 3.055A9.001 9.001 0 1020.945 13H11V3.055z" 
            />
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M20.488 9H15V3.512A9.025 9.025 0 0120.488 9z" 
            />
          </svg>
          <p className="mt-2 text-gray-600">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  const formatTooltipValue = (value: number, name: string) => {
    const formatted = formatDecimal(value, decimalPlaces);
    return isCurrency ? `$${formatted}` : formatted;
  };

  const label = ({ name, percent }: { name: string; percent: number }) => {
    return `${name} (${(percent * 100).toFixed(1)}%)`;
  };

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsPieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={label}
          outerRadius={150}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip 
          formatter={(value: number, name: string) => formatTooltipValue(value, name)}
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
            formatter={(value) => <span className="text-gray-700">{value}</span>}
          />
        )}
      </RechartsPieChart>
    </ResponsiveContainer>
  );
}