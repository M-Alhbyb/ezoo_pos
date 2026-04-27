'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { Menu } from 'lucide-react';

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  return (
    <div className="md:hidden glass p-4 flex justify-between items-center sticky top-0 z-40 border-b border-slate-200">
      <div className="flex items-center gap-2">
        <Image src="/logo.png" alt="RAYON energy Logo" width={32} height={32} className="rounded-lg shadow-sm" />
      </div>
      <button 
        className="p-2.5 text-slate-600 rounded-xl bg-white border border-slate-200 shadow-sm transition-all active:scale-95"
        onClick={onMenuClick}
      >
        <Menu className="w-6 h-6" />
      </button>
    </div>
  );
}
