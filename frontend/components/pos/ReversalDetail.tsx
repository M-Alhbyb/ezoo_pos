"use client";

import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";

interface ReversalDetailProps {
  saleAmount: number;
  customerName?: string;
  customerBalance?: number;
}

export default function ReversalDetail({ saleAmount, customerName, customerBalance }: ReversalDetailProps) {
  if (!customerName) return null;

  const impact = customerBalance !== undefined ? saleAmount : undefined;

  return (
    <div className="space-y-4">
      <div className="bg-rose-50 border border-rose-200 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-2">
          <svg className="w-5 h-5 text-rose-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 15L12 19L8 15M12 19V5"></path>
          </svg>
          <span className="font-bold text-rose-800">تأثير الإلغاء على العميل</span>
        </div>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-rose-600">العميل:</span>
            <span className="font-bold text-slate-800">{customerName}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-rose-600">مبلغ الإلغاء:</span>
            <span className="font-bold text-rose-600">-{formatCurrency(saleAmount)}</span>
          </div>
          {impact !== undefined && (
            <div className="flex justify-between border-t border-rose-200 pt-2 mt-2">
              <span className="text-rose-600">الرصيد الجديد:</span>
              <span className={`font-bold ${customerBalance! - saleAmount >= 0 ? 'text-emerald-600' : 'text-rose-600'}`}>
                {formatCurrency(customerBalance! - saleAmount)}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}