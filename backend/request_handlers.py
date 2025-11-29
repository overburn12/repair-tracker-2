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

        # TODO: Implement update handling based on channel and data
        # This will parse the data, determine entity type from keys,
        # and call appropriate service methods

        # For now, return not implemented
        return "Update handling not yet fully implemented"

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

        # TODO: Implement delete handling based on channel and keys
        # This will parse the keys, determine entity type,
        # and call appropriate service methods

        # For now, return not implemented
        return "Delete handling not yet fully implemented"

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
