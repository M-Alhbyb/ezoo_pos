import { API_BASE } from "./suppliers";

export interface SaleDetail {
  id: string;
  payment_method_name: string;
  payments: Array<{
    payment_method_name: string;
    amount: number;
  }>;
  items: Array<{
    product_id: string;
    product_name: string;
    quantity: number;
    remaining_quantity?: number;
    unit_price: number;
    line_total: number;
  }>;
  subtotal: number;
  fees_total: number;
  vat_total: number;
  grand_total: number;
  note: string;
  is_reversal: boolean;
  original_sale_id?: string;
  created_at: string;
}

export async function getSale(saleId: string): Promise<SaleDetail> {
  const response = await fetch(`${API_BASE}/sales/${saleId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch sale details");
  }
  return response.json();
}

export async function reverseSale(
  saleId: string, 
  reason: string = "Manual Reversal",
  items?: Array<{ product_id: string; quantity: number }>
): Promise<SaleDetail> {
  const response = await fetch(`${API_BASE}/sales/${saleId}/reverse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reason, items }),
  });
  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.detail?.error?.message || "Failed to reverse sale");
  }
  return response.json();
}
