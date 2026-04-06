"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { 
  TrendingUp, 
  Briefcase, 
  Users, 
  Package, 
  AlertTriangle,
  ArrowUpRight,
  ShoppingCart,
  DollarSign
} from "lucide-react";

import { LineChart } from "@/components/charts/LineChart";
import { BarChart } from "@/components/charts/BarChart";
import { PieChart } from "@/components/charts/PieChart";
import { getSalesDashboard, getProjectsDashboard, getPartnersDashboard, getInventoryDashboard } from "@/lib/api/dashboard";
import { 
  transformSalesChartData, 
  transformProjectChartData, 
  transformPartnerChartData, 
  transformInventoryChartData 
} from "@/lib/utils/chart-utils";

export default function OverviewPage() {
  const [startDate, setStartDate] = useState<string>("");
  const [endDate, setEndDate] = useState<string>("");
  const [loading, setLoading] = useState(true);
  
  // Chart Data
  const [salesData, setSalesData] = useState<any[]>([]);
  const [projectsData, setProjectsData] = useState<any[]>([]);
  const [partnersData, setPartnersData] = useState<any[]>([]);
  const [inventoryData, setInventoryData] = useState<any[]>([]);
  
  // Summary Stats
  const [stats, setStats] = useState({
    todayRevenue: 0,
    activeProjects: 0,
    totalPartners: 0,
    lowStockCount: 0
  });

  useEffect(() => {
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    setStartDate(thirtyDaysAgo.toISOString().split("T")[0]);
    setEndDate(today.toISOString().split("T")[0]);
  }, []);

  useEffect(() => {
    if (startDate && endDate) {
      fetchAllData();
    }
  }, [startDate, endDate]);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      const [sales, projects, partners, inventory] = await Promise.all([
        getSalesDashboard(startDate, endDate),
        getProjectsDashboard(startDate, endDate),
        getPartnersDashboard(startDate, endDate),
        getInventoryDashboard(startDate, endDate)
      ]);

      if (sales.success && sales.data) {
        setSalesData(transformSalesChartData(sales.data.dates, sales.data.revenue, sales.data.profit, sales.data.vat));
        const totalRev = sales.data.revenue.reduce((a, b) => a + b, 0);
        setStats(s => ({ ...s, todayRevenue: totalRev }));
      }

      if (projects.success && projects.data) {
        const trans = transformProjectChartData(projects.data.project_names, projects.data.profits, projects.data.profit_margins, projects.data.project_ids);
        setProjectsData(trans.map(t => ({ name: t.name, profit: t.profit })));
        setStats(s => ({ ...s, activeProjects: projects.data?.project_ids.length || 0 }));
      }

      if (partners.success && partners.data) {
        const trans = transformPartnerChartData(partners.data.partner_names, partners.data.dividend_amounts, partners.data.share_percentages, partners.data.partner_ids);
        setPartnersData(trans.map(t => ({ name: t.name, value: t.amount })));
        setStats(s => ({ ...s, totalPartners: partners.data?.partner_ids.length || 0 }));
      }

      if (inventory.success && inventory.data) {
        setInventoryData(transformInventoryChartData(inventory.data.dates, inventory.data.sales, inventory.data.restocks, inventory.data.reversals));
      }

      // Fetch low stock count
      const lowStockRes = await fetch("/api/inventory/low-stock?threshold=10");
      if (lowStockRes.ok) {
        const data = await lowStockRes.json();
        setStats(s => ({ ...s, lowStockCount: data.total || 0 }));
      }

    } catch (error) {
      console.error("Dashboard fetch error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-extrabold font-heading text-slate-900 tracking-tight">Overview Dashboard</h1>
          <p className="text-slate-500 mt-2 font-medium">Business intelligence and real-time performance tracking.</p>
        </div>
        <div className="flex items-center gap-3 bg-white p-2 rounded-2xl shadow-sm border border-slate-200">
          <input 
            type="date" 
            value={startDate} 
            onChange={e => setStartDate(e.target.value)}
            className="bg-transparent border-none focus:ring-0 text-sm font-semibold text-slate-700" 
          />
          <span className="text-slate-300 font-bold">→</span>
          <input 
            type="date" 
            value={endDate} 
            onChange={e => setEndDate(e.target.value)}
            className="bg-transparent border-none focus:ring-0 text-sm font-semibold text-slate-700" 
          />
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card group hover:scale-[1.02] transition-all duration-300">
          <div className="flex justify-between items-start">
            <div className="p-3 bg-blue-100/50 text-blue-600 rounded-2xl group-hover:bg-blue-600 group-hover:text-white transition-colors duration-300">
              <DollarSign className="w-6 h-6" />
            </div>
            <ArrowUpRight className="w-5 h-5 text-slate-300 group-hover:text-blue-500" />
          </div>
          <div className="mt-4">
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Total Revenue</p>
            <h3 className="text-3xl font-bold text-slate-900 mt-1">${stats.todayRevenue.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</h3>
          </div>
        </div>

        <div className="glass-card group hover:scale-[1.02] transition-all duration-300">
          <div className="flex justify-between items-start">
            <div className="p-3 bg-indigo-100/50 text-indigo-600 rounded-2xl group-hover:bg-indigo-600 group-hover:text-white transition-colors duration-300">
              <Briefcase className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4">
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Active Projects</p>
            <h3 className="text-3xl font-bold text-slate-900 mt-1">{stats.activeProjects}</h3>
          </div>
        </div>

        <div className="glass-card group hover:scale-[1.02] transition-all duration-300">
          <div className="flex justify-between items-start">
            <div className="p-3 bg-emerald-100/50 text-emerald-600 rounded-2xl group-hover:bg-emerald-600 group-hover:text-white transition-colors duration-300">
              <Users className="w-6 h-6" />
            </div>
          </div>
          <div className="mt-4">
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Partners</p>
            <h3 className="text-3xl font-bold text-slate-900 mt-1">{stats.totalPartners}</h3>
          </div>
        </div>

        <div className="glass-card group hover:scale-[1.02] transition-all duration-300">
          <div className="flex justify-between items-start">
            <div className="p-3 bg-rose-100/50 text-rose-600 rounded-2xl group-hover:bg-rose-600 group-hover:text-white transition-colors duration-300">
              <Package className="w-6 h-6" />
            </div>
            {stats.lowStockCount > 0 && <AlertTriangle className="w-5 h-5 text-rose-500 animate-pulse" />}
          </div>
          <div className="mt-4">
            <p className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Low Stock items</p>
            <h3 className={`text-3xl font-bold mt-1 ${stats.lowStockCount > 0 ? "text-rose-600" : "text-slate-900"}`}>{stats.lowStockCount}</h3>
          </div>
        </div>
      </div>

      {/* Main Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-10">
        {/* Sales Chart */}
        <div className="glass p-8 rounded-[2rem] border border-slate-100 shadow-sm hover:shadow-xl transition-all duration-500 overflow-hidden relative group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50/50 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-700"></div>
          <div className="flex items-center justify-between mb-8 relative z-10">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl">
                <TrendingUp className="w-5 h-5" />
              </div>
              <h3 className="text-xl font-bold text-slate-800">Sales Growth</h3>
            </div>
            <Link href="/dashboard/reports/sales" className="text-xs font-bold text-blue-600 hover:text-blue-700 uppercase tracking-wider">View Details</Link>
          </div>
          <LineChart 
            data={salesData} 
            lines={[{ dataKey: "revenue", color: "#3B82F6", name: "Revenue" }]} 
            height={320} 
            loading={loading}
            isCurrency={true}
            decimalPlaces={2}
          />
        </div>

        {/* Project Profit Chart */}
        <div className="glass p-8 rounded-[2rem] border border-slate-100 shadow-sm hover:shadow-xl transition-all duration-500 overflow-hidden relative group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50/50 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-700"></div>
          <div className="flex items-center justify-between mb-8 relative z-10">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-indigo-50 text-indigo-600 rounded-xl">
                <Briefcase className="w-5 h-5" />
              </div>
              <h3 className="text-xl font-bold text-slate-800">Project Performance</h3>
            </div>
            <Link href="/dashboard/reports/projects" className="text-xs font-bold text-indigo-600 hover:text-indigo-700 uppercase tracking-wider">View Projects</Link>
          </div>
          <BarChart 
            data={projectsData} 
            bars={[{ dataKey: "profit", color: "#6366F1", name: "Profit" }]} 
            height={320} 
            loading={loading}
            isCurrency={true}
          />
        </div>

        {/* Partner Distribution PIE */}
        <div className="glass p-8 rounded-[2rem] border border-slate-100 shadow-sm hover:shadow-xl transition-all duration-500 overflow-hidden relative group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-50/50 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-700"></div>
          <div className="flex items-center justify-between mb-8 relative z-10">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-emerald-50 text-emerald-600 rounded-xl">
                <Users className="w-5 h-5" />
              </div>
              <h3 className="text-xl font-bold text-slate-800">Partner Dividends</h3>
            </div>
            <Link href="/dashboard/reports/partners" className="text-xs font-bold text-emerald-600 hover:text-emerald-700 uppercase tracking-wider">Manage</Link>
          </div>
          <PieChart 
            data={partnersData} 
            height={320} 
            loading={loading}
            isCurrency={true}
          />
        </div>

        {/* Inventory Chart */}
        <div className="glass p-8 rounded-[2rem] border border-slate-100 shadow-sm hover:shadow-xl transition-all duration-500 overflow-hidden relative group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-rose-50/50 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-700"></div>
          <div className="flex items-center justify-between mb-8 relative z-10">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-rose-50 text-rose-600 rounded-xl">
                <Package className="w-5 h-5" />
              </div>
              <h3 className="text-xl font-bold text-slate-800">Stock Activity</h3>
            </div>
            <Link href="/dashboard/reports/inventory" className="text-xs font-bold text-rose-600 hover:text-rose-700 uppercase tracking-wider">Reports</Link>
          </div>
          <LineChart 
            data={inventoryData} 
            lines={[
              { dataKey: "sales", color: "#F43F5E", name: "Sales" },
              { dataKey: "restocks", color: "#10B981", name: "Restocks" }
            ]} 
            height={320} 
            loading={loading}
          />
        </div>
      </div>

      {/* Quick Access Area */}
      <div className="mt-12 bg-slate-900 rounded-[3rem] p-10 text-white relative overflow-hidden shadow-2xl">
        <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/20 rounded-full blur-[100px] -ml-48 -mt-48"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-indigo-500/20 rounded-full blur-[100px] -mr-48 -mb-48"></div>
        
        <div className="relative z-10">
          <h3 className="text-2xl font-bold mb-8">Quick Navigation</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <Link href="/pos" className="group p-6 bg-white/5 hover:bg-white/10 rounded-[2rem] border border-white/10 transition-all duration-300">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-blue-500/20 text-blue-400 rounded-2xl group-hover:bg-blue-500 group-hover:text-white transition-all">
                  <ShoppingCart className="w-6 h-6" />
                </div>
                <div className="font-bold text-lg">Sales POS</div>
              </div>
              <p className="mt-4 text-slate-400 text-sm leading-relaxed">Launch terminal for new sales and checkout processing.</p>
            </Link>

            <Link href="/products" className="group p-6 bg-white/5 hover:bg-white/10 rounded-[2rem] border border-white/10 transition-all duration-300">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-indigo-500/20 text-indigo-400 rounded-2xl group-hover:bg-indigo-500 group-hover:text-white transition-all">
                  <Package className="w-6 h-6" />
                </div>
                <div className="font-bold text-lg">Inventory</div>
              </div>
              <p className="mt-4 text-slate-400 text-sm leading-relaxed">Adjust catalogs, add products and track categories.</p>
            </Link>

            <Link href="/projects" className="group p-6 bg-white/5 hover:bg-white/10 rounded-[2rem] border border-white/10 transition-all duration-300">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-emerald-500/20 text-emerald-400 rounded-2xl group-hover:bg-emerald-500 group-hover:text-white transition-all">
                  <Briefcase className="w-6 h-6" />
                </div>
                <div className="font-bold text-lg">Projects</div>
              </div>
              <p className="mt-4 text-slate-400 text-sm leading-relaxed">Detailed financial tracking for project-based manufacturing.</p>
            </Link>

            <Link href="/partners" className="group p-6 bg-white/5 hover:bg-white/10 rounded-[2rem] border border-white/10 transition-all duration-300">
              <div className="flex items-center gap-4">
                <div className="p-3 bg-amber-500/20 text-amber-400 rounded-2xl group-hover:bg-amber-500 group-hover:text-white transition-all">
                  <Users className="w-6 h-6" />
                </div>
                <div className="font-bold text-lg">Partners</div>
              </div>
              <p className="mt-4 text-slate-400 text-sm leading-relaxed">Automate profit distributions and manages investor shares.</p>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}