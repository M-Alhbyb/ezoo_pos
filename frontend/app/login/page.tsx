"use client";

import React from "react";
import Image from "next/image";
import { LogIn, ShieldCheck, Mail, Lock } from "lucide-react";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 relative overflow-hidden">
      {/* Decorative background elements */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-[120px] -ml-48 -mt-48 transition-all duration-1000 animate-pulse"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px] -mr-48 -mb-48 transition-all duration-1000 delay-500 animate-pulse"></div>

      <div className="w-full max-w-md relative z-10">
        <div className="glass-card p-10 rounded-[2.5rem] shadow-2xl border border-white/40">
          <div className="flex flex-col items-center mb-10">
            <div className="p-4 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-[1.5rem] shadow-xl mb-6 ring-4 ring-blue-50 ring-offset-0">
              <ShieldCheck className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-extrabold text-slate-900 font-heading tracking-tight">Welcome Back</h1>
            <p className="text-slate-500 mt-2 font-medium">Log in to your RAYON energy account</p>
          </div>

          <form className="space-y-6" onSubmit={(e) => e.preventDefault()}>
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ml-1">Email Address</label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-500 transition-colors duration-300">
                  <Mail className="w-5 h-5" />
                </div>
                <input
                  type="email"
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-300 font-medium"
                  placeholder="name@company.com"
                  defaultValue="admin@ezoo.pos"
                />
              </div>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center px-1">
                <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Password</label>
                <a href="#" className="text-xs font-bold text-blue-600 hover:text-blue-700 tracking-wide">Forgot?</a>
              </div>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-500 transition-colors duration-300">
                  <Lock className="w-5 h-5" />
                </div>
                <input
                  type="password"
                  className="w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-300 font-medium"
                  placeholder="••••••••"
                  defaultValue="password123"
                />
              </div>
            </div>

            <div className="pt-4">
              <button 
                type="submit" 
                className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-4 rounded-2xl shadow-xl shadow-slate-900/10 hover:shadow-slate-900/20 transition-all duration-300 flex items-center justify-center gap-3 active:scale-[0.98]"
              >
                <LogIn className="w-5 h-5" />
                Sign In
              </button>
            </div>
          </form>

          <div className="mt-10 pt-8 border-t border-slate-100 flex flex-col items-center gap-4">
            <p className="text-sm text-slate-500 font-medium">New to RAYON energy?</p>
            <button className="text-sm font-bold text-slate-900 hover:text-blue-600 transition-colors duration-300">
              Create an account
            </button>
          </div>
        </div>
        
        <div className="mt-8 flex justify-center gap-8">
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Privacy Policy</p>
            <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">Terms of Service</p>
        </div>
      </div>
    </div>
  );
}
