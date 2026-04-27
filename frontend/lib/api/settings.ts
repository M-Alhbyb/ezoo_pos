import { API_BASE } from "./suppliers"; // Reusing the base URL pattern

export interface PaymentMethod {
  id: string;
  name: string;
  is_active: boolean;
}

export async function getPaymentMethods(activeOnly: boolean = true): Promise<PaymentMethod[]> {
  const response = await fetch(`${API_BASE}/settings/payment-methods?active_only=${activeOnly}`);
  if (!response.ok) {
    throw new Error("Failed to fetch payment methods");
  }
  const data = await response.json();
  return data.items;
}
