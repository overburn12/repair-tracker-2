"""
WebSocket Handlers

Handles initial data fetching and formatting for websocket channel
subscriptions. Provides properly formatted messages for each channel type.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from repair_service import RepairService
from events import event_bus


async def get_initial_data_for_channel(
    channel: str,
    session: Session
) -> Optional[Dict[str, Any]]:
    """
    Get initial data for a channel subscription.

    Args:
        channel: Channel name
        session: Database session

    Returns:
        Formatted message dict or None if channel not recognized
    """
    service = RepairService(session)

    if channel == event_bus.get_main_lists_channel():
        return await _get_main_lists_data(service)

    elif channel == event_bus.get_main_orders_channel():
        return await _get_main_orders_data(service)

    elif channel.startswith("order:RO-"):
        # Extract order ID from channel name
        try:
            order_id = int(channel.split("order:RO-")[1])
            return await _get_order_units_data(service, order_id)
        except (ValueError, IndexError):
            return None

    return None


async def _get_main_lists_data(service: RepairService) -> Dict[str, Any]:
    """
    Get main lists data (assignees, statuses, unit models).

    Args:
        service: RepairService instance

    Returns:
        Formatted message dict
    """
    assignees = service.get_all_assignees()
    statuses = service.get_all_statuses()
    models = service.get_all_unit_models()

    # Combine all lists into data array
    data = []
    data.extend(assignees)
    data.extend(statuses)
    data.extend(models)

    return {
        "channel": event_bus.get_main_lists_channel(),
        "type": "update",
        "data": data
    }


async def _get_main_orders_data(service: RepairService) -> Dict[str, Any]:
    """
    Get main orders data (all repair orders metadata).

    Args:
        service: RepairService instance

    Returns:
        Formatted message dict
    """
    orders = service.get_all_orders()

    return {
        "channel": event_bus.get_main_orders_channel(),
        "type": "update",
        "data": orders
    }


async def _get_order_units_data(
    service: RepairService,
    order_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get order units data (all repair units for an order).

    Args:
        service: RepairService instance
        order_id: Repair order ID

    Returns:
        Formatted message dict or None if order not found
    """
    order_data = service.get_order_by_id(order_id)
    if not order_data:
        return None

    units = order_data.get('units', [])

    return {
        "channel": event_bus.get_channel_for_order(order_id),
        "type": "update",
        "data": units
    }


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
