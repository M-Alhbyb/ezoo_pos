"use client";

import React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

export interface Column<T> {
  header: string;
  accessor: string;
  render?: (item: T) => React.ReactNode;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  loading?: boolean;
  emptyMessage?: string;
  // Pagination Props
  totalItems?: number;
  pageSize?: number;
  currentPage?: number;
  onPageChange?: (page: number) => void;
}

export function DataTable<T>({
  columns,
  data,
  loading = false,
  emptyMessage = "No data available",
  totalItems = 0,
  pageSize = 50,
  currentPage = 1,
  onPageChange
}: DataTableProps<T>) {
  const totalPages = Math.ceil(totalItems / pageSize);

  return (
    <div className="flex flex-col gap-4">
      <div className="overflow-x-auto rounded-[1.5rem] border border-slate-100 bg-white shadow-sm overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/50 border-b border-slate-100">
              {columns.map((column, idx) => (
                <th
                  key={idx}
                  className={`px-6 py-4 text-xs font-bold text-slate-500 uppercase tracking-widest ${column.className || ""}`}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              [...Array(5)].map((_, i) => (
                <tr key={i} className="animate-pulse">
                  {columns.map((_, idx) => (
                    <td key={idx} className="px-6 py-4 border-b border-slate-50">
                      <div className="h-4 bg-slate-100 rounded w-24"></div>
                    </td>
                  ))}
                </tr>
              ))
            ) : data.length > 0 ? (
              data.map((item, rowIdx) => (
                <tr
                  key={rowIdx}
                  className="hover:bg-slate-50/80 transition-colors duration-200 group"
                >
                  {columns.map((column, colIdx) => (
                    <td
                      key={colIdx}
                      className={`px-6 py-4 text-sm font-medium text-slate-700 border-b border-slate-50 group-last:border-none ${column.className || ""}`}
                    >
                      {column.render
                        ? column.render(item)
                        : (item as any)[column.accessor]?.toString()}
                    </td>
                  ))}
                </tr>
              ))
            ) : (
              <tr>
                <td
                  colSpan={columns.length}
                  className="px-6 py-12 text-center text-slate-400 font-medium"
                >
                  <div className="flex flex-col items-center gap-2">
                    <p>{emptyMessage}</p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Controls */}
      {totalPages > 1 && onPageChange && (
        <div className="flex items-center justify-between px-4 py-2 bg-white/50 backdrop-blur-md rounded-2xl border border-slate-100">
          <div className="text-sm font-semibold text-slate-500">
            Showing <span className="text-slate-900">{(currentPage - 1) * pageSize + 1}</span> to <span className="text-slate-900">{Math.min(currentPage * pageSize, totalItems)}</span> of <span className="text-slate-900">{totalItems}</span> items
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => onPageChange(currentPage - 1)}
              disabled={currentPage === 1 || loading}
              className="p-2 rounded-xl bg-white border border-slate-200 text-slate-400 hover:text-blue-600 hover:border-blue-200 disabled:opacity-50 disabled:hover:text-slate-400 disabled:hover:border-slate-200 transition-all duration-200"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            <div className="flex items-center gap-1">
              {[...Array(totalPages)].map((_, i) => {
                const pageNum = i + 1;
                // Only show a few pages around current if many
                if (totalPages > 7) {
                   if (pageNum !== 1 && pageNum !== totalPages && Math.abs(pageNum - currentPage) > 1) {
                      if (pageNum === 2 || pageNum === totalPages - 1) return <span key={pageNum} className="px-2 text-slate-300">...</span>;
                      return null;
                   }
                }
                return (
                  <button
                    key={pageNum}
                    onClick={() => onPageChange(pageNum)}
                    className={`min-w-[2.5rem] h-10 rounded-xl font-bold transition-all duration-200 ${
                      currentPage === pageNum
                        ? "bg-blue-600 text-white shadow-lg shadow-blue-600/20"
                        : "bg-white border border-slate-200 text-slate-600 hover:border-blue-200 hover:text-blue-600"
                    }`}
                  >
                    {pageNum}
                  </button>
                );
              })}
            </div>
            <button
              onClick={() => onPageChange(currentPage + 1)}
              disabled={currentPage === totalPages || loading}
              className="p-2 rounded-xl bg-white border border-slate-200 text-slate-400 hover:text-blue-600 hover:border-blue-200 disabled:opacity-50 disabled:hover:text-slate-400 disabled:hover:border-slate-200 transition-all duration-200"
            >
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
