/**
 * AssignmentList Component
 * 
 * Displays list of product assignments with filtering and actions.
 * Task: T045 - Phase 7
 */

"use client";

import { useState } from "react";

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

interface AssignmentListProps {
  assignments: Assignment[];
  onEdit?: (assignment: Assignment) => void;
  onDelete?: (assignmentId: string) => void;
  onViewDetails?: (assignment: Assignment) => void;
}

export default function AssignmentList({
  assignments,
  onEdit,
  onDelete,
  onViewDetails,
}: AssignmentListProps) {
  const [filter, setFilter] = useState<'all' | 'active' | 'fulfilled'>('all');

  const filteredAssignments = assignments.filter(a => 
    filter === 'all' || a.status === filter
  );

  const statusColors = {
    active: 'bg-green-100 text-green-800',
    fulfilled: 'bg-slate-100 text-slate-600',
  };

  const statusLabels = {
    active: 'نشط',
    fulfilled: 'مكتمل',
  };

  return (
    <div className="space-y-4">
      {/* Filter Tabs */}
      <div className="flex gap-2">
        {(['all', 'active', 'fulfilled'] as const).map(status => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-xl transition-colors ${
              filter === status
                ? 'bg-primary text-white'
                : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
            }`}
          >
            {status === 'all' ? 'الكل' : statusLabels[status]}
          </button>
        ))}
      </div>

      {/* Assignment List */}
      {filteredAssignments.length === 0 ? (
        <div className="text-center py-12 text-slate-500">
          لا توجد مهام
        </div>
      ) : (
        <div className="space-y-3">
          {filteredAssignments.map(assignment => (
            <div
              key={assignment.id}
              className="bg-white border border-slate-200 rounded-xl p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start mb-3">
                <div>
                  <h3 className="font-medium text-slate-800">
                    {assignment.product_name}
                  </h3>
                  <p className="text-sm text-slate-500">
                    {assignment.partner_name}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[assignment.status]}`}>
                  {statusLabels[assignment.status]}
                </span>
              </div>

              <div className="grid grid-cols-3 gap-4 text-sm mb-3">
                <div>
                  <span className="text-slate-500">الكمية:</span>
                  <div className="font-medium text-slate-800">
                    {assignment.remaining_quantity} / {assignment.assigned_quantity}
                  </div>
                </div>
                <div>
                  <span className="text-slate-500">نسبة الربح:</span>
                  <div className="font-medium text-slate-800">
                    {assignment.share_percentage}%
                  </div>
                </div>
                <div>
                  <span className="text-slate-500">التقدم:</span>
                  <div className="font-medium text-slate-800">
                    {assignment.assigned_quantity > 0 
                      ? Math.round((assignment.remaining_quantity / assignment.assigned_quantity) * 100)
                      : 0
                    }%
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-slate-200 rounded-full h-2 mb-3">
                <div
                  className="bg-primary h-2 rounded-full transition-all"
                  style={{
                    width: `${assignment.assigned_quantity > 0 
                      ? ((assignment.assigned_quantity - assignment.remaining_quantity) / assignment.assigned_quantity) * 100
                      : 0}%`
                  }}
                />
              </div>

              {/* Actions */}
              <div className="flex gap-2">
                {onViewDetails && (
                  <button
                    onClick={() => onViewDetails(assignment)}
                    className="text-sm text-primary hover:text-primary/80"
                  >
                    عرض التفاصيل
                  </button>
                )}
                {assignment.status === 'active' && onEdit && (
                  <button
                    onClick={() => onEdit(assignment)}
                    className="text-sm text-slate-600 hover:text-slate-800"
                  >
                    تعديل
                  </button>
                )}
                {assignment.status === 'active' && onDelete && assignment.remaining_quantity === assignment.assigned_quantity && (
                  <button
                    onClick={() => onDelete(assignment.id)}
                    className="text-sm text-rose-600 hover:text-rose-800"
                  >
                    حذف
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}