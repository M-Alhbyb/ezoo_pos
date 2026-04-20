'use client';

import React from 'react';
import { Calendar } from 'lucide-react';

export interface DatePickerProps {
  startDate: string;
  endDate: string;
  onStartDateChange: (date: string) => void;
  onEndDateChange: (date: string) => void;
 disabled?: boolean;
}

export function DatePicker({
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  disabled = false
}: DatePickerProps) {
  return (
    <div className="flex items-center gap-4">
      <div className="flex items-center gap-2">
        <Calendar className="w-5 h-5 text-gray-500" />
        <label className="text-sm font-medium text-gray-700">From:</label>
        <input
          type="date"
          value={startDate}
          onChange={(e) => onStartDateChange(e.target.value)}
          disabled={disabled}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
      </div>
      
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-gray-700">To:</label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => onEndDateChange(e.target.value)}
          disabled={disabled}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
        />
      </div>
    </div>
  );
}

export interface QuickRangeButton {
  label: string;
  range: { start: Date; end: Date };
}

export function QuickDateRanges({
  onRangeSelect,
  disabled = false
}: {
  onRangeSelect: (start: string, end: string) => void;
  disabled?: boolean;
}) {
  const today = new Date();
  
  const ranges: QuickRangeButton[] = [
    {
      label: 'Today',
      range: { start: today, end: today }
    },
    {
      label: 'Last 7 Days',
      range: {
        start: new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000),
        end: today
      }
    },
    {
      label: 'Last 30 Days',
      range: {
        start: new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000),
        end: today
      }
    },
    {
      label: 'This Month',
      range: {
        start: new Date(today.getFullYear(), today.getMonth(), 1),
        end: today
      }
    },
    {
      label: 'Last 3 Months',
      range: {
        start: new Date(today.getFullYear(), today.getMonth() - 2, 1),
        end: new Date(today.getFullYear(), today.getMonth() + 1, 0)
      }
    }
  ];

  const formatDate = (date: Date) => {
    return date.toISOString().split('T')[0];
  };

  return (
    <div className="flex flex-wrap gap-2">
      {ranges.map((range) => (
        <button
          key={range.label}
          onClick={() => onRangeSelect(formatDate(range.range.start), formatDate(range.range.end))}
          disabled={disabled}
          className="px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 disabled:bg-gray-100 disabled:text-gray-400 disabled:border-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {range.label}
        </button>
      ))}
    </div>
  );
}