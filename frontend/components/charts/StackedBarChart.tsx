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
import { ARABIC } from '@/lib/constants/arabic';

export interface StackedBarDataPoint {
  name: string;
  [key: string]: string | number;
}

export interface StackedBarChartProps {
  data: StackedBarDataPoint[];
  stacks: { dataKey: string; color: string; name: string }[];
  height?: number;
  loading?: boolean;
  emptyMessage?: string;
  showGrid?: boolean;
  showLegend?: boolean;
}

export function StackedBarChart({
  data,
  stacks,
  height = 400,
  loading = false,
  emptyMessage = 'لا توجد بيانات',
  showGrid = true,
  showLegend = true
}: StackedBarChartProps) {
  if (loading) {
    return (
      <div 
        style={{ height }} 
        className="flex items-center justify-center bg-slate-50 rounded-xl"
      >
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">{ARABIC.common.loading}</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div 
        style={{ height }} 
        className="flex items-center justify-center bg-slate-50 rounded-xl"
      >
        <div className="text-center">
          <svg 
            className="mx-auto h-12 w-12 text-slate-400" 
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
          <p className="mt-2 text-slate-600">{emptyMessage}</p>
        </div>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsBarChart data={data} layout="vertical">
        {showGrid && <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />}
        <XAxis 
          type="number"
          tick={{ fontSize: 12 }}
          stroke="#9ca3af"
        />
        <YAxis 
          type="category"
          dataKey="name" 
          tick={{ fontSize: 12 }}
          stroke="#9ca3af"
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: '#fff',
            border: '1px solid #e5e7eb',
            borderRadius: '0.5rem',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
            direction: 'rtl',
            textAlign: 'right'
          }}
        />
        {showLegend && (
          <Legend 
            wrapperStyle={{ paddingTop: '20px', direction: 'rtl' }}
          />
        )}
        {stacks.map((stack) => (
          <Bar
            key={stack.dataKey}
            dataKey={stack.dataKey}
            stackId="a"
            fill={stack.color}
            name={stack.name}
          />
        ))}
      </RechartsBarChart>
    </ResponsiveContainer>
  );
}
