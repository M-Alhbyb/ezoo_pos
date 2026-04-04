/**
 * Hook for subscribing to WebSocket stock updates.
 * 
 * Provides connection status and automatic stock updates.
 */

"use client";

import { useEffect, useState } from "react";
import { getWebSocketClient, WebSocketClient } from "@/lib/websocket-client";

export function useWebSocketStockUpdates(onStockUpdate?: (productId: string, quantity: number) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const [client] = useState<WebSocketClient>(() => getWebSocketClient());

  useEffect(() => {
    // Connect on mount
    client.connect();

    // Subscribe to connection status
    const unsubConnection = client.onConnectionStatusChange((connected) => {
      setIsConnected(connected);
    });

    // Subscribe to stock updates
    const unsubStock = onStockUpdate
      ? client.onStockUpdate((productId, quantity) => {
          if (onStockUpdate) {
            onStockUpdate(productId, quantity);
          }
        })
      : () => {};

    // Cleanup on unmount
    return () => {
      unsubConnection();
      unsubStock();
    };
  }, [client, onStockUpdate]);

  return { isConnected, client };
}