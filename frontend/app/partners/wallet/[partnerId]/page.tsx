/**
 * Partner Wallet Page
 * 
 * Page for viewing partner wallet balance and transaction history.
 * Task: T048 - Phase 7
 */

"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import PartnerWalletView from "@/components/partners/PartnerWalletView";

interface Partner {
  id: string;
  name: string;
  share_percentage: string;
  investment_amount: string;
}

export default function PartnerWalletPage({ params }: { params: { partnerId: string } }) {
  const router = useRouter();
  const { partnerId } = params;
  const [partner, setPartner] = useState<Partner | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [adjustMode, setAdjustMode] = useState(false);
  const [adjustAmount, setAdjustAmount] = useState("");
  const [adjustDescription, setAdjustDescription] = useState("");
  const [adjusting, setAdjusting] = useState(false);

  useEffect(() => {
    fetchPartner();
  }, [partnerId]);

  const fetchPartner = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `/api/v1/partners/${partnerId}`
      );

      if (!response.ok) {
        throw new Error("فشل في جلب بيانات الشريك");
      }

      const data = await response.json();
      setPartner(data);
    } catch (err: any) {
      setError(err.message || "حدث خطأ");
    } finally {
      setLoading(false);
    }
  };

  const handleAdjustWallet = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!adjustAmount || !adjustDescription) {
      alert("يرجى ملء جميع الحقول");
      return;
    }

    try {
      setAdjusting(true);
      const response = await fetch(
        `/api/v1/partners/${partnerId}/wallet/adjust`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            amount: parseFloat(adjustAmount),
            description: adjustDescription,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "فشل في تعديل المحفظة");
      }

      setAdjustMode(false);
      setAdjustAmount("");
      setAdjustDescription("");
      await fetchPartner();
      alert("تم تعديل المحفظة بنجاح");
    } catch (err: any) {
      alert(err.message || "حدث خطأ");
    } finally {
      setAdjusting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-slate-500">جارٍ التحميل...</div>
      </div>
    );
  }

  if (error || !partner) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-rose-50 border border-rose-200 text-rose-600 rounded-xl p-4">
          {error || "الشريك غير موجود"}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.back()}
          className="text-slate-600 hover:text-slate-800 mb-4 inline-flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          العودة للشركاء
        </button>
        
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-slate-800">{partner.name}</h1>
              <div className="text-slate-500 mt-1">
                نسبة الربح: {partner.share_percentage}%
              </div>
              <div className="text-slate-400 text-sm mt-1">
                الاستثمار: {new Intl.NumberFormat('ar-EG', { style: 'currency', currency: 'EGP' }).format(parseFloat(partner.investment_amount))}
              </div>
            </div>
            <button
              onClick={() => setAdjustMode(true)}
              className="bg-primary text-white px-4 py-2 rounded-xl hover:bg-primary/90 transition-colors"
            >
              تعديل المحفظة
            </button>
          </div>
        </div>
      </div>

      {/* Adjustment Modal */}
      {adjustMode && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold text-slate-800 mb-4">تعديل رصيد المحفظة</h2>
            <form onSubmit={handleAdjustWallet} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">
                  المبلغ (إيجابي للإضافة، سلبي للخصم)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={adjustAmount}
                  onChange={(e) => setAdjustAmount(e.target.value)}
                  className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
                  placeholder="مثال: 100 أو -50"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">
                  السبب
                </label>
                <textarea
                  value={adjustDescription}
                  onChange={(e) => setAdjustDescription(e.target.value)}
                  className="w-full bg-slate-50/50 border border-slate-200 text-slate-800 text-sm rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary p-2.5 transition-all outline-none"
                  placeholder="مثال: تسوية مارس 2026"
                  required
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={adjusting}
                  className="flex-1 bg-primary text-white py-2 px-4 rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50"
                >
                  {adjusting ? "جارٍ الحفظ..." : "حفظ"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setAdjustMode(false);
                    setAdjustAmount("");
                    setAdjustDescription("");
                  }}
                  className="px-4 py-2 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 transition-colors"
                >
                  إلغاء
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Wallet View */}
      <PartnerWalletView
        partnerId={partnerId}
        partnerName={partner.name}
        onRefresh={fetchPartner}
      />
    </div>
  );
}