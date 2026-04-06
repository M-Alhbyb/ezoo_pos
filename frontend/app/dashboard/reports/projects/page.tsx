"use client";

import React, { useState, useEffect } from "react";
import { Briefcase, BarChart3, TrendingDown, Target, Download, Calendar, ArrowRight } from "lucide-react";
import { DataTable, Column } from "@/components/reports/DataTable";
import { ExportButtonGroup } from "@/components/reports/ExportButtonGroup";

interface ProjectData {
  id: string;
  name: string;
  status: string;
  selling_price: number;
  total_cost: number;
  total_expenses: number;
  profit: number;
}

interface ProjectReportResponse {
  total_projects: number;
  total_selling_price: number;
  total_cost: number;
  total_expenses: number;
  total_profit: number;
  project_list: ProjectData[];
  total: number;
  page: number;
  page_size: number;
}

export default function ProjectsReportPage() {
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [reportData, setReportData] = useState<ProjectReportResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const pageSize = 15;

  useEffect(() => {
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 365); // Default to a year for projects
    
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
      const response = await fetch(`/api/reports/projects?${params}`);
      const data = await response.json();
      setReportData(data);
    } catch (error) {
      console.error("Projects report fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  const columns: Column<ProjectData>[] = [
    { header: "Project Name", accessor: "name", className: "font-bold text-slate-900" },
    { 
      header: "Status", 
      accessor: "status",
      render: (item) => (
        <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
          item.status === "completed" ? "bg-emerald-100 text-emerald-700" : "bg-blue-100 text-blue-700"
        }`}>
          {item.status}
        </span>
      )
    },
    { header: "Budget", accessor: "total_cost", render: (item) => <span className="text-slate-500 font-medium">${item.total_cost.toLocaleString()}</span> },
    { header: "Sale Price", accessor: "selling_price", render: (item) => <span className="text-indigo-600 font-bold">${item.selling_price.toLocaleString()}</span> },
    { 
      header: "Net Profit", 
      accessor: "profit", 
      render: (item) => <span className={`font-bold ${item.profit >= 0 ? "text-emerald-600" : "text-rose-600"}`}>${item.profit.toLocaleString()}</span> 
    },
    { 
      header: "Action", 
      accessor: "id", 
      render: (item) => (
        <button className="p-2 hover:bg-slate-100 rounded-xl transition-colors text-slate-400 hover:text-blue-600">
           <ArrowRight className="w-5 h-5" />
        </button>
      )
    },
  ];

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-extrabold font-heading text-slate-900 tracking-tight">Project Analytics</h1>
          <p className="text-slate-500 mt-2 font-medium">Detailed financial health and profitability tracking for custom projects.</p>
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
          <ExportButtonGroup reportType="projects" startDate={startDate} endDate={endDate} />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card p-6 border-b-4 border-b-blue-600 hover:shadow-xl transition-all duration-300">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl w-fit mb-4">
            <Briefcase className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Total Projects</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">{reportData?.total_projects || 0}</h3>
        </div>

        <div className="glass-card p-6 border-b-4 border-b-indigo-600 hover:shadow-xl transition-all duration-300">
          <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl w-fit mb-4">
            <Target className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Project Revenue</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">${reportData?.total_selling_price.toLocaleString() || "0"}</h3>
        </div>

        <div className="glass-card p-6 border-b-4 border-b-emerald-600 hover:shadow-xl transition-all duration-300">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-2xl w-fit mb-4">
            <BarChart3 className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Aggregate Profit</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">${reportData?.total_profit.toLocaleString() || "0"}</h3>
        </div>

        <div className="glass-card p-6 border-b-4 border-b-rose-500 hover:shadow-xl transition-all duration-300">
          <div className="p-3 bg-rose-50 text-rose-600 rounded-2xl w-fit mb-4">
            <TrendingDown className="w-6 h-6" />
          </div>
          <p className="text-sm font-bold text-slate-400 uppercase tracking-widest">Total Cost</p>
          <h3 className="text-3xl font-extrabold text-slate-900 mt-1">${reportData?.total_cost.toLocaleString() || "0"}</h3>
        </div>
      </div>

      {/* Main Table */}
      <div className="space-y-4">
        <DataTable 
          columns={columns} 
          data={reportData?.project_list || []} 
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
