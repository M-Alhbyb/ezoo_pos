import { Decimal } from 'decimal.js';

export interface ChartDataPoint {
  date: string;
  value: number;
}

export interface SalesChartDataPoint {
  date: string;
  revenue: number;
  profit: number;
  vat: number;
}

export interface ProjectChartDataPoint {
  name: string;
  profit: number;
  margin: number;
  id: number;
}

export interface PartnerChartDataPoint {
  name: string;
  amount: number;
  share_percentage: number;
  id: number;
}

export interface InventoryChartDataPoint {
  date: string;
  sales: number;
  restocks: number;
  reversals: number;
}

export function formatDecimal(value: number, decimals: number = 4): string {
  return new Decimal(value).toFixed(decimals);
}

export function formatCurrency(value: number, decimals: number = 2): string {
  return new Decimal(value).toFixed(decimals);
}

export function formatPercentage(value: number, decimals: number = 2): string {
  return new Decimal(value).toFixed(decimals) + '%';
}

export function transformSalesChartData(
  dates: string[],
  revenue: number[],
  profit: number[],
  vat: number[]
): SalesChartDataPoint[] {
  return dates.map((date, index) => ({
    date,
    revenue: revenue[index],
    profit: profit[index],
    vat: vat[index]
  }));
}

export function transformProjectChartData(
  project_names: string[],
  profits: number[],
  profit_margins: number[],
  project_ids: number[]
): ProjectChartDataPoint[] {
  return project_names.map((name, index) => ({
    name,
    profit: profits[index],
    margin: profit_margins[index],
    id: project_ids[index]
  }));
}

export function transformPartnerChartData(
  partner_names: string[],
  dividend_amounts: number[],
  share_percentages: number[],
  partner_ids: number[]
): PartnerChartDataPoint[] {
  return partner_names.map((name, index) => ({
    name,
    amount: dividend_amounts[index],
    share_percentage: share_percentages[index],
    id: partner_ids[index]
  }));
}

export function transformInventoryChartData(
  dates: string[],
  sales: number[],
  restocks: number[],
  reversals: number[]
): InventoryChartDataPoint[] {
  return dates.map((date, index) => ({
    date,
    sales: sales[index],
    restocks: restocks[index],
    reversals: reversals[index]
  }));
}

export function aggregateChartData(
  data: ChartDataPoint[],
  groupBy: 'day' | 'week' | 'month'
): ChartDataPoint[] {
  const grouped = new Map<string, number[]>();
  
  data.forEach(point => {
    const key = getGroupKey(point.date, groupBy);
    if (!grouped.has(key)) {
      grouped.set(key, []);
    }
    grouped.get(key)!.push(point.value);
  });
  
  return Array.from(grouped.entries()).map(([date, values]) => ({
    date,
    value: values.reduce((sum, val) => sum + val, 0) / values.length
  }));
}

function getGroupKey(date: string, groupBy: 'day' | 'week' | 'month'): string {
  const d = new Date(date);
  switch (groupBy) {
    case 'day':
      return date;
    case 'week':
      const week = getWeekNumber(d);
      return `${d.getFullYear()}-W${week.toString().padStart(2, '0')}`;
    case 'month':
      return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}`;
    default:
      return date;
  }
}

function getWeekNumber(date: Date): number {
  const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
  const dayNum = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - dayNum);
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
}

export function getColorForDataPoint(
  index: number,
  colorPalette: string[] = [
    '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#0088fe',
    '#00C49F', '#FFBB28', '#FF8042', '#a4de6c', '#d0ed57'
  ]
): string {
  return colorPalette[index % colorPalette.length];
}

export function calculateTrend(
  data: ChartDataPoint[]
): { direction: 'up' | 'down' | 'stable'; percentage: number } {
  if (data.length < 2) {
    return { direction: 'stable', percentage: 0 };
  }
  
  const first = data[0].value;
  const last = data[data.length - 1].value;
  
  if (first === 0) {
    return { direction: last > 0 ? 'up' : 'stable', percentage: 100 };
  }
  
  const percentage = ((last - first) / first) * 100;
  
  return {
    direction: percentage > 5 ? 'up' : percentage < -5 ? 'down' : 'stable',
    percentage: Math.abs(percentage)
  };
}