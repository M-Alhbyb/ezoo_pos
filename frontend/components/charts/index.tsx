import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts';
import { formatDecimal } from '../utils/chart-utils';
import { formatCurrency, formatPercentage } from '@/lib/utils/format';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe', '#00C49F', '#FFBB28', '#FF8042'];

interface BaseChartProps {
  data: any[];
  height?: number;
  loading?: boolean;
  emptyMessage?: string;
}

interface LineChartData {
  date: string;
  [key: string]: string | number;
}

interface BarChartData {
  name: string;
  value: number;
  [key: string]: string | number;
}

interface PieChartData {
  name: string;
  value: number;
}

export interface BaseChartConfig {
  showGrid?: boolean;
  showLegend?: boolean;
  showTooltip?: boolean;
  decimalPlaces?: number;
  isCurrency?: boolean;
  isPercentage?: boolean;
}

export const defaultChartConfig: BaseChartConfig = {
  showGrid: true,
  showLegend: true,
  showTooltip: true,
  decimalPlaces: 4,
  isCurrency: false,
  isPercentage: false
};

export const formatTooltipValue = (value: number, config: BaseChartConfig): string => {
  const formatted = formatDecimal(value, config.decimalPlaces || 4);
  if (config.isCurrency) {
    return formatCurrency(value);
  }
  if (config.isPercentage) {
    return formatPercentage(value);
  }
  return formatted;
};

export interface SalesLineChartProps extends BaseChartProps {
  data: LineChartData[];
  lines: { dataKey: string; color: string; name: string }[];
  config?: BaseChartConfig;
}

export const SalesLineChart: React.FC<SalesLineChartProps> = ({
  data,
  lines,
  height = 400,
  loading = false,
  emptyMessage = 'لا توجد بيانات',
  config = defaultChartConfig
}) => {
  if (loading) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>جارٍ التحميل...</div>;
  }
  
  if (!data || data.length === 0) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{emptyMessage}</div>;
  }
  
  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} layout="vertical">
        {config.showGrid && <CartesianGrid strokeDasharray="3 3" />}
        <XAxis type="number" />
        <YAxis type="category" dataKey="date" width={100} />
        {config.showTooltip && (
          <Tooltip formatter={(value: number) => formatTooltipValue(value, config)} />
        )}
        {config.showLegend && <Legend />}
        {lines.map((line, index) => (
          <Line
            key={line.dataKey}
            type="monotone"
            dataKey={line.dataKey}
            stroke={line.color}
            name={line.name}
            strokeWidth={2}
            dot={{ fill: line.color }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
};

export interface ProjectBarChartProps extends BaseChartProps {
  data: BarChartData[];
  bars: { dataKey: string; color: string; name: string }[];
  config?: BaseChartConfig;
}

export const ProjectBarChart: React.FC<ProjectBarChartProps> = ({
  data,
  bars,
  height = 400,
  loading = false,
  emptyMessage = 'لا توجد بيانات',
  config = defaultChartConfig
}) => {
  if (loading) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>جارٍ التحميل...</div>;
  }
  
  if (!data || data.length === 0) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{emptyMessage}</div>;
  }
  
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical">
        {config.showGrid && <CartesianGrid strokeDasharray="3 3" />}
        <XAxis type="number" />
        <YAxis type="category" dataKey="name" width={100} />
        {config.showTooltip && (
          <Tooltip formatter={(value: number) => formatTooltipValue(value, config)} />
        )}
        {config.showLegend && <Legend />}
        {bars.map((bar) => (
          <Bar
            key={bar.dataKey}
            dataKey={bar.dataKey}
            fill={bar.color}
            name={bar.name}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
};

export interface PartnerPieChartProps extends BaseChartProps {
  data: PieChartData[];
  config?: BaseChartConfig;
}

export const PartnerPieChart: React.FC<PartnerPieChartProps> = ({
  data,
  height = 400,
  loading = false,
  emptyMessage = 'لا توجد بيانات',
  config = defaultChartConfig
}) => {
  if (loading) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>جارٍ التحميل...</div>;
  }
  
  if (!data || data.length === 0) {
    return <div style={{ height, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{emptyMessage}</div>;
  }
  
  return (
    <ResponsiveContainer width="100%" height={height}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} (${(percent * 100).toFixed(1)}%)`}
          outerRadius={150}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        {config.showTooltip && (
          <Tooltip formatter={(value: number) => formatTooltipValue(value, config)} />
        )}
        {config.showLegend && <Legend />}
      </PieChart>
    </ResponsiveContainer>
  );
};

export { COLORS };