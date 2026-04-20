import { api } from '../api-client';

export interface SalesDashboardFilter {
  start_date: string;
  end_date: string;
}


export interface PartnersDashboardFilter extends SalesDashboardFilter {
  partner_id?: number;
}

export interface InventoryDashboardFilter extends SalesDashboardFilter {}

export interface DashboardResponse<T> {
  success: boolean;
  data: T | null;
  error: string | null;
  total_points: number | null;
  filter_applied: SalesDashboardFilter | null;
}

export interface SalesChartData {
  dates: string[];
  revenue: number[];
  profit: number[];
  vat: number[];
}


export interface PartnerChartData {
  partner_names: string[];
  dividend_amounts: number[];
  share_percentages: number[];
  partner_ids: number[];
}

export interface InventoryChartData {
  dates: string[];
  sales: number[];
  restocks: number[];
  reversals: number[];
}

export async function getSalesDashboard(
  startDate: string,
  endDate: string
): Promise<DashboardResponse<SalesChartData>> {
  const response = await api.get('/api/dashboard/sales', {
    params: { start_date: startDate, end_date: endDate }
  });
  return response;
}


export async function getPartnersDashboard(
  startDate: string,
  endDate: string,
  partnerId?: number
): Promise<DashboardResponse<PartnerChartData>> {
  const params: Record<string, string | number> = {
    start_date: startDate,
    end_date: endDate
  };
  if (partnerId !== undefined) {
    params.partner_id = partnerId;
  }
  const response = await api.get('/api/dashboard/partners', { params });
  return response;
}

export async function getInventoryDashboard(
  startDate: string,
  endDate: string
): Promise<DashboardResponse<InventoryChartData>> {
  const response = await api.get('/api/dashboard/inventory', {
    params: { start_date: startDate, end_date: endDate }
  });
  return response;
}