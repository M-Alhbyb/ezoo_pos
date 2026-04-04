"""
WebSocket connection manager for real-time updates.

Manages WebSocket connections for broadcasting real-time stock updates to POS clients.
"""

from typing import Set
from fastapi import WebSocket
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time stock updates.

    This manager maintains active WebSocket connections and provides
    methods to broadcast stock level changes to all connected clients.

    Constitution II (Single Source of Truth):
    - Backend is the sole authority for stock levels
    - WebSocket only broadcasts updates, clients receive and display
    """

    def __init__(self):
        """Initialize the connection manager."""
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """
        Accept a new WebSocket connection.

        Args:
            websocket: The WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(
            f"WebSocket connected. Total connections: {len(self.active_connections)}"
        )

    def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection.

        Args:
            websocket: The WebSocket connection to remove
        """
        self.active_connections.discard(websocket)
        logger.info(
            f"WebSocket disconnected. Total connections: {len(self.active_connections)}"
        )

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """
        Send a message to a specific WebSocket connection.

        Args:
            message: The message to send
            websocket: The target WebSocket connection
        """
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """
        Broadcast a message to all connected WebSocket clients.

        Args:
            message: The message to broadcast
        """
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_stock_update(self, product_id: str, stock_quantity: int):
        """
        Broadcast a stock level update to all connected POS clients.

        This method is called after any stock-changing operation:
        - Sale confirmation
        - Sale reversal
        - Manual restock
        - Manual adjustment

        Constitution VII (Backend Authority):
        - Only the backend determines stock levels
        - WebSocket is push-only; clients never send stock updates

        Args:
            product_id: UUID of the product with updated stock
            stock_quantity: The new stock level after the change

        Example message:
            {
                "event": "stock_updated",
                "data": {
                    "product_id": "uuid",
                    "stock_quantity": 48
                }
            }
        """
        message = json.dumps(
            {
                "event": "stock_updated",
                "data": {"product_id": product_id, "stock_quantity": stock_quantity},
            }
        )

        await self.broadcast(message)
        logger.info(
            f"Broadcasted stock update for product {product_id}: {stock_quantity}"
        )

    async def broadcast_multiple_stock_updates(self, updates: list[dict]):
        """
        Broadcast multiple stock updates in a single message.

        Useful for operations that affect multiple products simultaneously,
        such as sale confirmations that deduct stock for multiple items.

        Args:
            updates: List of dicts with 'product_id' and 'stock_quantity'

        Example:
            updates = [
                {"product_id": "uuid1", "stock_quantity": 48},
                {"product_id": "uuid2", "stock_quantity": 12}
            ]
        """
        message = json.dumps({"event": "stock_updated_batch", "data": updates})

        await self.broadcast(message)
        logger.info(f"Broadcasted batch stock update for {len(updates)} products")

    def get_connection_count(self) -> int:
        """
        Get the number of active WebSocket connections.

        Returns:
            Number of active connections
        """
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()
