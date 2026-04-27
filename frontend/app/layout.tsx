"use client";

import React, { useState } from "react";
import { 
  LayoutDashboard, 
  ShoppingCart, 
  Package, 
  Users, 
  Settings,
  History,
  Menu,
  X,
  Truck,
  User
} from "lucide-react";
import { Inter, Cairo } from "next/font/google";
import Link from "next/link";
import Image from "next/image";
import { ARABIC } from "@/lib/constants/arabic";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const cairo = Cairo({ 
  subsets: ["arabic", "latin"], 
  variable: "--font-cairo",
  weight: ["200", "300", "400", "500", "600", "700", "800", "900"]
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <html lang="ar" dir="rtl">
      <body className={`${inter.variable} ${cairo.variable} font-sans`}>
        <div className="flex h-screen bg-slate-50 relative overflow-hidden">
          {isMobileMenuOpen && (
            <div 
              className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 md:hidden transition-opacity duration-300"
              onClick={() => setIsMobileMenuOpen(false)}
            />
          )}

<aside className={`
            w-56 glass flex flex-col border-l border-slate-200 fixed inset-y-0 right-0 z-50 transform transition-transform duration-300 ease-in-out
            md:relative md:translate-x-0 
            ${isMobileMenuOpen ? "translate-x-0 shadow-2xl" : "translate-x-full"}
          `}>
            <div className="p-4 flex flex-col items-center relative border-b border-slate-100">
              <Image src="/logo.png" alt="RAYON" width={48} height={48} className="rounded-xl" />
            </div>

            <nav className="flex-1 px-3 py-3 text-slate-600 font-medium tracking-wide overflow-y-auto custom-scrollbar">
              <Link href="/dashboard" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-all duration-200 text-sm">
                <LayoutDashboard className="w-4 h-4" />
                لوحة التحكم
              </Link>
              <Link href="/pos" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-all duration-200 text-sm">
                <ShoppingCart className="w-4 h-4" />
                نقطة البيع
              </Link>
              <Link href="/products" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-all duration-200 text-sm">
                <Package className="w-4 h-4" />
                المنتجات
              </Link>
              <Link href="/inventory" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-all duration-200 text-sm">
                <History className="w-4 h-4" />
                المخزون
              </Link>
              <Link href="/partners" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-all duration-200 text-sm">
                <Users className="w-4 h-4" />
                الشركاء
              </Link>
              <Link href="/suppliers" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-all duration-200 text-sm">
                <Truck className="w-4 h-4" />
                الموردين
              </Link>
              <Link href="/customers" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-all duration-200 text-sm">
                <User className="w-4 h-4" />
                العملاء
              </Link>
              <Link href="/settings" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-2.5 hover:bg-slate-50 hover:text-blue-600 rounded-lg transition-all duration-200 text-sm">
                <Settings className="w-4 h-4" />
                الإعدادات
              </Link>
              
              <div className="pt-4 pb-2 mt-1">
                <p className="px-3 text-[9px] font-bold tracking-wider text-slate-400 uppercase">التقارير</p>
              </div>
              <Link href="/dashboard/reports/sales" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-blue-600 transition-all duration-200">
                <div className="w-1 h-1 rounded-full bg-blue-400"></div>
                تقارير المبيعات
              </Link>
              <Link href="/dashboard/reports/partners" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-emerald-600 transition-all duration-200">
                <div className="w-1 h-1 rounded-full bg-emerald-400"></div>
                توزيعات الأرباح
              </Link>
              <Link href="/dashboard/reports/inventory" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-rose-600 transition-all duration-200">
                <div className="w-1 h-1 rounded-full bg-rose-400"></div>
                حركة المخزون
              </Link>
            </nav>
          </aside>

          <main className="flex-1 overflow-y-auto h-full">
            <div className="md:hidden glass p-4 flex justify-between items-center sticky top-0 z-40 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <Image src="/logo.png" alt="RAYON energy Logo" width={32} height={32} className="rounded-lg shadow-sm" />
              </div>
              <button 
                className="p-2.5 text-slate-600 rounded-xl bg-white border border-slate-200 shadow-sm transition-all active:scale-95"
                onClick={() => setIsMobileMenuOpen(true)}
              >
                <Menu className="w-6 h-6" />
              </button>
            </div>

            <div className="p-6 md:p-10 animate-in fade-in duration-700 max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
