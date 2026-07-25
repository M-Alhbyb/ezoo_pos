"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { LogIn, ShieldCheck, Mail, Lock } from "lucide-react";
import { ARABIC } from "@/lib/constants/arabic";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated } = useAuth();
  const [email, setEmail] = useState("admin@ezoo.pos");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  if (isAuthenticated) {
    router.replace("/dashboard");
    return null;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.replace("/dashboard");
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 relative overflow-hidden">
      <div className="absolute top-0 start-0 w-96 h-96 bg-blue-500/10 rounded-full blur-[120px] -ms-48 -mt-48 transition-all duration-1000 animate-pulse"></div>
      <div className="absolute bottom-0 end-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-[120px] -me-48 -mb-48 transition-all duration-1000 delay-500 animate-pulse"></div>

      <div className="w-full max-w-md relative z-10">
        <div className="glass-card p-10 rounded-[2.5rem] shadow-2xl border border-white/40">
          <div className="flex flex-col items-center mb-10">
            <div className="p-4 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-[1.5rem] shadow-xl mb-6 ring-4 ring-blue-50 ring-offset-0">
              <ShieldCheck className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-extrabold text-slate-900 font-heading tracking-tight">{ARABIC.auth.welcomeBack}</h1>
            <p className="text-slate-500 mt-2 font-medium">{ARABIC.auth.loginToAccount}</p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-sm text-center font-medium">
                {error}
              </div>
            )}

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest ms-1">{ARABIC.auth.emailAddress}</label>
              <div className="relative group">
                <div className="absolute inset-y-0 start-0 ps-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-500 transition-colors duration-300">
                  <Mail className="w-5 h-5" />
                </div>
                <input
                  type="email"
                  className="w-full ps-12 pe-4 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-300 font-medium"
                  placeholder="admin@ezoo.pos"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  dir="ltr"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-widest px-1">{ARABIC.auth.password}</label>
              <div className="relative group">
                <div className="absolute inset-y-0 start-0 ps-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-500 transition-colors duration-300">
                  <Lock className="w-5 h-5" />
                </div>
                <input
                  type="password"
                  className="w-full ps-12 pe-4 py-4 bg-slate-50 border border-slate-200 rounded-2xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 outline-none transition-all duration-300 font-medium"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  dir="ltr"
                />
              </div>
            </div>

            <div className="pt-4">
              <button 
                type="submit" 
                disabled={loading}
                className="w-full bg-slate-900 hover:bg-slate-800 text-white font-bold py-4 rounded-2xl shadow-xl shadow-slate-900/10 hover:shadow-slate-900/20 transition-all duration-300 flex items-center justify-center gap-3 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <LogIn className="w-5 h-5" />
                {loading ? "..." : ARABIC.auth.signIn}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
