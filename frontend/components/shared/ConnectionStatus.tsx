/**
 * Connection Status Indicator Component
 * 
 * Displays WebSocket connection status in real-time.
 */

"use client";

import { useWebSocketStockUpdates } from "@/lib/use-websocket";

export default function ConnectionStatus() {
  const { isConnected } = useWebSocketStockUpdates();

  return (
    <div className="flex items-center space-x-2">
      <div
        className={`w-2 h-2 rounded-full ${
          isConnected ? "bg-green-500" : "bg-red-500"
        }`}
      />
      <span className="text-sm text-gray-600">
        {isConnected ? "Connected" : "Disconnected"}
      </span>
    </div>
  );
}