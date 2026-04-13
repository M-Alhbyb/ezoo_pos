"use client";

import { useState } from "react";
import { ARABIC } from "@/lib/constants/arabic";
import { Edit2, Trash2, Package, User, Hash, Percent, TrendingUp } from "lucide-react";

export interface Assignment {
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
}

export default function AssignmentList({
  assignments,
  onEdit,
  onDelete,
}: AssignmentListProps) {
  const [filter, setFilter] = useState<'all' | 'active' | 'fulfilled'>('all');
  const t = ARABIC.partners.assignments;

  const filteredAssignments = assignments.filter(a => 
    filter === 'all' || a.status === filter
  );

  const statusColors = {
    active: 'bg-emerald-50 text-emerald-700 border-emerald-100',
    fulfilled: 'bg-slate-50 text-slate-600 border-slate-100',
  };

  const statusLabels = {
    active: t.active,
    fulfilled: t.fulfilled,
  };

  return (
    <div className="space-y-6">
      {/* Filter Tabs */}
      <div className="flex gap-2 p-4 bg-slate-50/50 border-b border-slate-100">
        {(['all', 'active', 'fulfilled'] as const).map(status => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              filter === status
                ? 'bg-white text-primary shadow-sm border border-slate-200'
                : 'text-slate-500 hover:bg-white/50'
            }`}
          >
            {status === 'all' ? t.all : statusLabels[status]}
          </button>
        ))}
      </div>

      {/* Assignment List */}
      <div className="px-6 pb-6">
        {filteredAssignments.length === 0 ? (
          <div className="text-center py-20 text-slate-400">
            <Package className="w-12 h-12 mx-auto mb-3 opacity-20" />
            <p>{t.noAssignments}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {filteredAssignments.map(assignment => {
              const progress = assignment.assigned_quantity > 0 
                ? Math.round(((assignment.assigned_quantity - assignment.remaining_quantity) / assignment.assigned_quantity) * 100)
                : 0;

              return (
                <div
                  key={assignment.id}
                  className="bg-white border border-slate-100 rounded-2xl p-5 hover:border-primary/30 hover:shadow-lg hover:shadow-slate-100 transition-all group"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-start gap-3">
                      <div className="p-2.5 bg-indigo-50 rounded-xl text-indigo-600 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
                        <Package className="w-5 h-5" />
                      </div>
                      <div>
                        <h3 className="font-bold text-slate-800 leading-tight">
                          {assignment.product_name}
                        </h3>
                        <div className="flex items-center gap-1.5 text-sm text-slate-500 mt-1">
                          <User className="w-3.5 h-3.5" />
                          {assignment.partner_name}
                        </div>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border ${statusColors[assignment.status]}`}>
                      {statusLabels[assignment.status]}
                    </span>
                  </div>

                  <div className="grid grid-cols-3 gap-3 mb-5">
                    <div className="bg-slate-50 rounded-xl p-3">
                      <div className="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase mb-1">
                        <Hash className="w-3 h-3" />
                        {t.quantity}
                      </div>
                      <div className="text-sm font-bold text-slate-800">
                        {assignment.remaining_quantity} <span className="text-slate-400 font-normal">/ {assignment.assigned_quantity}</span>
                      </div>
                    </div>
                    <div className="bg-slate-50 rounded-xl p-3">
                      <div className="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase mb-1">
                        <Percent className="w-3 h-3" />
                        {t.share}
                      </div>
                      <div className="text-sm font-bold text-indigo-600">
                        {parseFloat(assignment.share_percentage).toFixed(1)}%
                      </div>
                    </div>
                    <div className="bg-slate-50 rounded-xl p-3">
                      <div className="flex items-center gap-1 text-[10px] font-bold text-slate-400 uppercase mb-1">
                        <TrendingUp className="w-3 h-3" />
                        التقدم
                      </div>
                      <div className="text-sm font-bold text-emerald-600">
                        {progress}%
                      </div>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-5">
                    <div className="w-full bg-slate-100 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-primary h-full transition-all duration-500 ease-out"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-end gap-2 border-t border-slate-50 pt-4">
                    {assignment.status === 'active' && onEdit && (
                      <button
                        onClick={() => onEdit(assignment)}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 hover:text-primary hover:bg-primary/5 rounded-lg transition-all"
                      >
                        <Edit2 className="w-3.5 h-3.5" />
                        {ARABIC.common.edit}
                      </button>
                    )}
                    {assignment.status === 'active' && onDelete && assignment.remaining_quantity === assignment.assigned_quantity && (
                      <button
                        onClick={() => onDelete(assignment.id)}
                        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50 rounded-lg transition-all"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                        {ARABIC.common.delete}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}