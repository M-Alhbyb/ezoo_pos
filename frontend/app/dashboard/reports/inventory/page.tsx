"use client";

import React, { useState, useEffect } from "react";
import { Package, RefreshCw, AlertTriangle, ArrowDownRight, ArrowUpRight, Calendar } from "lucide-react";
import { ARABIC } from "@/lib/constants/arabic";
import { DataTable, Column } from "@/components/reports/DataTable";
import { ExportButtonGroup } from "@/components/reports/ExportButtonGroup";

interface InventoryMovementData {
  reason: string;
  total_delta: number;
}

interface InventoryReportResponse {
  total_movements: number;
  movements_by_reason: InventoryMovementData[];
  total: number;
  page: number;
  page_size: number;
}

export default function InventoryReportPage() {
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [reportData, setReportData] = useState<InventoryReportResponse | null>(null);
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
      const response = await fetch(`/api/reports/inventory?${params}`);
      const data = await response.json();
      setReportData(data);
    } catch (error) {
      console.error("InventoryReport fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const getReasonLabel = (reason: string) => {
    const reasonMap: Record<string, string> = {
      sale: ARABIC.inventory.movementTypes.sale,
      restock: ARABIC.inventory.movementTypes.restock,
      adjustment: ARABIC.inventory.movementTypes.adjustment,
      reversal: ARABIC.inventory.movementTypes.reversal,
    };
    return reasonMap[reason] || reason;
  };

  const columns: Column<InventoryMovementData>[] = [
    { header: ARABIC.inventory.movementTypes.sale || 'السبب', accessor: "reason", className: "font-bold text-slate-800", render: (item) => getReasonLabel(item.reason) },
    { 
      header: ARABIC.inventory.delta || 'التغيير', 
      accessor: "total_delta",
      render: (item) => (
        <div className="flex items-center gap-2">
           <span className={`font-bold ${item.total_delta >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
             {item.total_delta > 0 ? "+" : ""}{item.total_delta}
           </span>
           {item.total_delta > 0 ? <ArrowUpRight className="w-4 h-4 text-emerald-400" /> : <ArrowDownRight className="w-4 h-4 text-rose-400" />}
        </div>
      )
    },
    { 
        header: ARABIC.common.status, 
        accessor: "status", 
        render: (item) => (
            <span className={`px-2 py-1 rounded-lg text-xs font-bold uppercase tracking-wider ${
                item.total_delta >= 0 ? "bg-emerald-50 text-emerald-600" : "bg-rose-50 text-rose-600"
            }`}>
                {item.total_delta >= 0 ? (ARABIC.inventory.restock || 'إعادة تخزين') : (ARABIC.inventory.movementTypes?.sale || 'مبيعة')}
            </span>
        ) 
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-extrabold font-heading text-slate-900 tracking-tight">{ARABIC.reports.inventory.title}</h1>
          <p className="text-slate-500 mt-2 font-medium">{ARABIC.reports.inventory.subtitle}</p>
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
          <ExportButtonGroup reportType="inventory" startDate={startDate} endDate={endDate} />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div className="glass-card p-8 hover:shadow-xl transition-all duration-300 border border-slate-100 flex flex-col justify-center">
          <div className="p-3 bg-blue-100/50 text-blue-600 rounded-2xl w-fit mb-4">
            <RefreshCw className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">{ARABIC.reports.inventory.totalMovements}</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">{reportData?.total_movements || 0}</h3>
        </div>

        <div className="glass-card p-8 hover:shadow-xl transition-all duration-300 border border-slate-100 flex flex-col justify-center">
          <div className="p-3 bg-emerald-100/50 text-emerald-600 rounded-2xl w-fit mb-4">
            <Package className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">{ARABIC.inventory.balance || 'الرصيد الإجمالي'}</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">
             {reportData?.movements_by_reason?.reduce((acc, curr) => acc + curr.total_delta, 0) || 0} {ARABIC.inventory.quantity || 'وحدة'}
          </h3>
        </div>

        <div className="glass-card p-8 hover:shadow-xl transition-all duration-300 border border-slate-100 flex flex-col justify-center">
          <div className="p-3 bg-rose-100/50 text-rose-600 rounded-2xl w-fit mb-4">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">{ARABIC.reports.inventory.movementsByReason}</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">{reportData?.movements_by_reason?.length || 0}</h3>
        </div>
      </div>

      <div className="space-y-4">
        <DataTable 
          columns={columns} 
          data={reportData?.movements_by_reason || []} 
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