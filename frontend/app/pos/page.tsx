"use client";

import { useState } from "react";
import { Decimal } from "decimal.js";

// Components
import ProductSearch from "@/components/pos/ProductSearch";
import POSCart from "@/components/pos/POSCart";
import FeeEditor from "@/components/pos/FeeEditor";
import PaymentMethodSelect from "@/components/pos/PaymentMethodSelect";
import SaleBreakdown from "@/components/pos/SaleBreakdown";
import ConfirmButton from "@/components/pos/ConfirmButton";

// Types
interface CartItem {
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
}

interface Fee {
  fee_type: "shipping" | "installation" | "custom";
  fee_label: string;
  fee_value_type: "fixed" | "percent";
  fee_value: number;
}

interface Breakdown {
  items: Array<{
    product_name: string;
    quantity: number;
    unit_price: string;
    line_total: string;
  }>;
  subtotal: string;
  fees: Array<{
    fee_label: string;
    fee_value: string;
    fee_value_type: string;
    calculated_amount: string;
  }>;
  fees_total: string;
  vat_enabled: boolean;
  vat_rate: string | null;
  vat_amount: string | null;
  total: string;
}

export default function POSPage() {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [fees, setFees] = useState<Fee[]>([]);
  const [paymentMethodId, setPaymentMethodId] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [breakdown, setBreakdown] = useState<Breakdown | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);

  // Add product to cart
  const handleProductSelect = async (product: any) => {
    // Check if product already in cart
    const existingItem = cartItems.find((item) => item.product_id === product.id);

    if (existingItem) {
      // Increment quantity
      handleQuantityChange(product.id, existingItem.quantity + 1);
    } else {
      // Add new item
      const newItem: CartItem = {
        product_id: product.id,
        product_name: product.name,
        quantity: 1,
        unit_price: parseFloat(product.selling_price),
      };

      setCartItems([...cartItems, newItem]);
    }

    // Recalculate breakdown
    await calculateBreakdown([...cartItems, existingItem ? { ...existingItem, quantity: existingItem.quantity + 1 } : newItem], fees);
  };

  // Change quantity
  const handleQuantityChange = async (product_id: string, quantity: number) => {
    const newItems = cartItems.map((item) =>
      item.product_id === product_id ? { ...item, quantity } : item
    );
    setCartItems(newItems);
    await calculateBreakdown(newItems, fees);
  };

  // Remove item from cart
  const handleRemove = async (product_id: string) => {
    const newItems = cartItems.filter((item) => item.product_id !== product_id);
    setCartItems(newItems);
    await calculateBreakdown(newItems, fees);
  };

  // Clear cart
  const handleClear = async () => {
    setCartItems([]);
    setBreakdown(null);
  };

  // Calculate breakdown
  const calculateBreakdown = async (items: CartItem[], saleFees: Fee[]) => {
    if (items.length === 0) {
      setBreakdown(null);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const response = await fetch("/api/sales/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: items.map((item) => ({
            product_id: item.product_id,
            quantity: item.quantity,
            unit_price_override: item.unit_price !== undefined ? item.unit_price : undefined,
          })),
          fees: saleFees,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail?.error?.message || "Failed to calculate breakdown");
      }

      const data = await response.json();
      setBreakdown(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Handle fees change
  const handleFeesChange = async (newFees: Fee[]) => {
    setFees(newFees);
    await calculateBreakdown(cartItems, newFees);
  };

  // Confirm sale
  const handleConfirm = async () => {
    if (!paymentMethodId || cartItems.length === 0) return;

    try {
      setLoading(true);
      setError("");
      setSuccess(false);

      const response = await fetch("/api/sales", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: cartItems.map((item) => ({
            product_id: item.product_id,
            quantity: item.quantity,
            unit_price_override: item.unit_price !== undefined ? item.unit_price : undefined,
          })),
          fees,
          payment_method_id: paymentMethodId,
          note: note || undefined,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail?.error?.message || "Failed to create sale");
      }

      // Success
      setSuccess(true);
      setCartItems([]);
      setFees([]);
      setBreakdown(null);
      setNote("");

      // Show success message
      setTimeout(() => setSuccess(false), 5000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Point of Sale</h1>

      {success && (
        <div className="bg-green-100 text-green-800 px-4 py-2 rounded mb-4">
          Sale completed successfully!
        </div>
      )}

      {error && (
        <div className="bg-red-100 text-red-700 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Product Search */}
        <div className="lg:col-span-1">
          <div className="border rounded p-4">
            <ProductSearch onProductSelect={handleProductSelect} />
          </div>
        </div>

        {/* Middle: Cart and Fees */}
        <div className="lg:col-span-1 space-y-4">
          <POSCart
            items={cartItems}
            onQuantityChange={handleQuantityChange}
            onRemove={handleRemove}
            onClear={handleClear}
          />

          <div className="border rounded p-4">
            <FeeEditor fees={fees} onFeesChange={handleFeesChange} />
          </div>

          <PaymentMethodSelect value={paymentMethodId} onChange={setPaymentMethodId} />

          <div>
            <label className="block text-sm font-medium mb-1">Note (optional)</label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="border rounded px-3 py-2 w-full"
              rows={2}
              placeholder="Add a note to this sale..."
            />
          </div>
        </div>

        {/* Right: Breakdown and Confirm */}
        <div className="lg:col-span-1 space-y-4">
          {breakdown && (
            <SaleBreakdown
              items={breakdown.items}
              subtotal={breakdown.subtotal}
              fees={breakdown.fees}
              fees_total={breakdown.fees_total}
              vat_enabled={breakdown.vat_enabled}
              vat_rate={breakdown.vat_rate}
              vat_amount={breakdown.vat_amount}
              total={breakdown.total}
            />
          )}

          <ConfirmButton
            onConfirm={handleConfirm}
            disabled={!paymentMethodId || cartItems.length === 0}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
}