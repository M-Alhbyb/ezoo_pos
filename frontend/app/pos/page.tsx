"use client";

import { useState } from "react";
import { Decimal } from "decimal.js";
import { ARABIC } from "@/lib/constants/arabic";

// Components
import ProductGrid from "@/components/pos/ProductGrid";
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
  stock_quantity: number;
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
    let newItems;

    if (existingItem) {
      // Check if we can add more
      if (existingItem.quantity >= product.stock_quantity) {
        setError(`${ARABIC.pos.outOfStock || 'لايوجد كمية كافية'}: ${product.name}`);
        return;
      }
      // Increment quantity
      newItems = cartItems.map((item) =>
        item.product_id === product.id ? { ...item, quantity: item.quantity + 1 } : item
      );
    } else {
      // Add new item
      if (product.stock_quantity <= 0) {
        setError(`${ARABIC.pos.outOfStock || 'لايوجد كمية كافية'}: ${product.name}`);
        return;
      }
      const newItem: CartItem = {
        product_id: product.id,
        product_name: product.name,
        quantity: 1,
        unit_price: parseFloat(product.selling_price),
        stock_quantity: product.stock_quantity,
      };
      newItems = [...cartItems, newItem];
    }
    
    setCartItems(newItems);
    await calculateBreakdown(newItems, fees);
  };

  // Change quantity
  const handleQuantityChange = async (product_id: string, quantity: number) => {
    const newItems = cartItems.map((item) => {
      if (item.product_id === product_id) {
        const validatedQuantity = Math.min(Math.max(1, quantity), item.stock_quantity);
        return { ...item, quantity: validatedQuantity };
      }
      return item;
    });
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
    <div className="space-y-6">
      <div className="flex justify-between items-end mb-4">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.pos.title}</h1>
          <p className="text-slate-500 mt-1">{ARABIC.pos.subtitle || 'معالجة عملية جديدة'}</p>
        </div>
      </div>

      {success && (
        <div className="bg-emerald-50 text-emerald-700 px-4 py-3 rounded-xl mb-4 border border-emerald-200 animate-slide-up flex items-center shadow-sm">
          <svg className="w-5 h-5 me-3 text-emerald-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"></path></svg>
          <span className="font-medium">{ARABIC.pos.saleComplete}</span>
        </div>
      )}

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl mb-4 border border-rose-200 animate-slide-up flex items-center shadow-sm">
          <svg className="w-5 h-5 me-3 text-rose-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left/Middle Column (Search & Cart) */}
        <div className="lg:col-span-8 space-y-6">
          <div className="glass p-6 rounded-2xl relative overflow-hidden">
            <div className="absolute top-0 start-0 -mt-20 -ms-20 w-64 h-64 bg-primary/5 rounded-full blur-3xl pointer-events-none"></div>
            
            <div className="relative mb-6">
              <h2 className="text-xl font-bold text-slate-800 flex items-center">
                <div className="p-2 bg-primary/10 rounded-lg me-3 text-primary">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M4 6h16M4 12h16m-7 6h7"></path></svg>
                </div>
                {ARABIC.pos.quickSelect || 'الاختيار السريع'}
              </h2>
              <p className="text-sm text-slate-500 me-12 mt-0.5">{ARABIC.pos.clickToAdd || 'انقر على منتج لإضافته إلى السلة'}</p>
            </div>

            <ProductGrid onProductSelect={handleProductSelect} />
          </div>

          <div className="glass p-6 rounded-2xl relative overflow-hidden">
             {/* Decorative Background */}
            <div className="absolute top-0 start-0 -mt-10 -ms-10 w-40 h-40 bg-blue-100/50 rounded-full blur-3xl pointer-events-none"></div>
            
            <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
              <svg className="w-5 h-5 me-2 text-indigo-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
              {ARABIC.pos.currentCart || 'السلة الحالية'}
            </h2>
            <POSCart
              items={cartItems}
              onQuantityChange={handleQuantityChange}
              onRemove={handleRemove}
              onClear={handleClear}
            />
          </div>
        </div>

        {/* Right Column (Checkout/Breakdown) */}
        <div className="lg:col-span-4 space-y-6">
          <div className="glass p-6 rounded-2xl relative overflow-hidden">
            <div className="absolute top-0 start-0 -mt-10 -ms-10 w-32 h-32 bg-emerald-100/40 rounded-full blur-3xl pointer-events-none"></div>

            <h2 className="text-lg font-semibold text-slate-800 mb-4 border-b border-slate-100 pb-3 flex items-center">
              <svg className="w-5 h-5 me-2 text-emerald-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              {ARABIC.pos.orderSummary || 'ملخص الطلب'}
            </h2>
            
            <div className="space-y-5">
              {breakdown ? (
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
              ) : (
                <div className="py-8 text-center text-slate-400 text-sm">
                  {ARABIC.pos.cartEmpty}
                </div>
              )}

              <div className="pt-4 border-t border-slate-100 space-y-4">
                <FeeEditor fees={fees} onFeesChange={handleFeesChange} />
                
                <PaymentMethodSelect value={paymentMethodId} onChange={setPaymentMethodId} />

                <div>
                  <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">{ARABIC.pos.note || 'ملاحظة'} (اختياري)</label>
                  <textarea
                    value={note}
                    onChange={(e) => setNote(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 p-3 h-20 transition-all resize-none shadow-sm"
                    placeholder={ARABIC.pos.addRemark || 'أضف ملاحظة...'}
                  />
                </div>
              </div>

              <div className="pt-4">
                <ConfirmButton
                  onConfirm={handleConfirm}
                  disabled={!paymentMethodId || cartItems.length === 0}
                  loading={loading}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}