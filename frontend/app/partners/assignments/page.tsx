/**
 * Assignment Management Page
 * 
 * Page for managing product assignments to partners.
 * Task: T047 - Phase 7
 */

"use client";

import { useState, useEffect } from "react";
import ProductAssignmentForm from "@/components/partners/ProductAssignmentForm";
import AssignmentList from "@/components/partners/AssignmentList";

interface Assignment {
  id: string;
  partner_id: string;
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
  id: string;
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

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [assignmentsRes, partnersRes, productsRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/partners/assignments'),
        fetch('http://localhost:8000/api/v1/partners'),
        fetch('http://localhost:8000/api/v1/products'),
      ]);

      if (!assignmentsRes.ok || !partnersRes.ok || !productsRes.ok) {
        throw new Error('فشل في جلب البيانات');
      }

      const assignmentsData = await assignmentsRes.json();
      const partnersData = await partnersRes.json();
      const productsData = await productsRes.json();

      setAssignments(assignmentsData || []);
      setPartners(partnersData || []);
      setProducts(productsData || []);
    } catch (err: any) {
      setError(err.message || 'حدث خطأ');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (data: Partial<Assignment>) => {
    const url = editingAssignment
      ? `http://localhost:8000/api/v1/partners/assignments/${editingAssignment.id}`
      : 'http://localhost:8000/api/v1/partners/assignments';
    
    const method = editingAssignment ? 'PATCH' : 'POST';

    const response = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'فشل في حفظ المهمة');
    }

    setShowForm(false);
    setEditingAssignment(null);
    await fetchData();
  };

  const handleDelete = async (assignmentId: string) => {
    if (!confirm('هل أنت متأكد من حذف هذه المهمة؟')) return;

    const response = await fetch(
      `http://localhost:8000/api/v1/partners/assignments/${assignmentId}`,
      { method: 'DELETE' }
    );

    if (!response.ok) {
      const errorData = await response.json();
      alert(errorData.detail || 'فشل في حذف المهمة');
      return;
    }

    await fetchData();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-slate-500">جارٍ التحميل...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">إدارة تخصيصات المنتجات</h1>
          <p className="text-slate-500 mt-1">تخصيص منتجات للشركاء وتتبع مكاسبهم</p>
        </div>
        <button
          onClick={() => {
            setEditingAssignment(null);
            setShowForm(true);
          }}
          className="bg-primary text-white px-6 py-2 rounded-xl hover:bg-primary/90 transition-colors"
        >
          + مهمة جديدة
        </button>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-600 rounded-xl p-4 mb-6">
          {error}
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold text-slate-800 mb-4">
              {editingAssignment ? 'تعديل المهمة' : 'مهمة جديدة'}
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

      <AssignmentList
        assignments={assignments}
        onEdit={(assignment) => {
          if (assignment.status === 'active') {
            setEditingAssignment(assignment);
            setShowForm(true);
          }
        }}
        onDelete={handleDelete}
        onViewDetails={(assignment) => {
          alert(`تفاصيل المهمة:\nالمنتج: ${assignment.product_name}\nالشريك: ${assignment.partner_name}\nالكمية: ${assignment.remaining_quantity} / ${assignment.assigned_quantity}\nالنسبة: ${assignment.share_percentage}%`);
        }}
      />

      {/* Stats Summary */}
      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <div className="text-sm text-slate-500">إجمالي المهام</div>
          <div className="text-2xl font-bold text-slate-800">{assignments.length}</div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <div className="text-sm text-slate-500">المهام النشطة</div>
          <div className="text-2xl font-bold text-green-600">
            {assignments.filter(a => a.status === 'active').length}
          </div>
        </div>
        <div className="bg-white border border-slate-200 rounded-xl p-4">
          <div className="text-sm text-slate-500">المهام المكتملة</div>
          <div className="text-2xl font-bold text-slate-600">
            {assignments.filter(a => a.status === 'fulfilled').length}
          </div>
        </div>
      </div>
    </div>
  );
}