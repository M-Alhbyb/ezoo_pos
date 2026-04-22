const API_BASE = '/api';

export interface Customer {
  id: string;
  name: string;
  phone: string | null;
  address: string | null;
  notes: string | null;
  credit_limit: number;
  created_at: string;
  updated_at: string;
}

export interface CustomerWithBalance extends Pick<Customer, 'id' | 'name' | 'phone' | 'credit_limit'> {
  balance: number;
}

export interface CustomerSummary {
  total_sales: number;
  total_payments: number;
  total_returns: number;
  balance: number;
}

export interface CustomerDetail extends Customer {
  summary: CustomerSummary;
}

export interface CustomerListResponse {
  customers: CustomerWithBalance[];
  total: number;
}

export interface LedgerEntry {
  id: string;
  type: string;
  amount: number;
  reference_id: string | null;
  payment_method: string | null;
  note: string | null;
  created_at: string;
}

export interface LedgerListResponse {
  entries: LedgerEntry[];
  total: number;
}

export async function getCustomers(): Promise<CustomerWithBalance[]> {
  const res = await fetch(`${API_BASE}/customers`);
  if (!res.ok) throw new Error('Failed to fetch customers');
  const data: CustomerListResponse = await res.json();
  return data.customers;
}

export async function getCustomer(id: string): Promise<CustomerDetail> {
  const res = await fetch(`${API_BASE}/customers/${id}`);
  if (!res.ok) throw new Error('Failed to fetch customer');
  return res.json();
}

export async function createCustomer(data: {
  name: string;
  phone: string;
  address?: string;
  notes?: string;
  credit_limit?: number;
}): Promise<Customer> {
  const res = await fetch(`${API_BASE}/customers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create customer');
  return res.json();
}

export async function getCustomerLedger(
  customerId: string,
  page: number = 1,
  pageSize: number = 50,
  startDate?: string,
  endDate?: string
): Promise<LedgerListResponse> {
  const params = new URLSearchParams();
  params.set('page', page.toString());
  params.set('page_size', pageSize.toString());
  if (startDate) params.set('start_date', startDate);
  if (endDate) params.set('end_date', endDate);
  const res = await fetch(`${API_BASE}/customers/${customerId}/ledger?${params}`);
  if (!res.ok) throw new Error('Failed to fetch ledger');
  return res.json();
}

export async function recordCustomerPayment(
  customerId: string,
  data: { amount: number; payment_method: string; note?: string; idempotency_key?: string }
): Promise<LedgerEntry> {
  const res = await fetch(`${API_BASE}/customers/${customerId}/payments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to record payment');
  return res.json();
}

export interface CustomerReport {
  id: string;
  name: string;
  phone: string | null;
  balance: number;
  credit_limit: number;
}

export interface CustomerReportResponse {
  total_customers: number;
  total_debt: number;
  customers: CustomerReport[];
}

export async function getCustomerSummaryReport(): Promise<CustomerReportResponse> {
  const res = await fetch(`${API_BASE}/customers/report/summary`);
  if (!res.ok) throw new Error('Failed to fetch customer report');
  return res.json();
}