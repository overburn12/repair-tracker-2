"""
Message Formatters

Simple formatting functions for WebSocket messages.
Separated from websocket_handlers to avoid circular imports.
"""

from typing import Dict, Any, List

from events import event_bus


def format_update_message(
    channel: str,
    data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Format an update message for a channel.

    Args:
        channel: Channel name
        data: List of data objects with 'key' fields

    Returns:
        Formatted message dict
    """
    return {
        "channel": channel,
        "type": "update",
        "data": data
    }


def format_delete_message(
    channel: str,
    keys: List[str]
) -> Dict[str, Any]:
    """
    Format a delete message for a channel.

    Args:
        channel: Channel name
        keys: List of JIRA-style keys to delete

    Returns:
        Formatted message dict
    """
    return {
        "channel": channel,
        "type": "delete",
        "data": keys
    }


def format_error_message(
    websocket_id: str,
    message: str
) -> Dict[str, Any]:
    """
    Format an error message for __messages__ channel.

    Args:
        websocket_id: Target websocket ID
        message: Error message text

    Returns:
        Formatted error message dict
    """
    return {
        "channel": event_bus.get_messages_channel(),
        "websocket_id": websocket_id,
        "type": "error",
        "message": message
    }
