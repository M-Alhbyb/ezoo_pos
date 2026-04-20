/**
 * SaleBreakdown Component
 * 
 * Display financial breakdown with subtotal, fees, VAT, and total.
 * Task: T073
 */

"use client";

import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";

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
      <h3 className="font-medium text-lg">{ARABIC.pos.financialBreakdown || 'تفصيل مالي'}</h3>

      {/* Line Items */}
      <div className="space-y-2">
        <div className="text-sm font-medium text-slate-700">{ARABIC.pos.items || 'المنتجات'}:</div>
        {items.map((item, index) => (
          <div key={index} className="flex justify-between text-sm ps-4">
            <div>
              {item.product_name} × {item.quantity}
              <span className="text-slate-500 ms-2">({ARABIC.pos.at || '@'} {formatCurrency(item.unit_price)})</span>
            </div>
            <div>{formatCurrency(item.line_total)}</div>
          </div>
        ))}
      </div>

      {/* Subtotal */}
      <div className="flex justify-between font-medium pt-2 border-t">
        <div>{ARABIC.pos.subtotal || 'المجموع الفرعي'}:</div>
        <div>{formatCurrency(subtotal)}</div>
      </div>

      {/* Fees */}
      {fees.length > 0 && (
        <div className="space-y-2">
          <div className="text-sm font-medium text-slate-700">{ARABIC.pos.fees || 'الرسوم'}:</div>
          {fees.map((fee, index) => (
            <div key={index} className="flex justify-between text-sm ps-4">
              <div>
                {fee.fee_label}
                <span className="text-slate-500 ms-2">
                  ({fee.fee_value_type === "percent" ? `${fee.fee_value}%` : formatCurrency(fee.fee_value)})
                </span>
              </div>
              <div>{formatCurrency(fee.calculated_amount)}</div>
            </div>
          ))}
          <div className="flex justify-between text-sm ps-4 font-medium">
            <div>{ARABIC.pos.totalFees || 'إجمالي الرسوم'}:</div>
            <div>{formatCurrency(fees_total)}</div>
          </div>
        </div>
      )}

      {/* VAT */}
      {vat_enabled && vat_amount && vat_rate && (
        <div className="flex justify-between text-sm">
          <div>{ARABIC.pos.vat || 'ضريبة القيمة المضافة'} ({vat_rate}%):</div>
          <div>{formatCurrency(vat_amount)}</div>
        </div>
      )}

      {/* Grand Total */}
      <div className="flex justify-between font-bold text-lg pt-2 border-t">
        <div>{ARABIC.pos.grandTotal || 'الإجمالي الكلي'}:</div>
        <div>{formatCurrency(total)}</div>
      </div>
    </div>
  );
}