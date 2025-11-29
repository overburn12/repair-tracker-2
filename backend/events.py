"""
Event Bus: In-memory Pub/Sub System

Custom event bus to handle publish/subscribe messaging without Redis.
Supports multiple channel types for different data flows.

Channels:
- 'main:lists': Assignees, statuses, and unit models
- 'main:orders': All repair order metadata
- 'order:RO-##': Updates for specific repair order and its units (JIRA key)
- '__messages__': Private channel for error messages (websocket_id routing)
"""

from typing import Dict, Set, Callable, Any
import asyncio


class EventBus:
    """
    Simple in-memory pub/sub event bus.

    Manages subscriptions and broadcasts messages to subscribers.
    """

    def __init__(self):
        self.subscribers: Dict[str, Set[Callable]] = {}
        self._lock = asyncio.Lock()

    async def subscribe(self, channel: str, callback: Callable):
        """
        Subscribe a callback to a channel.

        Args:
            channel: Channel name to subscribe to
            callback: Async function to call when messages published
        """
        async with self._lock:
            if channel not in self.subscribers:
                self.subscribers[channel] = set()
            self.subscribers[channel].add(callback)

    async def unsubscribe(self, channel: str, callback: Callable):
        """
        Unsubscribe a callback from a channel.

        Args:
            channel: Channel name to unsubscribe from
            callback: The callback function to remove
        """
        async with self._lock:
            if channel in self.subscribers:
                self.subscribers[channel].discard(callback)
                if not self.subscribers[channel]:
                    del self.subscribers[channel]

    async def publish(self, channel: str, message: Any):
        """
        Publish a message to all subscribers of a channel.

        Args:
            channel: Channel name to publish to
            message: Message data to send (typically a dict)
        """
        async with self._lock:
            if channel in self.subscribers:
                callbacks = self.subscribers[channel].copy()

        # Call callbacks outside the lock to avoid blocking
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
            except Exception as e:
                # Log error but don't stop other callbacks
                print(f"Error in event bus callback: {e}")

    def get_channel_for_order(self, order_id: int) -> str:
        """
        Get the channel name for a specific repair order.

        Args:
            order_id: Repair order ID

        Returns:
            Channel name string (e.g., "order:RO-123")
        """
        return f"order:RO-{order_id}"

    @staticmethod
    def get_main_lists_channel() -> str:
        """
        Get the channel name for main lists data.

        Returns:
            Channel name string
        """
        return "main:lists"

    @staticmethod
    def get_main_orders_channel() -> str:
        """
        Get the channel name for main orders data.

        Returns:
            Channel name string
        """
        return "main:orders"

    @staticmethod
    def get_messages_channel() -> str:
        """
        Get the private messages channel for error routing.

        Returns:
            Channel name string
        """
        return "__messages__"


# Global event bus instance
event_bus = EventBus()
