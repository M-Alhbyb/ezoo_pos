"use client";

import React, { useState, useEffect } from "react";
import { Users, Landmark, Wallet, History, Calendar } from "lucide-react";
import { DataTable, Column } from "@/components/reports/DataTable";
import { ExportButtonGroup } from "@/components/reports/ExportButtonGroup";

interface PartnerPayoutData {
  partner_id: string;
  partner_name: string;
  total_payout: number;
}

interface PartnerReportResponse {
  total_payout: number;
  payouts_by_partner: PartnerPayoutData[];
  total: number;
  page: number;
  page_size: number;
}

export default function PartnersReportPage() {
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [reportData, setReportData] = useState<PartnerReportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 15;

  useEffect(() => {
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 90); // Default to a quarter for partners
    
    setStartDate(thirtyDaysAgo.toISOString().split("T")[0]);
    setEndDate(today.toISOString().split("T")[0]);
  }, []);

  useEffect(() => {
    if (startDate && endDate) {
      fetchReportData();
    }
  }, [startDate, endDate, page]);

  const fetchReportData = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate,
        page: page.toString(),
        page_size: pageSize.toString()
      });
      const response = await fetch(`/api/reports/partners?${params}`);
      const data = await response.json();
      setReportData(data);
    } catch (error) {
      console.error("Partners report fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns: Column<PartnerPayoutData>[] = [
    { header: "Partner Name", accessor: "partner_name", className: "font-bold text-slate-900" },
    { 
      header: "Total Payouts", 
      accessor: "total_payout", 
      render: (item) => <span className="text-emerald-600 font-bold">${item.total_payout.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span> 
    },
    { 
      header: "Activity", 
      accessor: "partner_id", 
      render: (item) => (
        <div className="p-2 w-fit bg-slate-100 rounded-lg">
           <History className="w-4 h-4 text-slate-500" />
        </div>
      )
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-extrabold font-heading text-slate-900 tracking-tight">Partner Dividends</h1>
          <p className="text-slate-500 mt-2 font-medium">Historical payout tracking and distribution analytics per investor.</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex items-center gap-2 bg-white p-2.5 rounded-2xl shadow-sm border border-slate-100">
            <Calendar className="w-4 h-4 text-slate-400 ml-2" />
            <input 
              type="date" 
              value={startDate} 
              onChange={e => { setStartDate(e.target.value); setPage(1); }}
              className="bg-transparent border-none focus:ring-0 text-sm font-bold text-slate-700 cursor-pointer" 
            />
            <span className="text-slate-300 font-bold">→</span>
            <input 
              type="date" 
              value={endDate} 
              onChange={e => { setEndDate(e.target.value); setPage(1); }}
              className="bg-transparent border-none focus:ring-0 text-sm font-bold text-slate-700 cursor-pointer" 
            />
          </div>
          <ExportButtonGroup reportType="inventory" startDate={startDate} endDate={endDate} />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="glass-p-6 bg-slate-900 text-white rounded-[2rem] p-8 shadow-2xl relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/20 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-700"></div>
          <p className="text-blue-400 text-xs font-bold uppercase tracking-widest mb-4">Total Distributed</p>
          <h3 className="text-4xl font-extrabold tracking-tight">${reportData?.total_payout.toLocaleString(undefined, { minimumFractionDigits: 2 }) || "0.00"}</h3>
          <div className="mt-8 flex items-center gap-3 text-slate-400 text-sm">
             <Landmark className="w-5 h-5 text-blue-400" />
             <span>Across all active partners</span>
          </div>
        </div>

        <div className="glass-card p-8 hover:shadow-xl transition-all duration-300 border border-slate-100 flex flex-col justify-center">
          <div className="p-3 bg-emerald-100/50 text-emerald-600 rounded-2xl w-fit mb-4">
             <Users className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Active Partners</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">{reportData?.payouts_by_partner.length || 0}</h3>
        </div>

        <div className="glass-card p-8 hover:shadow-xl transition-all duration-300 border border-slate-100 flex flex-col justify-center">
          <div className="p-3 bg-indigo-100/50 text-indigo-600 rounded-2xl w-fit mb-4">
             <Wallet className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Avg. Payout</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">
             ${reportData?.payouts_by_partner.length ? (reportData.total_payout / reportData.payouts_by_partner.length).toLocaleString(undefined, { minimumFractionDigits: 2 }) : "0.00"}
          </h3>
        </div>
      </div>

      <div className="space-y-4">
        <DataTable 
          columns={columns} 
          data={reportData?.payouts_by_partner || []} 
          loading={loading}
          totalItems={reportData?.total || 0}
          pageSize={pageSize}
          currentPage={page}
          onPageChange={setPage}
        />
      </div>
    </div>
  );
}
