"""
WebSocket Manager

Manages WebSocket connections with unique IDs, channel subscriptions,
and message delivery. Integrates with the event bus to receive updates
and forward them to clients.
"""

from typing import Dict, Set, Any, Optional
from fastapi import WebSocket
import uuid
import asyncio

from events import event_bus


class WebSocketManager:
    """
    Manages WebSocket connections and subscriptions.

    Each WebSocket gets a unique ID for error message routing.
    Subscribes to channels and forwards messages from event bus.
    """

    def __init__(self):
        # Map of websocket -> websocket_id
        self.websocket_ids: Dict[WebSocket, str] = {}
        # Map of websocket -> set of subscribed channels
        self.connections: Dict[WebSocket, Set[str]] = {}
        # Map of websocket -> callback function
        self.callbacks: Dict[WebSocket, Any] = {}
        # Map of websocket_id -> websocket (for error routing)
        self.id_to_websocket: Dict[str, WebSocket] = {}
        self._lock = asyncio.Lock()
        self._messages_subscribed = False

    async def connect(self, websocket: WebSocket) -> str:
        """
        Accept and register a new WebSocket connection.

        Args:
            websocket: FastAPI WebSocket instance

        Returns:
            Unique websocket_id for this connection
        """
        await websocket.accept()

        websocket_id = str(uuid.uuid4())

        async with self._lock:
            self.websocket_ids[websocket] = websocket_id
            self.connections[websocket] = set()
            self.id_to_websocket[websocket_id] = websocket

            # Create persistent callback for this websocket
            callback = self._create_callback(websocket)
            self.callbacks[websocket] = callback

            # Subscribe to __messages__ channel if not already
            if not self._messages_subscribed:
                await event_bus.subscribe(
                    event_bus.get_messages_channel(),
                    self._handle_error_message
                )
                self._messages_subscribed = True

        return websocket_id

    async def disconnect(self, websocket: WebSocket):
        """
        Unregister a WebSocket connection and unsubscribe from channels.

        Args:
            websocket: FastAPI WebSocket instance
        """
        async with self._lock:
            if websocket not in self.connections:
                return

            channels = self.connections[websocket].copy()
            websocket_id = self.websocket_ids.get(websocket)
            callback = self.callbacks.get(websocket)

            # Clean up mappings
            if websocket in self.connections:
                del self.connections[websocket]
            if websocket in self.websocket_ids:
                del self.websocket_ids[websocket]
            if websocket in self.callbacks:
                del self.callbacks[websocket]
            if websocket_id and websocket_id in self.id_to_websocket:
                del self.id_to_websocket[websocket_id]

        # Unsubscribe from all channels
        if callback:
            for channel in channels:
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

            callback = self.callbacks.get(websocket)
            if not callback:
                return

            for channel in channels:
                # Skip __messages__ channel (private)
                if channel == event_bus.get_messages_channel():
                    continue

                if channel not in self.connections[websocket]:
                    self.connections[websocket].add(channel)
                    await event_bus.subscribe(channel, callback)

    async def send_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any]
    ):
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

    def get_websocket_id(self, websocket: WebSocket) -> Optional[str]:
        """
        Get the websocket_id for a given WebSocket.

        Args:
            websocket: FastAPI WebSocket instance

        Returns:
            websocket_id string or None
        """
        return self.websocket_ids.get(websocket)

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

    async def _handle_error_message(self, message: Dict[str, Any]):
        """
        Handle error messages from __messages__ channel.

        Routes error messages to the correct websocket based on
        websocket_id.

        Args:
            message: Error message with websocket_id
        """
        websocket_id = message.get("websocket_id")
        if not websocket_id:
            return

        websocket = self.id_to_websocket.get(websocket_id)
        if websocket:
            await self.send_message(websocket, message)

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
        await event_bus.publish(channel, message)


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
