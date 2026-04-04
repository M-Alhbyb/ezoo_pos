/**
 * WebSocket client for real-time stock updates.
 * 
 * Provides connection management, auto-reconnect logic, and event handling.
 * Task: T112-T116
 */

export interface StockUpdateEvent {
  event: "stock_updated" | "stock_updated_batch";
  data:
  | {
    product_id: string;
    stock_quantity: number;
  }
  | Array<{
    product_id: string;
    stock_quantity: number;
  }>;
}

export type StockUpdateCallback = (productId: string, quantity: number) => void;
export type ConnectionStatusCallback = (connected: boolean) => void;

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private isManualClose = false;
  private stockUpdateCallbacks: Set<StockUpdateCallback> = new Set();
  private connectionStatusCallbacks: Set<ConnectionStatusCallback> = new Set();
  private heartbeatInterval: NodeJS.Timeout | null = null;

  constructor(url?: string) {
    this.url = url || process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000/ws/stock-updates";
  }

  /**
   * Connect to WebSocket server.
   */
  connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      console.log("[WebSocket] Already connected or connecting");
      return;
    }

    this.isManualClose = false;
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      console.log("[WebSocket] Connected to stock updates");
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
      this.notifyConnectionStatus(true);
      this.startHeartbeat();
    };

    this.ws.onmessage = (event) => {
      try {
        const message: StockUpdateEvent = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (error) {
        console.error("[WebSocket] Error parsing message:", error);
      }
    };

    this.ws.onerror = (error) => {
      console.error("[WebSocket] Error:", error);
    };

    this.ws.onclose = (event) => {
      console.log("[WebSocket] Disconnected:", event.code, event.reason);
      this.notifyConnectionStatus(false);
      this.stopHeartbeat();

      // Auto-reconnect if not manual close
      if (!this.isManualClose) {
        this.scheduleReconnect();
      }
    };
  }

  /**
   * Disconnect from WebSocket server.
   */
  disconnect(): void {
    this.isManualClose = true;
    this.stopHeartbeat();

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }

    if (this.ws) {
      this.ws.close(1000, "Manual disconnect");
      this.ws = null;
    }

    this.notifyConnectionStatus(false);
  }

  /**
   * Subscribe to stock update events.
   */
  onStockUpdate(callback: StockUpdateCallback): () => void {
    this.stockUpdateCallbacks.add(callback);

    // Return unsubscribe function
    return () => {
      this.stockUpdateCallbacks.delete(callback);
    };
  }

  /**
   * Subscribe to connection status changes.
   */
  onConnectionStatusChange(callback: ConnectionStatusCallback): () => void {
    this.connectionStatusCallbacks.add(callback);

    // Return unsubscribe function
    return () => {
      this.connectionStatusCallbacks.delete(callback);
    };
  }

  /**
   * Check if currently connected.
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Handle incoming WebSocket message.
   */
  private handleMessage(message: StockUpdateEvent): void {
    if (message.event === "stock_updated") {
      const data = message.data as { product_id: string; stock_quantity: number };
      this.notifyStockUpdate(data.product_id, data.stock_quantity);
    } else if (message.event === "stock_updated_batch") {
      const data = message.data as Array<{ product_id: string; stock_quantity: number }>;
      for (const update of data) {
        this.notifyStockUpdate(update.product_id, update.stock_quantity);
      }
    }
  }

  /**
   * Notify all stock update callbacks.
   */
  private notifyStockUpdate(productId: string, quantity: number): void {
    for (const callback of Array.from(this.stockUpdateCallbacks)) {
      try {
        callback(productId, quantity);
      } catch (error) {
        console.error("[WebSocket] Error in stock update callback:", error);
      }
    }
  }

  /**
   * Notify all connection status callbacks.
   */
  private notifyConnectionStatus(connected: boolean): void {
    for (const callback of Array.from(this.connectionStatusCallbacks)) {
      try {
        callback(connected);
      } catch (error) {
        console.error("[WebSocket] Error in connection status callback:", error);
      }
    }
  }

  /**
   * Schedule reconnection attempt.
   */
  private scheduleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("[WebSocket] Max reconnection attempts reached");
      return;
    }

    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts),
      this.maxReconnectDelay
    );

    console.log(`[WebSocket] Reconnecting in ${delay / 1000} seconds...`);

    this.reconnectTimeout = setTimeout(() => {
      this.reconnectAttempts++;
      this.connect();
    }, delay);
  }

  /**
   * Start heartbeat to keep connection alive.
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: "ping" }));
      }
    }, 30000); // Send heartbeat every 30 seconds
  }

  /**
   * Stop heartbeat.
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
}

// Singleton instance
let wsClient: WebSocketClient | null = null;

/**
 * Get the WebSocket client singleton instance.
 */
export function getWebSocketClient(): WebSocketClient {
  if (!wsClient) {
    wsClient = new WebSocketClient();
  }
  return wsClient;
}