"""
WebSocket Handlers

Handles initial data fetching and formatting for websocket channel
subscriptions. Provides properly formatted messages for each channel type.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from repair_service import RepairService
from events import event_bus
from message_formatters import (
    format_update_message,
    format_delete_message,
    format_error_message
)


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

    if channel == event_bus.get_main_assignee_channel():
        return await _get_main_assignee_data(service)

    elif channel == event_bus.get_main_status_channel():
        return await _get_main_status_data(service)

    elif channel == event_bus.get_main_unitmodel_channel():
        return await _get_main_unitmodel_data(service)

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


async def _get_main_assignee_data(service: RepairService) -> Dict[str, Any]:
    """
    Get main assignee data.

    Args:
        service: RepairService instance

    Returns:
        Formatted message dict
    """
    assignees = service.get_all_assignees()

    return {
        "channel": event_bus.get_main_assignee_channel(),
        "type": "update",
        "data": assignees
    }


async def _get_main_status_data(service: RepairService) -> Dict[str, Any]:
    """
    Get main status data.

    Args:
        service: RepairService instance

    Returns:
        Formatted message dict
    """
    statuses = service.get_all_statuses()

    return {
        "channel": event_bus.get_main_status_channel(),
        "type": "update",
        "data": statuses
    }


async def _get_main_unitmodel_data(service: RepairService) -> Dict[str, Any]:
    """
    Get main unit model data.

    Args:
        service: RepairService instance

    Returns:
        Formatted message dict
    """
    models = service.get_all_unit_models()

    return {
        "channel": event_bus.get_main_unitmodel_channel(),
        "type": "update",
        "data": models
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
