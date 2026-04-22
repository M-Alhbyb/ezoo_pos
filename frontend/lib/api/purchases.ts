const API_BASE = '/api';

export interface PurchaseItem {
  id: string;
  purchase_id: string;
  product_id: string;
  quantity: number;
  unit_cost: number;
  total_cost: number;
  product_name?: string;
  product_sku?: string;
  current_stock?: number;
}

export interface Purchase {
  id: string;
  supplier_id: string;
  total_amount: number;
  created_at: string;
}

export interface PurchaseWithItems extends Purchase {
  items: PurchaseItem[];
}

export interface PurchaseListResponse {
  purchases: Purchase[];
  total: number;
}

export interface CreatePurchaseItem {
  product_id: string;
  quantity: number;
  unit_cost: number;
}

export async function createPurchase(data: {
  supplier_id: string;
  items: CreatePurchaseItem[];
}): Promise<Purchase> {
  const res = await fetch(`${API_BASE}/purchases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error('Failed to create purchase');
  return res.json();
}

export async function getPurchases(
  supplierId?: string,
  limit = 100,
  offset = 0
): Promise<Purchase[]> {
  const params = new URLSearchParams();
  if (supplierId) params.set('supplier_id', supplierId);
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  const res = await fetch(`${API_BASE}/purchases?${params}`);
  if (!res.ok) throw new Error('Failed to fetch purchases');
  const data: PurchaseListResponse = await res.json();
  return data.purchases;
}

export async function getPurchase(id: string): Promise<PurchaseWithItems> {
  const res = await fetch(`${API_BASE}/purchases/${id}`);
  if (!res.ok) throw new Error('Failed to fetch purchase');
  return res.json();
}

export interface ReturnItem {
  product_id: string;
  quantity: number;
}

export interface ReturnResponse {
  id: string;
  purchase_id: string;
  total_returned: number;
  created_at: string;
  items: PurchaseItem[];
}

export async function returnItems(
  purchaseId: string,
  data: { items: ReturnItem[]; note?: string }
): Promise<ReturnResponse> {
  const res = await fetch(`${API_BASE}/purchases/${purchaseId}/return`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || 'Failed to return items');
  }
  return res.json();
}