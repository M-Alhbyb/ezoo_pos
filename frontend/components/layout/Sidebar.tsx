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
  History,
  Truck,
  User
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
  { href: '/suppliers', icon: Truck, label: ARABIC.nav.suppliers },
  { href: '/customers', icon: User, label: ARABIC.customers.title },
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
          w-56 glass flex flex-col border-s border-slate-200 fixed inset-y-0 right-0 z-50 transform transition-transform duration-300 ease-in-out
          md:relative md:translate-x-0 
          ${isMobileOpen ? "translate-x-0 shadow-2xl" : "translate-x-full"}
        `}
      >
        <div className="p-3 flex flex-col items-center relative border-b border-slate-100">
          <Image src="/logo.png" alt="RAYON energy Logo" width={40} height={40} className="rounded-lg" />

        </div>

        <nav className="flex-1 px-2 py-2 text-slate-600 font-medium tracking-wide overflow-y-auto custom-scrollbar">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onMobileClose}
                className={`
                  flex items-center gap-2 px-3 py-2 rounded-lg transition-all duration-200 group text-sm
                  ${isActive 
                    ? 'bg-blue-50 text-blue-600' 
                    : 'hover:bg-slate-50 hover:text-blue-600'
                  }
                `}
              >
                <item.icon className="w-4 h-4" />
                {item.label}
              </Link>
            );
          })}
          
          <div className="pt-4 pb-2 mt-2">
            <p className="px-3 text-[9px] font-bold tracking-wider text-slate-400 uppercase">التقارير</p>
          </div>
          
          {reportItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onMobileClose}
                className={`
                  flex items-center gap-2 px-3 py-1.5 text-xs font-medium transition-all duration-200
                  ${isActive 
                    ? 'text-blue-600' 
                    : 'text-slate-400 hover:text-blue-600'
                  }
                `}
              >
                <div className={`w-1 h-1 rounded-full ${item.color}`}></div>
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
