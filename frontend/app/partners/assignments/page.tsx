"use client";

import { useState, useEffect } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { Plus, ClipboardList, TrendingUp, AlertCircle, Loader2, ArrowRight } from "lucide-react";
import Link from "next/link";
import ProductAssignmentForm from "@/components/partners/ProductAssignmentForm";
import AssignmentList from "@/components/partners/AssignmentList";

interface Assignment {
  id: string;
  partner_id: number;
  partner_name: string;
  product_id: string;
  product_name: string;
  assigned_quantity: number;
  remaining_quantity: number;
  share_percentage: string;
  status: 'active' | 'fulfilled';
  created_at: string;
}

interface Partner {
  id: number;
  name: string;
  share_percentage: string;
}

interface Product {
  id: string;
  name: string;
  category_id: string;
}

export default function AssignmentsPage() {
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [partners, setPartners] = useState<Partner[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingAssignment, setEditingAssignment] = useState<Assignment | null>(null);

  const t = ARABIC.partners.assignments;

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [assignmentsRes, partnersRes, productsRes] = await Promise.all([
        fetch('/api/partners/assignments'),
        fetch('/api/partners'),
        fetch('/api/products'),
      ]);

      if (!assignmentsRes.ok || !partnersRes.ok || !productsRes.ok) {
        throw new Error(ARABIC.errors.fetchFailed);
      }

      const assignmentsData = await assignmentsRes.json();
      const partnersData = await partnersRes.json();
      const productsData = await productsRes.json();

      // Backend returns ProductAssignmentListResponse with 'assignments' field
      setAssignments(assignmentsData.assignments || []);
      setPartners(partnersData || []);
      setProducts(productsData || []);
    } catch (err: any) {
      setError(err.message || ARABIC.common.error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: Partial<Assignment>) => {
    const url = editingAssignment
      ? `/api/partners/assignments/${editingAssignment.id}`
      : '/api/partners/assignments';
    
    const method = editingAssignment ? 'PATCH' : 'POST';

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || ARABIC.errors.saveFailed);
    }

    setShowForm(false);
    setEditingAssignment(null);
    await fetchData();
  };

  const handleDelete = async (assignmentId: string) => {
    if (!confirm(t.confirmDelete)) return;

    try {
      const response = await fetch(
        `/api/partners/assignments/${assignmentId}`,
        { method: 'DELETE' }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || ARABIC.errors.deleteFailed);
      }

      await fetchData();
    } catch (err: any) {
      alert(err.message);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-20">
        <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
        <p className="text-slate-500 font-medium">{ARABIC.common.loading}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <Link href="/partners" className="text-sm text-primary hover:text-primary/80 mb-2 inline-flex items-center gap-1">
            <ArrowRight className="w-4 h-4 rtl:rotate-180" />
            {ARABIC.partners.title}
          </Link>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">{t.title}</h1>
          <p className="text-slate-500 mt-1">{t.subtitle}</p>
        </div>
        <button
          onClick={() => {
            setEditingAssignment(null);
            setShowForm(true);
          }}
          className="flex items-center gap-2 bg-primary text-white px-6 py-2.5 rounded-xl hover:bg-blue-600 transition-all shadow-sm shadow-blue-200 font-medium"
        >
          <Plus className="w-5 h-5" />
          {t.newAssignment}
        </button>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-700 rounded-2xl p-4 flex items-center gap-3 animate-slide-up">
          <AlertCircle className="w-5 h-5 text-rose-500" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {/* Stats Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass p-5 rounded-2xl border border-slate-100/50 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-indigo-50 rounded-xl text-indigo-600">
            <ClipboardList className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{t.statsTotal}</p>
            <p className="text-2xl font-bold text-slate-800">{assignments.length}</p>
          </div>
        </div>
        
        <div className="glass p-5 rounded-2xl border border-slate-100/50 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-emerald-50 rounded-xl text-emerald-600">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{t.statsActive}</p>
            <p className="text-2xl font-bold text-emerald-600">
              {assignments.filter(a => a.status === 'active').length}
            </p>
          </div>
        </div>

        <div className="glass p-5 rounded-2xl border border-slate-100/50 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-slate-100 rounded-xl text-slate-600">
            <ClipboardList className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{t.statsFulfilled}</p>
            <p className="text-2xl font-bold text-slate-800">
              {assignments.filter(a => a.status === 'fulfilled').length}
            </p>
          </div>
        </div>
      </div>

      {/* Main List Container */}
      <div className="glass rounded-2xl overflow-hidden shadow-sm border border-slate-100/50">
        <AssignmentList
          assignments={assignments}
          onEdit={(assignment) => {
            if (assignment.status === 'active') {
              setEditingAssignment(assignment);
              setShowForm(true);
            }
          }}
          onDelete={handleDelete}
        />
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
          <div className="bg-white rounded-3xl p-8 max-w-lg w-full shadow-2xl border border-slate-100 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full -mr-16 -mt-16 blur-3xl"></div>
            
            <h2 className="text-2xl font-bold text-slate-800 mb-6 relative">
              {editingAssignment ? t.editAssignment : t.newAssignment}
            </h2>
            
            <ProductAssignmentForm
              assignment={editingAssignment}
              partners={partners}
              products={products}
              onSubmit={handleSubmit}
              onCancel={() => {
                setShowForm(false);
                setEditingAssignment(null);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}