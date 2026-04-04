/**
 * POSCart Component
 * 
 * Shopping cart with quantity editing and item removal.
 * Task: T071
 */

"use client";

import { useState } from "react";

interface CartItem {
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: number;
}

interface POSCartProps {
  items: CartItem[];
  onQuantityChange: (product_id: string, quantity: number) => void;
  onRemove: (product_id: string) => void;
  onClear: () => void;
}

export default function POSCart({ items, onQuantityChange, onRemove, onClear }: POSCartProps) {
  const lineTotals = items.map((item) => ({
    ...item,
    line_total: item.quantity * item.unit_price,
  }));

  const subtotal = lineTotals.reduce((sum, item) => sum + item.line_total, 0);

  return (
    <div className="border rounded p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-medium">Cart</h2>
        {items.length > 0 && (
          <button
            onClick={onClear}
            className="text-sm text-red-600 hover:text-red-800"
          >
            Clear All
          </button>
        )}
      </div>

      {items.length === 0 ? (
        <div className="text-gray-500 text-center py-8">Cart is empty</div>
      ) : (
        <div className="space-y-3">
          {lineTotals.map((item) => (
            <div key={item.product_id} className="border-b pb-3 last:border-b-0">
              <div className="flex justify-between items-start mb-2">
                <div className="flex-1">
                  <div className="font-medium">{item.product_name}</div>
                  <div className="text-sm text-gray-500">${item.unit_price.toFixed(2)} each</div>
                </div>
                <button
                  onClick={() => onRemove(item.product_id)}
                  className="text-red-600 hover:text-red-800 text-sm"
                >
                  Remove
                </button>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <label className="text-sm">Qty:</label>
                  <input
                    type="number"
                    min="1"
                    value={item.quantity}
                    onChange={(e) => onQuantityChange(item.product_id, parseInt(e.target.value) || 1)}
                    className="border rounded px-2 py-1 w-20 text-sm"
                  />
                </div>
                <div className="font-medium">${item.line_total.toFixed(2)}</div>
              </div>
            </div>
          ))}

          <div className="border-t pt-3 mt-3">
            <div className="flex justify-between items-center font-medium text-lg">
              <div>Subtotal:</div>
              <div>${subtotal.toFixed(2)}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}