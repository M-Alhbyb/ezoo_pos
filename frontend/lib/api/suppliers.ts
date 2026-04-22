const API_BASE = '/api';

export interface Supplier {
  id: string;
  name: string;
  phone: string | null;
  notes: string | null;
  created_at: string;
}

export interface SupplierWithBalance extends Supplier {
  balance: number;
}

export interface SupplierSummary {
  total_purchases: number;
  total_payments: number;
  total_returns: number;
  balance: number;
}

export interface SupplierDetail extends Supplier {
  summary: SupplierSummary;
}

export interface SupplierListResponse {
  suppliers: SupplierWithBalance[];
  total: number;
}

export async function getSuppliers(): Promise<SupplierWithBalance[]> {
  const res = await fetch(`${API_BASE}/suppliers`);
  if (!res.ok) throw new Error('Failed to fetch suppliers');
  const data: SupplierListResponse = await res.json();
  return data.suppliers;
}

export async function getSupplier(id: string): Promise<SupplierDetail> {
  const res = await fetch(`${API_BASE}/suppliers/${id}`);
  if (!res.ok) throw new Error('Failed to fetch supplier');
  return res.json();
}

export async function createSupplier(data: { name: string; phone?: string; notes?: string }): Promise<Supplier> {
  const res = await fetch(`${API_BASE}/suppliers`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create supplier');
  return res.json();
}

export async function recordPayment(
  supplierId: string,
  data: { amount: number; note?: string }
): Promise<{ id: string }> {
  const res = await fetch(`${API_BASE}/suppliers/${supplierId}/payments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to record payment');
  return res.json();
}

export interface SupplierSummaryReport {
  id: string;
  name: string;
  total_purchases: number;
  total_payments: number;
  total_returns: number;
  balance: number;
}

export async function getSupplierSummaryReport(): Promise<SupplierSummaryReport[]> {
  const res = await fetch(`${API_BASE}/reports/suppliers`);
  if (!res.ok) throw new Error('Failed to fetch supplier report');
  const data = await res.json();
  return data.suppliers;
}

export interface SupplierStatement {
  supplier: { id: string; name: string };
  summary: SupplierSummary;
  ledger: Array<{
    id: string;
    type: string;
    amount: number;
    reference_id: string | null;
    note: string | null;
    created_at: string;
  }>;
}

export async function getSupplierStatement(
  supplierId: string,
  startDate?: string,
  endDate?: string
): Promise<SupplierStatement> {
  const params = new URLSearchParams();
  if (startDate) params.set('start_date', startDate);
  if (endDate) params.set('end_date', endDate);
  const query = params.toString();
  const res = await fetch(`${API_BASE}/reports/suppliers/${supplierId}${query ? `?${query}` : ''}`);
  if (!res.ok) throw new Error('Failed to fetch supplier statement');
  return res.json();
}