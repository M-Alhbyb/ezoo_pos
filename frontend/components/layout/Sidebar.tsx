'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  ShoppingCart, 
  Package, 
  Users, 
  History
} from 'lucide-react';
import { ARABIC } from '@/lib/constants/arabic';

interface SidebarProps {
  isMobileOpen: boolean;
  onMobileClose: () => void;
}

const navItems = [
  { href: '/dashboard', icon: LayoutDashboard, label: ARABIC.nav.dashboard },
  { href: '/pos', icon: ShoppingCart, label: ARABIC.nav.pos },
  { href: '/products', icon: Package, label: ARABIC.nav.products },
  { href: '/inventory', icon: History, label: ARABIC.nav.inventory },
  { href: '/partners', icon: Users, label: ARABIC.nav.partners },
];

const reportItems = [
  { href: '/dashboard/reports/sales', label: ARABIC.nav.salesReport, color: 'bg-blue-400' },
  { href: '/dashboard/reports/partners', label: 'توزيعات الأرباح', color: 'bg-emerald-400' },
  { href: '/dashboard/reports/inventory', label: 'حركة المخزون', color: 'bg-rose-400' },
];

export default function Sidebar({ isMobileOpen, onMobileClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 md:hidden"
          onClick={onMobileClose}
        />
      )}

      <aside
        className={`
          w-64 glass flex flex-col border-s border-slate-200 fixed inset-y-0 right-0 z-50 transform transition-transform duration-300 ease-in-out
          md:relative md:translate-x-0 
          ${isMobileOpen ? "translate-x-0 shadow-2xl" : "translate-x-full"}
        `}
      >
        <div className="p-8 flex flex-col items-center relative">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
            <Image src="/logo.png" alt="RAYON energy Logo" width={100} height={100} className="relative rounded-2xl shadow-xl transition-transform duration-300" />
          </div>
          <div className="mt-6 text-center">
            <h2 className="text-xl font-bold text-slate-900 font-heading">RAYON energy</h2>
            <p className="text-[10px] font-bold text-blue-600 uppercase tracking-[0.2em] mt-1">نظام نقطة البيع</p>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-4 text-slate-600 font-medium tracking-wide overflow-y-auto custom-scrollbar">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onMobileClose}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-2xl transition-all duration-300 group
                  ${isActive 
                    ? 'bg-blue-50 text-blue-600' 
                    : 'hover:bg-slate-50 hover:text-blue-600'
                  }
                `}
              >
                <div className={`
                  p-2 rounded-xl transition-colors
                  ${isActive 
                    ? 'bg-blue-100 text-blue-600' 
                    : 'bg-slate-50 text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600'
                  }
                `}>
                  <item.icon className="w-5 h-5" />
                </div>
                {item.label}
              </Link>
            );
          })}
          
          <div className="pt-6 pb-2">
            <p className="px-4 text-[10px] font-bold tracking-[0.2em] text-slate-400 uppercase">التحليلات والتقارير</p>
          </div>
          
          {reportItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onMobileClose}
                className={`
                  flex items-center px-4 py-2 text-sm font-bold transition-all duration-200
                  ${isActive 
                    ? 'text-blue-600 -translate-x-1' 
                    : 'text-slate-500 hover:text-blue-600 hover:-translate-x-1'
                  }
                `}
              >
                <div className={`w-1.5 h-1.5 rounded-full ${item.color} ms-3`}></div>
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-6 border-t border-slate-100">
          <div className="p-4 bg-slate-50 rounded-2xl flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-700 flex items-center justify-center text-white font-bold shadow-lg shadow-blue-200">
              م
            </div>
            <div className="flex-1 truncate">
              <p className="text-sm font-bold text-slate-900 truncate">مدير النظام</p>
              <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">مدير</p>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
}
