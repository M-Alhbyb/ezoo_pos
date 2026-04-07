"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDateTime } from "@/lib/utils/format";
import { ArrowRight, User, TrendingUp, Calendar } from "lucide-react";

interface Distribution {
  id: string;
  project_name: string;
  amount: string;
  distributed_at: string;
}

interface Partner {
  id: string;
  name: string;
  share_percentage: number;
  investment_amount: string;
  created_at: string;
  distributions: Distribution[];
}

export default function PartnerHistoryPage({ params }: { params: Promise<{ partnerId: string }> }) {
  const resolvedParams = use(params);
  const [partner, setPartner] = useState<Partner | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchPartner();
  }, [resolvedParams.partnerId]);

  const fetchPartner = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/partners/${resolvedParams.partnerId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(ARABIC.partners.partnerNotFound || 'الشريك غير موجود');
        }
        throw new Error(ARABIC.common.error);
      }

      const data = await response.json();
      setPartner(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <Link href="/partners" className="text-sm text-primary hover:text-primary/80 mb-2 inline-flex items-center gap-1">
            <ArrowRight className="w-4 h-4 rtl:rotate-180" />
            {ARABIC.partners.title}
          </Link>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.partners.partnerHistory || 'سجل الشريك'}</h1>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl border border-rose-200 flex items-center">
          <ArrowRight className="w-5 h-5 me-3 text-rose-500" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
          <p className="text-slate-500 mt-4">{ARABIC.common.loading}</p>
        </div>
      ) : partner ? (
        <>
          {/* Partner Header */}
          <div className="glass p-6 rounded-2xl">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-16 h-16 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-2xl">
                {partner.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-800">{partner.name}</h2>
                <p className="text-sm text-slate-500 font-mono">{partner.id}</p>
              </div>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
              <div className="bg-slate-50 p-4 rounded-xl">
                <p className="text-xs font-semibold text-slate-500 uppercase">{ARABIC.partners.sharePercentage}</p>
                <p className="text-2xl font-bold text-indigo-600">{parseFloat(partner.share_percentage.toString()).toFixed(2)}%</p>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl">
                <p className="text-xs font-semibold text-slate-500 uppercase">{ARABIC.partners.investmentAmount}</p>
                <p className="text-2xl font-bold text-slate-800">{formatCurrency(partner.investment_amount)}</p>
              </div>
              <div className="bg-slate-50 p-4 rounded-xl">
                <p className="text-xs font-semibold text-slate-500 uppercase">{ARABIC.common.createdAt}</p>
                <p className="text-lg font-medium text-slate-800">{formatDateTime(partner.created_at)}</p>
              </div>
            </div>
          </div>

          {/* Distribution History */}
          <div className="glass rounded-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-emerald-500" />
                {ARABIC.partners.distributionHistory || 'سجل التوزيعات'}
              </h3>
            </div>
            {!partner.distributions || partner.distributions.length === 0 ? (
              <div className="p-8 text-center text-slate-400">
                <Calendar className="w-12 h-12 mx-auto mb-3 text-slate-200" />
                <p>{ARABIC.partners.noDistributions || 'لا توجد توزيعات بعد'}</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-100">
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">{ARABIC.projects.projectName || 'المشروع'}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{ARABIC.partners.amountReceived}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{ARABIC.common.createdAt}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {partner.distributions.map((dist) => (
                      <tr key={dist.id} className="hover:bg-slate-50/50">
                        <td className="px-6 py-4 font-medium text-slate-800">{dist.project_name}</td>
                        <td className="px-6 py-4 text-end font-semibold text-emerald-600">{formatCurrency(dist.amount)}</td>
                        <td className="px-6 py-4 text-end text-sm text-slate-500">{formatDateTime(dist.distributed_at)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}