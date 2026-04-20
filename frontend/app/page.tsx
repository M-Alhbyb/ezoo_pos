import Link from "next/link";

export default function HomePage() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-bold font-heading text-slate-800 tracking-tight">Overview</h1>
          <p className="text-slate-500 mt-1">Welcome back to EZOO POS. Here is what is happening today.</p>
        </div>
        <div className="text-sm font-medium text-slate-500 bg-white px-4 py-2 rounded-lg border border-slate-200 shadow-sm">
          {new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Stat Card 1 */}
        <div className="glass p-6 rounded-2xl animate-slide-up" style={{ animationDelay: "0ms" }}>
          <div className="flex items-center justify-between">
            <h3 className="text-slate-500 font-medium text-sm">Today&apos;s Sales</h3>
            <span className="p-2 bg-blue-50 text-blue-600 rounded-lg">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </span>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-bold text-slate-800">$0.00</span>
            <div className="text-sm text-green-500 font-medium mt-1">Ready for business</div>
          </div>
        </div>

        {/* Stat Card 2 */}
        <div className="glass p-6 rounded-2xl animate-slide-up" style={{ animationDelay: "100ms" }}>
          <div className="flex items-center justify-between">
            <h3 className="text-slate-500 font-medium text-sm">Active Products</h3>
            <span className="p-2 bg-indigo-50 text-indigo-600 rounded-lg">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path></svg>
            </span>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-bold text-slate-800">API Link</span>
            <div className="text-sm text-indigo-500 font-medium mt-1">Waiting for data...</div>
          </div>
        </div>

        {/* Stat Card 3 */}
        <div className="glass p-6 rounded-2xl animate-slide-up" style={{ animationDelay: "200ms" }}>
          <div className="flex items-center justify-between">
            <h3 className="text-slate-500 font-medium text-sm">Low Stock Alerts</h3>
            <span className="p-2 bg-rose-50 text-rose-600 rounded-lg">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
            </span>
          </div>
          <div className="mt-4">
            <span className="text-3xl font-bold text-slate-800 text-rose-600">0</span>
            <div className="text-sm text-rose-500 font-medium mt-1">Check inventory</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <h2 className="text-xl font-bold font-heading text-slate-800 mt-10 mb-4">Quick Actions</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up" style={{ animationDelay: "300ms" }}>
        <Link href="/pos" className="group bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-blue-300 transition-all flex items-center justify-between">
          <div>
            <div className="font-semibold text-slate-800 group-hover:text-blue-600 transition-colors">Start Sale</div>
            <div className="text-xs text-slate-500 mt-1">Open POS register</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-slate-50 group-hover:bg-blue-50 flex items-center justify-center text-slate-400 group-hover:text-blue-600 transition-colors">
            &rarr;
          </div>
        </Link>
        <Link href="/products" className="group bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-indigo-300 transition-all flex items-center justify-between">
          <div>
            <div className="font-semibold text-slate-800 group-hover:text-indigo-600 transition-colors">Manage Products</div>
            <div className="text-xs text-slate-500 mt-1">Add or edit catalog</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-slate-50 group-hover:bg-indigo-50 flex items-center justify-center text-slate-400 group-hover:text-indigo-600 transition-colors">
            &rarr;
          </div>
        </Link>
        <Link href="/inventory" className="group bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:border-emerald-300 transition-all flex items-center justify-between">
          <div>
            <div className="font-semibold text-slate-800 group-hover:text-emerald-600 transition-colors">Adjust Stock</div>
            <div className="text-xs text-slate-500 mt-1">Restock inventory</div>
          </div>
          <div className="w-10 h-10 rounded-full bg-slate-50 group-hover:bg-emerald-50 flex items-center justify-center text-slate-400 group-hover:text-emerald-600 transition-colors">
            &rarr;
          </div>
        </Link>
      </div>
    </div>
  );
}