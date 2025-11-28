"""
WebSocket Manager

Manages WebSocket connections, channel subscriptions, and message delivery.
Integrates with the event bus to receive updates and forward them to clients.
"""

from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio

from events import event_bus


class WebSocketManager:
    """
    Manages WebSocket connections and subscriptions.

    Each WebSocket can subscribe to multiple channels. When messages are
    published to a channel via the event bus, they are forwarded to all
    subscribed WebSocket connections.
    """

    def __init__(self):
        # Map of websocket -> set of subscribed channels
        self.connections: Dict[WebSocket, Set[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance
        """
        await websocket.accept()
        async with self._lock:
            self.connections[websocket] = set()

    async def disconnect(self, websocket: WebSocket):
        """
        Unregister a WebSocket connection and unsubscribe from channels.

        Args:
            websocket: FastAPI WebSocket instance
        """
        async with self._lock:
            if websocket in self.connections:
                channels = self.connections[websocket]
                del self.connections[websocket]

        # Unsubscribe from all channels
        for channel in channels:
            callback = self._create_callback(websocket)
            await event_bus.unsubscribe(channel, callback)

    async def subscribe_to_channels(
        self,
        websocket: WebSocket,
        channels: list
    ):
        """
        Subscribe a WebSocket to multiple channels.

        Args:
            websocket: FastAPI WebSocket instance
            channels: List of channel names to subscribe to
        """
        async with self._lock:
            if websocket not in self.connections:
                return

            for channel in channels:
                self.connections[websocket].add(channel)
                callback = self._create_callback(websocket)
                await event_bus.subscribe(channel, callback)

    async def send_message(self, websocket: WebSocket, message: Dict[str, Any]):
        """
        Send a message to a specific WebSocket.

        Args:
            websocket: FastAPI WebSocket instance
            message: Message data to send
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending message to websocket: {e}")
            await self.disconnect(websocket)

    def _create_callback(self, websocket: WebSocket):
        """
        Create a callback function for event bus subscriptions.

        Args:
            websocket: FastAPI WebSocket instance

        Returns:
            Async callback function
        """
        async def callback(message: Any):
            await self.send_message(websocket, message)
        return callback

    async def broadcast_to_channel(
        self,
        channel: str,
        message: Dict[str, Any]
    ):
        """
        Broadcast a message to all WebSockets subscribed to a channel.

        Args:
            channel: Channel name
            message: Message data to broadcast
        """
        # This method can be used for direct broadcasting if needed,
        # but typically the event bus handles this
        await event_bus.publish(channel, message)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
