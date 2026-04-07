'use client';

import React, { ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  className?: string;
}

export default function PageHeader({
  title,
  description,
  actions,
  className = ""
}: PageHeaderProps) {
  return (
    <div className={`flex flex-col md:flex-row justify-between items-start md:items-end gap-4 mb-8 ${className}`}>
      <div>
        <h1 className="text-4xl font-extrabold font-heading text-slate-900 tracking-tight">{title}</h1>
        {description && (
          <p className="text-slate-500 mt-2 font-medium">{description}</p>
        )}
      </div>
      {actions && (
        <div className="flex items-center gap-3">
          {actions}
        </div>
      )}
    </div>
  );
}
