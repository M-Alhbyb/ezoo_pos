'use client';

import React from 'react';
import { Calendar } from 'lucide-react';
import { ARABIC } from '@/lib/constants/arabic';

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
        <Calendar className="w-5 h-5 text-slate-500" />
        <label className="text-sm font-medium text-slate-700">{ARABIC.dates.from}:</label>
        <input
          type="date"
          value={startDate}
          onChange={(e) => onStartDateChange(e.target.value)}
          disabled={disabled}
          className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-slate-100 disabled:cursor-not-allowed"
        />
      </div>
      
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium text-slate-700">{ARABIC.dates.to}:</label>
        <input
          type="date"
          value={endDate}
          onChange={(e) => onEndDateChange(e.target.value)}
          disabled={disabled}
          className="px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-slate-100 disabled:cursor-not-allowed"
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
      label: ARABIC.dates.today,
      range: { start: today, end: today }
    },
    {
      label: '7 أيام',
      range: {
        start: new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000),
        end: today
      }
    },
    {
      label: '30 يوم',
      range: {
        start: new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000),
        end: today
      }
    },
    {
      label: ARABIC.dates.thisMonth,
      range: {
        start: new Date(today.getFullYear(), today.getMonth(), 1),
        end: today
      }
    },
    {
      label: '3 أشهر',
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
          className="px-3 py-1.5 text-sm font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 disabled:bg-slate-100 disabled:text-slate-400 disabled:border-slate-300 disabled:cursor-not-allowed transition-colors"
        >
          {range.label}
        </button>
      ))}
    </div>
  );
}
