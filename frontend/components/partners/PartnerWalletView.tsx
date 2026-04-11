/**
 * PartnerWalletView Component
 * 
 * Displays partner wallet balance and transaction history.
 * Task: T046 - Phase 7
 */

"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";

interface WalletBalance {
  partner_id: string;
  partner_name: string;
  current_balance: string;
  last_transaction_at: string | null;
}

interface Transaction {
  id: string;
  amount: string;
  transaction_type: 'sale_profit' | 'manual_adjustment';
  reference_id: string | null;
  reference_type: string | null;
  description: string | null;
  balance_after: string;
  created_at: string;
}

interface PartnerWalletViewProps {
  partnerId: string;
  partnerName: string;
  onRefresh?: () => void;
}

export default function PartnerWalletView({
  partnerId,
  partnerName,
  onRefresh,
}: PartnerWalletViewProps) {
  const [balance, setBalance] = useState<WalletBalance | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [limit, setLimit] = useState(10);

  useEffect(() => {
    fetchWalletData();
  }, [partnerId, limit]);

  const fetchWalletData = async () => {
    try {
      setLoading(true);
      const [balanceRes, transactionsRes] = await Promise.all([
        fetch(`http://localhost:8000/api/v1/partners/${partnerId}/wallet`),
        fetch(`http://localhost:8000/api/v1/partners/${partnerId}/wallet/transactions?limit=${limit}`),
      ]);

      if (!balanceRes.ok || !transactionsRes.ok) {
        throw new Error("فشل في جلب البيانات");
      }

      const balanceData = await balanceRes.json();
      const transactionsData = await transactionsRes.json();

      setBalance(balanceData);
      setTransactions(transactionsData.transactions || []);
    } catch (err: any) {
      setError(err.message || "حدث خطأ");
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (amount: string) => {
    return new Intl.NumberFormat('ar-EG', {
      style: 'currency',
      currency: 'EGP',
    }).format(parseFloat(amount));
  };

  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat('ar-EG', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(dateString));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center p-12">
        <div className="text-slate-500">جارٍ التحميل...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-rose-50 rounded-xl p-4 text-rose-600">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Balance Card */}
      <div className="bg-gradient-to-br from-primary to-primary/80 rounded-xl p-6 text-white">
        <div className="text-sm opacity-90 mb-1">الرصيد الحالي</div>
        <div className="text-3xl font-bold mb-2">
          {balance ? formatAmount(balance.current_balance) : formatAmount('0.00')}
        </div>
        <div className="text-sm opacity-75">
          {partnerName}
          {balance?.last_transaction_at && (
            <> • آخر معاملة: {formatDate(balance.last_transaction_at)}</>
          )}
        </div>
      </div>

      {/* Transaction History */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-slate-800">
            سجل المعاملات
          </h2>
          <div className="flex gap-2">
            <select
              value={limit}
              onChange={(e) => setLimit(parseInt(e.target.value))}
              className="bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-sm"
            >
              <option value={10}>آخر 10</option>
              <option value={25}>آخر 25</option>
              <option value={50}>آخر 50</option>
              <option value={100}>آخر 100</option>
            </select>
            {onRefresh && (
              <button
                onClick={onRefresh}
                className="bg-slate-100 text-slate-600 px-3 py-1.5 rounded-lg hover:bg-slate-200 transition-colors text-sm"
              >
                تحديث
              </button>
            )}
          </div>
        </div>

        {transactions.length === 0 ? (
          <div className="text-center py-8 text-slate-500 bg-slate-50 rounded-xl">
            لا توجد معاملات بعد
          </div>
        ) : (
          <div className="space-y-2">
            {transactions.map((tx) => (
              <div
                key={tx.id}
                className="bg-white border border-slate-200 rounded-xl p-4"
              >
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1">
                    <div className="font-medium text-slate-800">
                      {tx.transaction_type === 'sale_profit' ? 'ربح من مبيعات' : 'تسوية يدوية'}
                    </div>
                    {tx.description && (
                      <div className="text-sm text-slate-500 mt-1">
                        {tx.description}
                      </div>
                    )}
                  </div>
                  <div className="text-left">
                    <div className={`font-bold ${
                      parseFloat(tx.amount) >= 0 ? 'text-green-600' : 'text-rose-600'
                    }`}>
                      {parseFloat(tx.amount) >= 0 ? '+' : ''}{formatAmount(tx.amount)}
                    </div>
                    <div className="text-xs text-slate-400">
                      الرصيد: {formatAmount(tx.balance_after)}
                    </div>
                  </div>
                </div>
                <div className="text-xs text-slate-400">
                  {formatDate(tx.created_at)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}