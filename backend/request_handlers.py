"""
Request Handlers

Handles incoming update/delete requests from frontend websockets.
Processes requests through the service layer and handles errors.
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from repair_service import RepairService
from events import event_bus
import websocket_handlers


async def handle_update_request(
    message: Dict[str, Any],
    websocket_id: str,
    session: Session
) -> Optional[str]:
    """
    Handle an update request from the frontend.

    Args:
        message: Update message with channel, type, and data
        websocket_id: Websocket ID for error routing
        session: Database session

    Returns:
        Error message string if error occurred, None if successful
    """
    try:
        channel = message.get("channel")
        data_list = message.get("data", [])

        if not channel or not isinstance(data_list, list):
            return "Invalid update message format"

        service = RepairService(session)

        # Handle main:assignee channel
        if channel == event_bus.get_main_assignee_channel():
            for item in data_list:
                if "id" not in item:
                    return "Missing required 'id' field in assignee data"
                parsed = parse_key(item["id"])
                if not parsed or parsed["type"] != "assignee":
                    return f"Invalid assignee key: {item['id']}"

                assignee_id = parsed["id"]
                name = item.get("name")
                is_active = item.get("is_active")

                result = await service.update_assignee(
                    assignee_id=assignee_id,
                    name=name,
                    is_active=is_active
                )
                if not result:
                    return f"Failed to update assignee {item['id']}"

        # Handle main:status channel
        elif channel == event_bus.get_main_status_channel():
            for item in data_list:
                if "id" not in item:
                    return "Missing required 'id' field in status data"
                parsed = parse_key(item["id"])
                if not parsed or parsed["type"] != "status":
                    return f"Invalid status key: {item['id']}"

                status_id = parsed["id"]
                name = item.get("name")
                order = item.get("order")
                color = item.get("color")
                is_ending_status = item.get("is_ending_status")

                result = await service.update_status(
                    status_id=status_id,
                    name=name,
                    order=order,
                    color=color,
                    is_ending_status=is_ending_status
                )
                if not result:
                    return f"Failed to update status {item['id']}"

        # Handle main:unitmodel channel
        elif channel == event_bus.get_main_unitmodel_channel():
            for item in data_list:
                if "id" not in item:
                    return "Missing required 'id' field in unit model data"
                parsed = parse_key(item["id"])
                if not parsed or parsed["type"] != "unit_model":
                    return f"Invalid unit model key: {item['id']}"

                model_id = parsed["id"]
                name = item.get("name")

                result = await service.update_unit_model(
                    model_id=model_id,
                    name=name
                )
                if not result:
                    return f"Failed to update unit model {item['id']}"

        # Handle main:orders channel
        elif channel == event_bus.get_main_orders_channel():
            for item in data_list:
                if "id" not in item:
                    return "Missing required 'id' field in repair order data"
                parsed = parse_key(item["id"])
                if not parsed or parsed["type"] != "repair_order":
                    return f"Invalid repair order key: {item['id']}"

                order_id = parsed["id"]
                # Ignore auto-calculated fields: started, finished, created
                # Ignore relational fields: status, units
                name = item.get("name")
                status_id = item.get("status_id")
                summary = item.get("summary")
                color = item.get("color")
                received = item.get("received")
                received_quantity = item.get("received_quantity")

                result = await service.update_repair_order(
                    order_id=order_id,
                    name=name,
                    status_id=status_id,
                    summary=summary,
                    color=color,
                    received=received,
                    received_quantity=received_quantity
                )
                if not result:
                    return f"Failed to update repair order {item['id']}"

        # Handle order:RO-## channels (repair units)
        elif channel.startswith("order:"):
            for item in data_list:
                if "id" not in item:
                    return "Missing required 'id' field in repair unit data"
                parsed = parse_key(item["id"])
                if not parsed or parsed["type"] != "repair_unit":
                    return f"Invalid repair unit key: {item['id']}"

                unit_id = parsed["id"]
                # Ignore auto-calculated fields: created, updated_at,
                # current_status_id, current_assignee_id
                # Ignore relational fields: order, model, current_status,
                # current_assignee
                # Ignore events_json - use event methods instead
                serial = item.get("serial")
                model_id = item.get("model_id")

                result = await service.update_repair_unit(
                    unit_id=unit_id,
                    serial=serial,
                    model_id=model_id
                )
                if not result:
                    return f"Failed to update repair unit {item['id']}"

        else:
            return f"Unknown channel: {channel}"

        return None  # Success

    except Exception as e:
        return f"Update failed: {str(e)}"


async def handle_delete_request(
    message: Dict[str, Any],
    websocket_id: str,
    session: Session
) -> Optional[str]:
    """
    Handle a delete request from the frontend.

    Args:
        message: Delete message with channel, type, and data (keys)
        websocket_id: Websocket ID for error routing
        session: Database session

    Returns:
        Error message string if error occurred, None if successful
    """
    try:
        channel = message.get("channel")
        keys_list = message.get("data", [])

        if not channel or not isinstance(keys_list, list):
            return "Invalid delete message format"

        service = RepairService(session)

        # Handle main:assignee channel
        if channel == event_bus.get_main_assignee_channel():
            for key in keys_list:
                parsed = parse_key(key)
                if not parsed or parsed["type"] != "assignee":
                    return f"Invalid assignee key: {key}"

                success = await service.delete_assignee(parsed["id"])
                if not success:
                    return f"Failed to delete assignee {key}"

        # Handle main:status channel
        elif channel == event_bus.get_main_status_channel():
            for key in keys_list:
                parsed = parse_key(key)
                if not parsed or parsed["type"] != "status":
                    return f"Invalid status key: {key}"

                success = await service.delete_status(parsed["id"])
                if not success:
                    return f"Failed to delete status {key}"

        # Handle main:unitmodel channel
        elif channel == event_bus.get_main_unitmodel_channel():
            for key in keys_list:
                parsed = parse_key(key)
                if not parsed or parsed["type"] != "unit_model":
                    return f"Invalid unit model key: {key}"

                success = await service.delete_unit_model(parsed["id"])
                if not success:
                    return f"Failed to delete unit model {key}"

        # Handle main:orders channel
        elif channel == event_bus.get_main_orders_channel():
            for key in keys_list:
                parsed = parse_key(key)
                if not parsed or parsed["type"] != "repair_order":
                    return f"Invalid repair order key: {key}"

                success = await service.delete_repair_order(parsed["id"])
                if not success:
                    return f"Failed to delete repair order {key}"

        # Handle order:RO-## channels (repair units)
        elif channel.startswith("order:"):
            for key in keys_list:
                parsed = parse_key(key)
                if not parsed or parsed["type"] != "repair_unit":
                    return f"Invalid repair unit key: {key}"

                success = await service.delete_repair_unit(parsed["id"])
                if not success:
                    return f"Failed to delete repair unit {key}"

        else:
            return f"Unknown channel: {channel}"

        return None  # Success

    except Exception as e:
        return f"Delete failed: {str(e)}"


def parse_key(key: str) -> Optional[Dict[str, Any]]:
    """
    Parse a JIRA-style key into entity type and ID.

    Args:
        key: JIRA-style key (e.g., "RO-123", "RU-456")

    Returns:
        Dict with 'type' and 'id' or None if invalid
    """
    try:
        parts = key.split("-")
        if len(parts) != 2:
            return None

        entity_type = parts[0]
        entity_id = int(parts[1])

        type_map = {
            "AS": "assignee",
            "ST": "status",
            "UM": "unit_model",
            "RO": "repair_order",
            "RU": "repair_unit"
        }

        if entity_type not in type_map:
            return None

        return {
            "type": type_map[entity_type],
            "id": entity_id
        }

    except (ValueError, IndexError):
        return None
