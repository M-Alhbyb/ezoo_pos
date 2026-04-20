"use client";

import React, { useState } from "react";
import { 
  LayoutDashboard, 
  ShoppingCart, 
  Package, 
  Users, 
  Settings,
  TrendingUp,
  History,
  Menu,
  X,
  Plus
} from "lucide-react";
import { Inter, Cairo } from "next/font/google";
import Link from "next/link";
import Image from "next/image";
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
            w-64 glass flex flex-col border-l border-r border-slate-200 fixed inset-y-0 right-0 z-50 transform transition-transform duration-300 ease-in-out
            md:relative md:translate-x-0 
            ${isMobileMenuOpen ? "translate-x-0 shadow-2xl" : "translate-x-full"}
          `}>
            <div className="p-8 flex flex-col items-center relative">
              <div className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200"></div>
                <Image src="/logo.png" alt="RAYON energy Logo" width={100} height={100} className="relative rounded-2xl shadow-xl transition-transform duration-300" />
              </div>
              <button 
                className="md:hidden absolute top-2 start-2 p-2 text-slate-400 hover:text-slate-600 rounded-xl bg-slate-100/50"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <X className="w-5 h-5" />
              </button>
              <div className="mt-6 text-center">
                 <h2 className="text-xl font-bold text-slate-900 font-heading">RAYON energy</h2>
                 <p className="text-[10px] font-bold text-blue-600 uppercase tracking-[0.2em] mt-1">نظام نقطة البيع</p>
              </div>
            </div>

            <nav className="flex-1 px-4 space-y-2 mt-4 text-slate-600 font-medium tracking-wide overflow-y-auto custom-scrollbar">
              <Link href="/dashboard" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 hover:text-blue-600 rounded-2xl transition-all duration-300 group">
                <div className="p-2 bg-slate-50 text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 rounded-xl transition-colors">
                  <LayoutDashboard className="w-5 h-5" />
                </div>
                لوحة التحكم
              </Link>
              <Link href="/pos" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 hover:text-blue-600 rounded-2xl transition-all duration-300 group">
                <div className="p-2 bg-slate-50 text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 rounded-xl transition-colors">
                  <ShoppingCart className="w-5 h-5" />
                </div>
                نقطة البيع
              </Link>
              <Link href="/products" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 hover:text-blue-600 rounded-2xl transition-all duration-300 group">
                <div className="p-2 bg-slate-50 text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 rounded-xl transition-colors">
                   <Package className="w-5 h-5" />
                </div>
                المنتجات
              </Link>
              <Link href="/inventory" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 hover:text-blue-600 rounded-2xl transition-all duration-300 group">
                <div className="p-2 bg-slate-50 text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 rounded-xl transition-colors">
                   <History className="w-5 h-5" />
                </div>
                المخزون
              </Link>
              <Link href="/partners" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 hover:text-blue-600 rounded-2xl transition-all duration-300 group">
                <div className="p-2 bg-slate-50 text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 rounded-xl transition-colors">
                   <Users className="w-5 h-5" />
                </div>
                الشركاء
              </Link>
              <Link href="/settings" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center gap-3 px-4 py-3 hover:bg-slate-50 hover:text-blue-600 rounded-2xl transition-all duration-300 group">
                <div className="p-2 bg-slate-50 text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 rounded-xl transition-colors">
                   <Settings className="w-5 h-5" />
                </div>
                الإعدادات
              </Link>
              
              <div className="pt-6 pb-2">
                <p className="px-4 text-[10px] font-bold tracking-[0.2em] text-slate-400 uppercase">التحليلات والتقارير</p>
              </div>
              <Link href="/dashboard/reports/sales" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center px-4 py-2 text-sm font-bold text-slate-500 hover:text-blue-600 hover:-translate-x-1 transition-all duration-200">
                <div className="w-1.5 h-1.5 rounded-full bg-blue-400 ms-3"></div>
                تقارير المبيعات
              </Link>
              <Link href="/dashboard/reports/partners" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center px-4 py-2 text-sm font-bold text-slate-500 hover:text-emerald-600 hover:-translate-x-1 transition-all duration-200">
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 ms-3"></div>
                توزيعات الأرباح
              </Link>
              <Link href="/dashboard/reports/inventory" onClick={() => setIsMobileMenuOpen(false)} className="flex items-center px-4 py-2 text-sm font-bold text-slate-500 hover:text-rose-600 hover:-translate-x-1 transition-all duration-200">
                <div className="w-1.5 h-1.5 rounded-full bg-rose-400 ms-3"></div>
                حركة المخزون
              </Link>
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

          <main className="flex-1 overflow-y-auto h-full">
            <div className="md:hidden glass p-4 flex justify-between items-center sticky top-0 z-40 border-b border-slate-200">
              <div className="flex items-center gap-2">
                <Image src="/logo.png" alt="RAYON energy Logo" width={32} height={32} className="rounded-lg shadow-sm" />
                <h1 className="text-lg font-bold text-slate-900 font-heading">RAYON energy</h1>
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
