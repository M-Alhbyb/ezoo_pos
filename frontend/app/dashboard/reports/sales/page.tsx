"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import { TrendingUp, ShoppingBag, DollarSign, PieChart as PieIcon, Calendar, Eye, Activity, ListFilter, ArrowDownNarrowWide } from "lucide-react";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency } from "@/lib/utils/format";
import { DataTable, Column } from "@/components/reports/DataTable";
import { ExportButtonGroup } from "@/components/reports/ExportButtonGroup";
import SaleDetailModal from "@/components/reports/SaleDetailModal";

interface SalesData {
  date: string;
  count: number;
  revenue: number;
  cost: number;
  profit: number;
}

interface Sale {
  id: string;
  payment_method_name: string;
  created_at: string;
  grand_total: number;
  profit: number;
}

interface SalesReportResponse {
  total_revenue: number;
  total_cost: number;
  total_profit: number;
  sales_count: number;
  daily_breakdown: SalesData[];
}

export default function SalesReportPage() {
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [reportData, setReportData] = useState<SalesReportResponse | null>(null);
  const [summaryLoading, setSummaryLoading] = useState(false);
  
  // Transactions State (Infinite Scroll)
  const [transactions, setTransactions] = useState<Sale[]>([]);
  const [transactionsLoading, setTransactionsLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const pageSize = 15;

  // Modal State
  const [selectedSaleId, setSelectedSaleId] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Intersection Observer
  const observer = useRef<IntersectionObserver | null>(null);
  const lastElementRef = useCallback((node: HTMLDivElement | null) => {
    if (transactionsLoading) return;
    if (observer.current) observer.current.disconnect();
    
    observer.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setPage(prev => prev + 1);
      }
    });
    
    if (node) observer.current.observe(node);
  }, [transactionsLoading, hasMore]);

  useEffect(() => {
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    setStartDate(thirtyDaysAgo.toISOString().split("T")[0]);
    setEndDate(today.toISOString().split("T")[0]);
  }, []);

  useEffect(() => {
    if (startDate && endDate) {
      fetchSummary();
      // Reset transactions when dates change
      setTransactions([]);
      setPage(1);
      setHasMore(true);
    }
  }, [startDate, endDate]);

  useEffect(() => {
    if (startDate && endDate && page > 0) {
      fetchTransactions();
    }
  }, [page, startDate, endDate]);

  const fetchSummary = async () => {
    setSummaryLoading(true);
    try {
      const params = new URLSearchParams({
        start_date: startDate,
        end_date: endDate
      });
      const response = await fetch(`/api/reports/sales?${params}`);
      const data = await response.json();
      setReportData(data);
    } catch (error) {
      console.error("Sales report summary fetch error:", error);
    } finally {
      setSummaryLoading(false);
    }
  };

  const fetchTransactions = async () => {
    if (!hasMore && page > 1) return;
    
    setTransactionsLoading(true);
    try {
      const params = new URLSearchParams({
        start_date: startDate + "T00:00:00",
        end_date: endDate + "T23:59:59",
        page: page.toString(),
        page_size: pageSize.toString()
      });
      const response = await fetch(`/api/sales?${params}`);
      const data = await response.json();
      
      if (data.items.length < pageSize) {
        setHasMore(false);
      }
      
      setTransactions(prev => page === 1 ? data.items : [...prev, ...data.items]);
    } catch (error) {
      console.error("Sales fetch error:", error);
    } finally {
      setTransactionsLoading(false);
    }
  };

  const openDetails = (id: string) => {
    setSelectedSaleId(id);
    setIsModalOpen(true);
  };

  const dashboardColumns: Column<SalesData>[] = [
    { header: ARABIC.reports.sales.date, accessor: "date", className: "font-bold" },
    { header: ARABIC.reports.sales.count, accessor: "count", render: (item) => <span className="bg-slate-100 text-slate-700 px-2 py-1 rounded-lg text-xs font-bold">{item.count}</span> },
    { header: ARABIC.reports.sales.amount, accessor: "revenue", render: (item) => <span className="text-blue-600 font-bold">{formatCurrency(item.revenue)}</span> },
    { header: ARABIC.reports.sales.netProfit, accessor: "profit", render: (item) => <span className={`font-bold ${item.profit >= 0 ? "text-emerald-600" : "text-rose-600"}`}>{formatCurrency(item.profit)}</span> },
  ];

  const transactionColumns: Column<Sale>[] = [
    { 
      header: ARABIC.reports.id, 
      accessor: "id", 
      render: (item) => <span className="font-mono text-[10px] text-slate-400 font-semibold">{item.id.substring(0, 8).toUpperCase()}</span> 
    },
    { 
      header: ARABIC.reports.sales.time, 
      accessor: "created_at", 
      render: (item) => (
        <div className="flex flex-col">
          <span className="font-bold text-slate-700 text-xs">{new Date(item.created_at).toLocaleDateString('ar-EG')}</span>
          <span className="text-[10px] text-slate-400 font-semibold">{new Date(item.created_at).toLocaleTimeString('ar-EG', { hour: '2-digit', minute: '2-digit' })}</span>
        </div>
      )
    },
    { header: ARABIC.reports.paymentMethod, accessor: "payment_method_name", className: "text-slate-500 font-bold" },
    { 
      header: ARABIC.reports.total, 
      accessor: "grand_total", 
      render: (item) => <span className="text-indigo-600 font-black">{formatCurrency(item.grand_total)}</span> 
    },
    { 
      header: ARABIC.reports.sales.netProfit, 
      accessor: "profit", 
      render: (item) => <span className={`font-bold ${item.profit >= 0 ? "text-emerald-600" : "text-rose-600"}`}>{formatCurrency(item.profit)}</span> 
    },
    {
      header: '',
      accessor: 'actions',
      render: (item) => (
        <button 
          onClick={() => openDetails(item.id)}
          className="p-2 hover:bg-slate-100 rounded-xl transition-all text-slate-400 hover:text-indigo-600 group"
          title={ARABIC.reports.viewDetails}
        >
          <Eye className="w-5 h-5 transition-transform group-hover:scale-110" />
        </button>
      )
    }
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-20">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-black font-heading text-slate-900 tracking-tight">{ARABIC.reports.sales.title}</h1>
          <p className="text-slate-500 mt-2 font-bold flex items-center gap-2">
            <Activity className="w-4 h-4 text-indigo-500" />
            {ARABIC.reports.sales.subtitle}
          </p>
        </div>
        <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
          <div className="flex items-center gap-2 bg-white/70 backdrop-blur-md p-2.5 rounded-2xl shadow-sm border border-slate-100 flex-1">
            <Calendar className="w-4 h-4 text-slate-400 ms-2" />
            <input 
              type="date" 
              value={startDate} 
              onChange={e => setStartDate(e.target.value)}
              className="bg-transparent border-none focus:ring-0 text-sm font-black text-slate-700 cursor-pointer w-full" 
            />
            <span className="text-slate-300 font-bold">←</span>
            <input 
              type="date" 
              value={endDate} 
              onChange={e => setEndDate(e.target.value)}
              className="bg-transparent border-none focus:ring-0 text-sm font-black text-slate-700 cursor-pointer w-full" 
            />
          </div>
          <ExportButtonGroup reportType="sales" startDate={startDate} endDate={endDate} />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card p-6 bg-gradient-to-br from-blue-50/50 to-white hover:shadow-xl transition-all duration-500 border border-blue-100 shadow-sm rounded-[2rem]">
          <div className="p-3 bg-blue-100/50 text-blue-600 rounded-2xl w-fit mb-4 shadow-inner">
            <TrendingUp className="w-6 h-6" />
          </div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{ARABIC.reports.sales.totalRevenue}</p>
          <h3 className="text-3xl font-black text-slate-900 mt-1 tracking-tighter">{formatCurrency(reportData?.total_revenue || 0)}</h3>
        </div>

        <div className="glass-card p-6 bg-gradient-to-br from-emerald-50/50 to-white hover:shadow-xl transition-all duration-500 border border-emerald-100 shadow-sm rounded-[2rem]">
          <div className="p-3 bg-emerald-100/50 text-emerald-600 rounded-2xl w-fit mb-4 shadow-inner">
            <DollarSign className="w-6 h-6" />
          </div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{ARABIC.reports.sales.netProfit}</p>
          <h3 className="text-3xl font-black text-slate-900 mt-1 tracking-tighter">{formatCurrency(reportData?.total_profit || 0)}</h3>
        </div>

        <div className="glass-card p-6 bg-gradient-to-br from-indigo-50/50 to-white hover:shadow-xl transition-all duration-500 border border-indigo-100 shadow-sm rounded-[2rem]">
          <div className="p-3 bg-indigo-100/50 text-indigo-600 rounded-2xl w-fit mb-4 shadow-inner">
            <ShoppingBag className="w-6 h-6" />
          </div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{ARABIC.reports.sales.salesCount}</p>
          <h3 className="text-3xl font-black text-slate-900 mt-1 tracking-tighter">{reportData?.sales_count || 0}</h3>
        </div>

        <div className="glass-card p-6 bg-gradient-to-br from-purple-50/50 to-white hover:shadow-xl transition-all duration-500 border border-purple-100 shadow-sm rounded-[2rem]">
          <div className="p-3 bg-purple-100/50 text-purple-600 rounded-2xl w-fit mb-4 shadow-inner">
            <PieIcon className="w-6 h-6" />
          </div>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">{ARABIC.reports.sales.avgMargin}</p>
          <h3 className="text-3xl font-black text-slate-900 mt-1 tracking-tighter">
            {reportData?.total_revenue && reportData.total_revenue > 0
              ? ((reportData.total_profit / reportData.total_revenue) * 100).toFixed(1)
              : "0.0"}%
          </h3>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Daily Stats Table */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex items-center gap-2 px-2">
              <ListFilter className="w-5 h-5 text-slate-400" />
              <h2 className="text-xl font-black text-slate-800">{ARABIC.reports.sales.dailyStatistics}</h2>
          </div>
          <div className="glass-card rounded-[2rem] border border-slate-100 overflow-hidden shadow-sm">
            <DataTable 
              columns={dashboardColumns} 
              data={reportData?.daily_breakdown || []} 
              loading={summaryLoading}
              emptyMessage={ARABIC.reports.noData}
            />
          </div>
        </div>

        {/* Transactions Table with Infinite Scroll */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between px-2">
              <div className="flex items-center gap-2">
                <ArrowDownNarrowWide className="w-5 h-5 text-indigo-500" />
                <h2 className="text-xl font-black text-slate-800">{ARABIC.reports.individualTransactions}</h2>
              </div>
              <div className="px-3 py-1 bg-slate-100 rounded-full text-[10px] font-black text-slate-500 uppercase">
                {transactions.length} {ARABIC.reports.of} {reportData?.sales_count || 0}
              </div>
          </div>
          
          <div className="glass-card rounded-[2rem] border border-slate-100 overflow-hidden shadow-sm bg-white">
             {/* Instead of DataTable, we render a custom table to handle infinite scrolling smoothly */}
             <div className="overflow-x-auto">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-100">
                      {transactionColumns.map((col, idx) => (
                        <th key={idx} className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest text-start">{col.header}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {transactions.map((sale, idx) => (
                      <tr key={sale.id} className="hover:bg-slate-50/80 transition-all duration-200">
                        {transactionColumns.map((col, colIdx) => (
                          <td key={colIdx} className={`px-6 py-4 text-sm font-bold text-slate-700 ${col.className || ''}`}>
                            {col.render ? col.render(sale) : (sale as any)[col.accessor]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
             </div>

             {/* Infinite Scroll Trigger */}
             <div ref={lastElementRef} className="p-8 flex justify-center">
                {transactionsLoading ? (
                  <div className="flex items-center gap-3 bg-white px-6 py-3 rounded-2xl shadow-sm border border-slate-100">
                    <div className="animate-spin h-5 w-5 border-2 border-indigo-600 border-t-transparent rounded-full" />
                    <span className="text-sm font-black text-slate-500">{ARABIC.common.loading || 'جاري التحميل...'}</span>
                  </div>
                ) : !hasMore && transactions.length > 0 ? (
                  <div className="text-xs font-black text-slate-300 uppercase tracking-widest bg-slate-50 px-4 py-2 rounded-full">
                    {ARABIC.reports.noMoreData}
                  </div>
                ) : null}
             </div>
          </div>
        </div>
      </div>

      <SaleDetailModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        saleId={selectedSaleId}
      />
    </div>
  );
}