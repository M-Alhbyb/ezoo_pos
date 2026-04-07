"use client";

import { useState, useEffect, use } from "react";
import Link from "next/link";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDateTime } from "@/lib/utils/format";
import { ArrowRight, Package, Receipt, TrendingUp, AlertTriangle } from "lucide-react";

interface ProjectItem {
  id: string;
  product_id: string;
  product_name: string;
  quantity: number;
  unit_price: string;
  line_total: string;
}

interface Expense {
  id: string;
  description: string;
  amount: string;
}

interface Project {
  id: string;
  name: string;
  status: string;
  selling_price: string;
  total_cost: string;
  total_expenses: string;
  profit: string;
  note: string | null;
  items: ProjectItem[];
  expenses: Expense[];
  created_at: string;
}

export default function ProjectDetailPage({ params }: { params: Promise<{ projectId: string }> }) {
  const resolvedParams = use(params);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchProject();
  }, [resolvedParams.projectId]);

  const fetchProject = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/projects/${resolvedParams.projectId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error(ARABIC.projects.projectNotFound || 'المشروع غير موجود');
        }
        throw new Error(ARABIC.common.error);
      }

      const data = await response.json();
      setProject(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteProject = async () => {
    if (!project) return;
    if (!confirm(ARABIC.projects.confirmCompleteMessage || 'هل أنت متأكد؟')) return;

    try {
      const response = await fetch(`/api/projects/${project.id}/complete`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || ARABIC.common.error);
      }

      await fetchProject();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const getStatusLabel = (status: string) => {
    const statusMap: Record<string, string> = {
      DRAFT: ARABIC.projects.statusTypes.draft,
      COMPLETED: ARABIC.projects.statusTypes.completed,
    };
    return statusMap[status] || status;
  };

  const getStatusStyle = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return 'bg-emerald-100 text-emerald-700';
      case 'DRAFT':
      default:
        return 'bg-amber-100 text-amber-700';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <Link href="/projects" className="text-sm text-primary hover:text-primary/80 mb-2 inline-flex items-center gap-1">
            <ArrowRight className="w-4 h-4 rtl:rotate-180" />
            {ARABIC.projects.title}
          </Link>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.projects.projectDetails}</h1>
        </div>
        {project && project.status !== 'COMPLETED' && (
          <button
            onClick={handleCompleteProject}
            className="px-4 py-2.5 bg-emerald-600 text-white font-medium rounded-xl hover:bg-emerald-700 transition-all shadow-sm"
          >
            {ARABIC.projects.completeProject}
          </button>
        )}
      </div>

      {error && (
        <div className="bg-rose-50 text-rose-700 px-4 py-3 rounded-xl border border-rose-200 flex items-center">
          <AlertTriangle className="w-5 h-5 me-3 text-rose-500" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="flex flex-col items-center justify-center py-20">
          <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
          <p className="text-slate-500 mt-4">{ARABIC.common.loading}</p>
        </div>
      ) : project ? (
        <>
          {/* Project Header */}
          <div className="glass p-6 rounded-2xl">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-2xl font-bold text-slate-800">{project.name}</h2>
                <p className="text-sm text-slate-500 font-mono mt-1">{project.id}</p>
              </div>
              <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${getStatusStyle(project.status)}`}>
                {getStatusLabel(project.status)}
              </span>
            </div>
            
            {project.note && (
              <div className="mt-4 p-4 bg-slate-50 rounded-xl">
                <p className="text-sm text-slate-600">{project.note}</p>
              </div>
            )}

            <div className="mt-4 text-sm text-slate-500">
              {ARABIC.common.createdAt}: {formatDateTime(project.created_at)}
            </div>
          </div>

          {/* Financial Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="glass p-6 rounded-2xl">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                </div>
                <span className="text-slate-500 text-sm">{ARABIC.projects.sellingPrice}</span>
              </div>
              <p className="text-2xl font-bold text-slate-800">{formatCurrency(project.selling_price)}</p>
            </div>
            <div className="glass p-6 rounded-2xl">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-amber-100 rounded-lg">
                  <Package className="w-5 h-5 text-amber-600" />
                </div>
                <span className="text-slate-500 text-sm">{ARABIC.projects.totalCost}</span>
              </div>
              <p className="text-2xl font-bold text-slate-800">{formatCurrency(project.total_cost)}</p>
            </div>
            <div className="glass p-6 rounded-2xl">
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-emerald-100 rounded-lg">
                  <TrendingUp className="w-5 h-5 text-emerald-600" />
                </div>
                <span className="text-slate-500 text-sm">{ARABIC.projects.profit}</span>
              </div>
              <p className="text-2xl font-bold text-emerald-600">{formatCurrency(project.profit)}</p>
            </div>
          </div>

          {/* Project Items */}
          <div className="glass rounded-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Package className="w-5 h-5 text-blue-500" />
                {ARABIC.projects.projectItems}
              </h3>
            </div>
            {project.items.length === 0 ? (
              <div className="p-8 text-center text-slate-400">
                {ARABIC.projects.noItems || 'لا توجد منتجات'}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-100">
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">{ARABIC.pos.product}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{ARABIC.pos.quantity}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{ARABIC.pos.price}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{ARABIC.pos.total}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {project.items.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50/50">
                        <td className="px-6 py-4 font-medium text-slate-800">{item.product_name}</td>
                        <td className="px-6 py-4 text-end text-slate-600">{item.quantity}</td>
                        <td className="px-6 py-4 text-end text-slate-600">{formatCurrency(item.unit_price)}</td>
                        <td className="px-6 py-4 text-end font-medium text-slate-800">{formatCurrency(item.line_total)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Project Expenses */}
          <div className="glass rounded-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Receipt className="w-5 h-5 text-amber-500" />
                {ARABIC.projects.projectExpenses}
              </h3>
            </div>
            {project.expenses.length === 0 ? (
              <div className="p-8 text-center text-slate-400">
                {ARABIC.projects.noExpenses || 'لا توجد مصاريف'}
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-start border-collapse">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-100">
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase">{ARABIC.expenses.description || 'الوصف'}</th>
                      <th className="px-6 py-3 text-xs font-semibold text-slate-500 uppercase text-end">{ARABIC.pos.total}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {project.expenses.map((expense) => (
                      <tr key={expense.id} className="hover:bg-slate-50/50">
                        <td className="px-6 py-4 font-medium text-slate-800">{expense.description}</td>
                        <td className="px-6 py-4 text-end font-medium text-slate-800">{formatCurrency(expense.amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {project.expenses.length > 0 && (
              <div className="px-6 py-4 bg-slate-50/50 border-t border-slate-100 flex justify-between">
                <span className="font-medium text-slate-600">{ARABIC.projects.totalExpenses}</span>
                <span className="font-bold text-slate-800">{formatCurrency(project.total_expenses)}</span>
              </div>
            )}
          </div>
        </>
      ) : null}
    </div>
  );
}