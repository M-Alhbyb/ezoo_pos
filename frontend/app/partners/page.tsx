"use client";
import { useState, useEffect } from "react";
import PartnerModal from "@/components/partners/PartnerModal";
import DistributeModal from "@/components/partners/DistributeModal";

interface Partner {
  id: string;
  name: string;
  share_percentage: number;
  investment_amount: number;
  created_at: string;
}

export default function PartnersPage() {
  const [partners, setPartners] = useState<Partner[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  
  const [isPartnerModalOpen, setIsPartnerModalOpen] = useState(false);
  const [isDistributeModalOpen, setIsDistributeModalOpen] = useState(false);
  const [isDistributing, setIsDistributing] = useState(false);
  const [distributionResult, setDistributionResult] = useState<any>(null);

  useEffect(() => {
    fetchPartners();
  }, []);

  const fetchPartners = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/partners");
      if (!response.ok) throw new Error("Failed to fetch partners");
      
      const data = await response.json();
      setPartners(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAddPartner = async (data: any) => {
    const response = await fetch("/api/partners", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Failed to add partner");
    }

    await fetchPartners();
    setIsPartnerModalOpen(false);
  };

  const handleDistribute = async (data: any) => {
    setIsDistributing(true);
    setDistributionResult(null);
    try {
      const response = await fetch("/api/partners/distribute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to distribute profits");
      }

      const result = await response.json();
      setDistributionResult(result);
      setIsDistributeModalOpen(false);
    } catch (err: any) {
      throw err;
    } finally {
      setIsDistributing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end mb-6">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">Partners</h1>
          <p className="text-slate-500 mt-1">Manage investment partners and distribute profits.</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => setIsDistributeModalOpen(true)}
            className="flex items-center px-4 py-2.5 bg-indigo-50 text-indigo-700 font-medium rounded-xl hover:bg-indigo-100 transition-all border border-indigo-200"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            Distribute Profits
          </button>
          <button 
            onClick={() => setIsPartnerModalOpen(true)}
            className="flex items-center px-4 py-2.5 bg-primary text-white font-medium rounded-xl hover:bg-blue-600 transition-all shadow-sm shadow-blue-200"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
            Add Partner
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl mb-4 border border-rose-200 animate-slide-up flex items-center shadow-sm">
          <svg className="w-5 h-5 mr-3 text-rose-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
          <span className="font-medium">{error}</span>
        </div>
      )}

      {distributionResult && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 shadow-sm animate-fade-in mb-6">
          <h3 className="text-lg font-bold text-emerald-800 mb-2 border-b border-emerald-100 pb-2">Distribution Successful</h3>
          <div className="flex gap-6 mb-4">
            <div>
              <div className="text-xs font-semibold text-emerald-600 uppercase tracking-wider">Total Profit Distributed</div>
              <div className="text-2xl font-bold text-emerald-900">${parseFloat(distributionResult.distributed_total || "0").toFixed(2)}</div>
            </div>
          </div>
          <div className="bg-white rounded-xl overflow-hidden border border-emerald-100">
            <table className="w-full text-left text-sm">
              <thead className="bg-emerald-50 text-emerald-800">
                <tr>
                  <th className="px-4 py-2 font-semibold">Partner</th>
                  <th className="px-4 py-2 font-semibold text-right">Percentage</th>
                  <th className="px-4 py-2 font-semibold text-right">Amount Received</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-emerald-50">
                {distributionResult.distributions.map((dist: any, idx: number) => (
                  <tr key={idx}>
                    <td className="px-4 py-3 font-medium text-slate-800">{dist.name}</td>
                    <td className="px-4 py-3 text-right text-slate-600">{parseFloat(dist.share_percentage).toFixed(2)}%</td>
                    <td className="px-4 py-3 text-right font-semibold text-emerald-700">${parseFloat(dist.amount).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="glass rounded-2xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400">
            <svg className="animate-spin w-8 h-8 mb-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="font-medium">Loading partners...</span>
          </div>
        ) : partners.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse animate-fade-in">
              <thead>
                <tr className="bg-slate-50/50 border-b border-slate-200">
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Partner Name</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Share Percentage (%)</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Investment Amount</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Joined</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white/50">
                {partners.map((partner) => (
                  <tr key={partner.id} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="px-6 py-4 font-medium text-slate-800">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-bold flex items-center justify-center text-xs">
                          {partner.name.charAt(0).toUpperCase()}
                        </div>
                        {partner.name}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right font-medium text-indigo-600">
                      {parseFloat(partner.share_percentage.toString()).toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 text-right font-medium text-slate-700">
                      ${parseFloat(partner.investment_amount.toString()).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-right text-sm text-slate-500">
                      {new Date(partner.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-24 text-slate-400 animate-fade-in">
            <svg className="w-16 h-16 mb-4 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
            <div className="text-lg font-medium text-slate-600 mb-1">No partners</div>
            <p className="text-sm">Add investment partners to start tracking distributions.</p>
          </div>
        )}
      </div>

      <PartnerModal 
        isOpen={isPartnerModalOpen}
        onClose={() => setIsPartnerModalOpen(false)}
        onSubmit={handleAddPartner}
      />
      
      <DistributeModal
        isOpen={isDistributeModalOpen}
        onClose={() => setIsDistributeModalOpen(false)}
        onSubmit={handleDistribute}
        loading={isDistributing}
      />
    </div>
  );
}
