"use client";

import { useWebSocketStockUpdates } from "@/lib/use-websocket";
import { ARABIC } from "@/lib/constants/arabic";

export default function ConnectionStatus() {
  const { isConnected } = useWebSocketStockUpdates();

  return (
    <div className="flex items-center gap-2">
      <div
        className={`w-2 h-2 rounded-full ${
          isConnected ? "bg-emerald-500" : "bg-red-500"
        }`}
      />
      <span className="text-sm text-slate-600">
        {isConnected ? "متصل" : "غير متصل"}
      </span>
    </div>
  );
}
