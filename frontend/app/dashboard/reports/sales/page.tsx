"use client";

import React, { useState, useEffect } from "react";
import { TrendingUp, ShoppingBag, DollarSign, PieChart as PieIcon, Calendar } from "lucide-react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";
import { DataTable, Column } from "@/components/reports/DataTable";
import { ExportButtonGroup } from "@/components/reports/ExportButtonGroup";

interface SalesData {
  date: string;
  count: number;
  revenue: number;
  cost: number;
  profit: number;
}

interface SalesReportResponse {
  total_revenue: number;
  total_cost: number;
  total_profit: number;
  sales_count: number;
  daily_breakdown: SalesData[];
  total: number;
  page: number;
  page_size: number;
}

export default function SalesReportPage() {
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [reportData, setReportData] = useState<SalesReportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 15;

  useEffect(() => {
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
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
      const response = await fetch(`/api/reports/sales?${params}`);
      const data = await response.json();
      setReportData(data);
    } catch (error) {
      console.error("Sales report fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns: Column<SalesData>[] = [
    { header: ARABIC.reports.sales.date, accessor: "date", className: "font-bold" },
    { header: ARABIC.reports.sales.salesCount || 'العدد', accessor: "count", render: (item) => <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded-lg text-xs font-bold">{item.count}</span> },
    { header: ARABIC.reports.sales.totalRevenue, accessor: "revenue", render: (item) => <span className="text-blue-600 font-bold">{formatCurrency(item.revenue)}</span> },
    { header: ARABIC.reports.sales.netProfit, accessor: "profit", render: (item) => <span className={`font-bold ${item.profit >= 0 ? "text-emerald-600" : "text-rose-600"}`}>{formatCurrency(item.profit)}</span> },
    { 
      header: ARABIC.reports.sales.avgMargin, 
      accessor: "margin", 
      render: (item) => {
        const margin = item.revenue > 0 ? (item.profit / item.revenue) * 100 : 0;
        return <span className="text-slate-500 text-xs font-semibold">{margin.toFixed(1)}%</span>
      }
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-extrabold font-heading text-slate-900 tracking-tight">{ARABIC.reports.sales.title}</h1>
          <p className="text-slate-500 mt-2 font-medium">{ARABIC.reports.sales.subtitle}</p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex items-center gap-2 bg-white p-2.5 rounded-2xl shadow-sm border border-slate-100">
            <Calendar className="w-4 h-4 text-slate-400 ms-2" />
            <input 
              type="date" 
              value={startDate} 
              onChange={e => { setStartDate(e.target.value); setPage(1); }}
              className="bg-transparent border-none focus:ring-0 text-sm font-bold text-slate-700 cursor-pointer" 
            />
            <span className="text-slate-300 font-bold">←</span>
            <input 
              type="date" 
              value={endDate} 
              onChange={e => { setEndDate(e.target.value); setPage(1); }}
              className="bg-transparent border-none focus:ring-0 text-sm font-bold text-slate-700 cursor-pointer" 
            />
          </div>
          <ExportButtonGroup reportType="sales" startDate={startDate} endDate={endDate} />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card p-6 bg-gradient-to-br from-blue-50/50 to-white hover:shadow-xl transition-all duration-300 border border-blue-100/50">
          <div className="p-3 bg-blue-100/50 text-blue-600 rounded-2xl w-fit mb-4">
            <TrendingUp className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">{ARABIC.reports.sales.totalRevenue}</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">{formatCurrency(reportData?.total_revenue || 0)}</h3>
        </div>

        <div className="glass-card p-6 bg-gradient-to-br from-emerald-50/50 to-white hover:shadow-xl transition-all duration-300 border border-emerald-100/50">
          <div className="p-3 bg-emerald-100/50 text-emerald-600 rounded-2xl w-fit mb-4">
            <DollarSign className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">{ARABIC.reports.sales.netProfit}</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">{formatCurrency(reportData?.total_profit || 0)}</h3>
        </div>

        <div className="glass-card p-6 bg-gradient-to-br from-indigo-50/50 to-white hover:shadow-xl transition-all duration-300 border border-indigo-100/50">
          <div className="p-3 bg-indigo-100/50 text-indigo-600 rounded-2xl w-fit mb-4">
            <ShoppingBag className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">{ARABIC.reports.sales.salesCount}</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">{reportData?.sales_count || 0}</h3>
        </div>

        <div className="glass-card p-6 bg-gradient-to-br from-purple-50/50 to-white hover:shadow-xl transition-all duration-300 border border-purple-100/50">
          <div className="p-3 bg-purple-100/50 text-purple-600 rounded-2xl w-fit mb-4">
            <PieIcon className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">{ARABIC.reports.sales.avgMargin}</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">
            {reportData?.total_revenue && reportData.total_revenue > 0
              ? ((reportData.total_profit / reportData.total_revenue) * 100).toFixed(1)
              : "0.0"}%
          </h3>
        </div>
      </div>

      {/* Main Table */}
      <div className="space-y-4">
        <div className="flex items-center justify-between px-2">
            <h2 className="text-xl font-bold text-slate-800">{ARABIC.reports.sales.dailyStatistics}</h2>
        </div>
        <DataTable 
          columns={columns} 
          data={reportData?.daily_breakdown || []} 
          loading={loading}
          totalItems={reportData?.total || 0}
          pageSize={pageSize}
          currentPage={page}
          onPageChange={setPage}
          emptyMessage={ARABIC.reports.noData || 'لا توجد بيانات'}
        />
      </div>
    </div>
  );
}