"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { ARABIC } from "@/lib/constants/arabic";
import { formatCurrency, formatDateTime } from "@/lib/utils/format";
import ProjectModal from "@/components/projects/ProjectModal";

interface ProjectItem {
  id: string;
  product_name: string;
  quantity: number;
}

interface Expense {
  id: string;
  description: string;
  amount: number;
}

interface Project {
  id: string;
  name: string;
  status: string;
  selling_price: number;
  total_cost: number;
  total_expenses: number;
  profit: number;
  created_at: string;
  items: ProjectItem[];
  expenses: Expense[];
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const response = await fetch("/api/projects");
      if (!response.ok) throw new Error("Failed to fetch projects");
      
      const data = await response.json();
      setProjects(Array.isArray(data) ? data : data.items || []);
    } catch (err: any) {
      console.error(err);
      setError(ARABIC.common.error);
      setProjects([]);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async (data: any) => {
    const response = await fetch("/api/projects", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || ARABIC.common.error);
    }

    await fetchProjects();
    setIsModalOpen(false);
  };

  const handleCompleteProject = async (projectId: string) => {
    if (!confirm(ARABIC.projects.confirmComplete)) return;
    
    try {
      const response = await fetch(`/api/projects/${projectId}/complete`, {
        method: "POST",
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || ARABIC.common.error);
      }

      await fetchProjects();
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
      <div className="flex justify-between items-end mb-6">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{ARABIC.projects.title}</h1>
          <p className="text-slate-500 mt-1">{ARABIC.projects.subtitle}</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          className="flex items-center px-4 py-2.5 bg-primary text-white font-medium rounded-xl hover:bg-blue-600 transition-all shadow-sm shadow-blue-200"
        >
          <svg className="w-5 h-5 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
          {ARABIC.projects.createProject}
        </button>
      </div>

      {error && (
        <div className="bg-amber-50 text-amber-700 px-4 py-3 rounded-xl mb-4 border border-amber-200 animate-slide-up flex items-center shadow-sm">
          <svg className="w-5 h-5 me-3 text-amber-500" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
          <span className="font-medium text-sm">{error}</span>
        </div>
      )}

      <div className="glass rounded-2xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-400">
            <svg className="animate-spin w-8 h-8 mb-4 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span className="font-medium">{ARABIC.common.loading}</span>
          </div>
        ) : projects.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-start border-collapse animate-fade-in">
              <thead>
                <tr className="bg-slate-50/50 border-b border-slate-200">
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.projects.projectName}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">{ARABIC.projects.status}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.projects.sellingPrice}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.projects.totalCost}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.projects.profit}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.common.createdAt}</th>
                  <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-end">{ARABIC.common.actions}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 bg-white/50">
                {projects.map((project) => (
                  <tr key={project.id} className="hover:bg-slate-50/80 transition-colors group">
                    <td className="px-6 py-4">
                      <Link href={`/projects/${project.id}`} className="font-medium text-slate-800 hover:text-primary transition-colors">
                        {project.name}
                      </Link>
                      <div className="text-xs text-slate-500 mt-0.5 font-mono">{project.id.slice(0, 8)}...</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${getStatusStyle(project.status)}`}>
                        {getStatusLabel(project.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-end font-medium text-slate-800">
                      {formatCurrency(project.selling_price)}
                    </td>
                    <td className="px-6 py-4 text-end text-slate-600">
                      {formatCurrency(project.total_cost)}
                    </td>
                    <td className="px-6 py-4 text-end font-medium text-emerald-600">
                      {formatCurrency(project.profit)}
                    </td>
                    <td className="px-6 py-4 text-end text-slate-500 text-sm">
                      {formatDateTime(project.created_at)}
                    </td>
                    <td className="px-6 py-4 text-end">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/projects/${project.id}`}
                          className="px-3 py-1.5 text-xs font-medium bg-slate-50 text-slate-700 rounded-lg hover:bg-slate-100 transition-colors border border-slate-200"
                        >
                          {ARABIC.projects.viewDetails}
                        </Link>
                        {project.status !== 'COMPLETED' && (
                          <button
                            onClick={() => handleCompleteProject(project.id)}
                            className="px-3 py-1.5 text-xs font-medium bg-emerald-50 text-emerald-700 rounded-lg hover:bg-emerald-100 transition-colors border border-emerald-200"
                          >
                            {ARABIC.projects.completeProject}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-24 text-slate-400 animate-fade-in">
            <svg className="w-16 h-16 mb-4 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
            <div className="text-lg font-medium text-slate-600 mb-1">{ARABIC.projects.noProjects}</div>
            <p className="text-sm">{ARABIC.projects.createProjectStart}</p>
          </div>
        )}
      </div>

      <ProjectModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateProject}
      />
    </div>
  );
}