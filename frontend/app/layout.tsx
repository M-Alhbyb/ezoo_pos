import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import Link from "next/link";
import Image from "next/image";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-outfit" });

export const metadata: Metadata = {
  title: "RAYON energy | Premium Sales Suite",
  description: "Next-Generation Point of Sale System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${outfit.variable} font-sans`}>
        <div className="flex min-h-screen bg-slate-50">
          {/* Glassmorphic Sidebar */}
          <aside className="w-64 glass hidden md:flex flex-col border-r border-slate-200">
            <div className="p-8 flex justify-center">
              <Image src="/logo.png" alt="RAYON energy Logo" width={120} height={120} className="rounded-2xl shadow-lg hover:scale-105 transition-transform duration-300" />
            </div>

            <nav className="flex-1 px-4 space-y-2 mt-4 text-slate-600 font-medium tracking-wide">
              <Link href="/" className="flex items-center px-4 py-3 hover:bg-slate-100/50 rounded-xl transition-all">
                <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
                Dashboard
              </Link>
              <Link href="/pos" className="flex items-center px-4 py-3 hover:bg-slate-100/50 rounded-xl transition-all">
                <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                Point of Sale
              </Link>
              <Link href="/products" className="flex items-center px-4 py-3 hover:bg-slate-100/50 rounded-xl transition-all">
                <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path></svg>
                Products
              </Link>
              <Link href="/inventory" className="flex items-center px-4 py-3 hover:bg-slate-100/50 rounded-xl transition-all">
                <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>
                Inventory
              </Link>
              <Link href="/settings" className="flex items-center px-4 py-3 hover:bg-slate-100/50 rounded-xl transition-all">
                <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                Settings
              </Link>
            </nav>

            <div className="p-4 border-t border-slate-200">
              <div className="flex items-center">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[#073053] to-[#F69826] shadow-inner"></div>
                <div className="ml-3">
                  <p className="text-sm font-semibold text-slate-800">Admin User</p>
                  <p className="text-xs text-slate-500">Store Manager</p>
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content Area */}
          <main className="flex-1 overflow-x-hidden overflow-y-auto">
            {/* Topbar Mobile */}
            <div className="md:hidden glass p-4 flex justify-between items-center sticky top-0 z-20">
              <div className="flex items-center gap-2">
                <Image src="/logo.png" alt="RAYON energy Logo" width={32} height={32} className="rounded-md shadow-sm" />
                <h1 className="text-xl font-bold text-gradient font-heading">RAYON energy</h1>
              </div>
              <button className="p-2 text-slate-600 rounded bg-slate-100">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
              </button>
            </div>

            <div className="p-4 md:p-8 animate-fade-in max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}