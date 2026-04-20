/**
 * SaleBreakdown Component
 * 
 * Display financial breakdown with subtotal, fees, VAT, and total.
 * Task: T073
 */

"use client";

interface BreakdownItem {
  product_name: string;
  quantity: number;
  unit_price: string;
  line_total: string;
}

interface BreakdownFee {
  fee_label: string;
  fee_value: string;
  fee_value_type: string;
  calculated_amount: string;
}

interface SaleBreakdownProps {
  items: BreakdownItem[];
  subtotal: string;
  fees: BreakdownFee[];
  fees_total: string;
  vat_enabled: boolean;
  vat_rate: string | null;
  vat_amount: string | null;
  total: string;
}

export default function SaleBreakdown({
  items,
  subtotal,
  fees,
  fees_total,
  vat_enabled,
  vat_rate,
  vat_amount,
  total,
}: SaleBreakdownProps) {
  return (
    <div className="border rounded p-4 space-y-4">
      <h3 className="font-medium text-lg">Financial Breakdown</h3>

      {/* Line Items */}
      <div className="space-y-2">
        <div className="text-sm font-medium text-gray-700">Items:</div>
        {items.map((item, index) => (
          <div key={index} className="flex justify-between text-sm pl-4">
            <div>
              {item.product_name} × {item.quantity}
              <span className="text-gray-500 ml-2">(@ ${item.unit_price})</span>
            </div>
            <div>${item.line_total}</div>
          </div>
        ))}
      </div>

      {/* Subtotal */}
      <div className="flex justify-between font-medium pt-2 border-t">
        <div>Subtotal:</div>
        <div>${subtotal}</div>
      </div>

      {/* Fees */}
      {fees.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-gray-700">Fees:</div>
          {fees.map((fee, index) => (
            <div key={index} className="flex justify-between text-sm pl-4">
              <div>
                {fee.fee_label}
                <span className="text-gray-500 ml-2">
                  ({fee.fee_value_type === "percent" ? `${fee.fee_value}%` : `$${fee.fee_value}`})
                </span>
              </div>
              <div>${fee.calculated_amount}</div>
            </div>
          ))}
          <div className="flex justify-between text-sm pl-4 font-medium">
            <div>Total Fees:</div>
            <div>${fees_total}</div>
          </div>
        </div>
      )}

      {/* VAT */}
      {vat_enabled && vat_amount && vat_rate && (
        <div className="flex justify-between text-sm">
          <div>VAT ({vat_rate}%):</div>
          <div>${vat_amount}</div>
        </div>
      )}

      {/* Grand Total */}
      <div className="flex justify-between font-bold text-lg pt-2 border-t">
        <div>Total:</div>
        <div>${total}</div>
      </div>
    </div>
  );
}