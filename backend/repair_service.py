"""
Service Layer: Business Logic

This layer orchestrates repositories, owns transactions, handles business
rules, processes events_json, and publishes updates to the event bus.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
import uuid

from repo.assignee_repo import AssigneeRepository
from repo.unit_model_repo import UnitModelRepository
from repo.status_repo import StatusRepository
from repo.repair_order_repo import RepairOrderRepository
from repo.repair_unit_repo import RepairUnitRepository
from events import event_bus
from db_models import UnitType


class RepairService:
    """
    Service layer for repair tracker business logic.

    Orchestrates data access layer, manages transactions, and publishes
    events to connected websocket clients.
    """

    def __init__(self, session: Session):
        self.session = session
        self.assignee_repo = AssigneeRepository(session)
        self.unit_model_repo = UnitModelRepository(session)
        self.status_repo = StatusRepository(session)
        self.order_repo = RepairOrderRepository(session)
        self.unit_repo = RepairUnitRepository(session)

    # Assignee methods
    def get_all_assignees(self) -> List[Dict[str, Any]]:
        """Get all assignees."""
        assignees = self.assignee_repo.get_all()
        return [self._serialize_assignee(a) for a in assignees]

    def get_active_assignees(self) -> List[Dict[str, Any]]:
        """Get all active assignees."""
        assignees = self.assignee_repo.get_active()
        return [self._serialize_assignee(a) for a in assignees]

    # Status methods
    def get_all_statuses(self) -> List[Dict[str, Any]]:
        """Get all statuses."""
        statuses = self.status_repo.get_all()
        return [self._serialize_status(s) for s in statuses]

    # Unit model methods
    def get_all_unit_models(self) -> List[Dict[str, Any]]:
        """Get all unit models."""
        models = self.unit_model_repo.get_all()
        return [self._serialize_unit_model(m) for m in models]

    # Repair order methods
    def get_all_orders(self) -> List[Dict[str, Any]]:
        """Get all repair orders with metadata."""
        orders = self.order_repo.get_all(load_relationships=True)
        return [self._serialize_order(o) for o in orders]

    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific repair order with units."""
        order = self.order_repo.get_by_id(
            order_id,
            load_relationships=True
        )
        if not order:
            return None
        return self._serialize_order_with_units(order)

    def create_repair_order(
        self,
        name: str,
        status_id: int,
        summary: Optional[str] = None,
        color: str = '#FFFFFF'
    ) -> Dict[str, Any]:
        """
        Create a new repair order.

        Publishes to 'main' channel after creation.
        """
        order = self.order_repo.create(
            name=name,
            status_id=status_id,
            summary=summary,
            color=color
        )
        self.session.commit()

        # Publish to main channel
        serialized = self._serialize_order(order)
        # Note: publish is async, needs to be awaited in async context
        # This is a placeholder for the pattern

        return serialized

    # Repair unit methods
    def create_repair_unit(
        self,
        repair_order_id: int,
        unit_type: UnitType,
        initial_status_id: int,
        initial_assignee_id: Optional[int],
        serial: Optional[str] = None,
        model_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create a new repair unit with initial status event.

        This creates the origin status event in events_json which cannot
        be deleted. Syncs current_status_id, current_assignee_id, and
        updated_at to match the initial status event.

        Publishes to order channel after creation.
        """
        # Create initial status event
        now = datetime.utcnow()
        initial_event = self._create_status_event(
            status_id=initial_status_id,
            assignee_id=initial_assignee_id,
            timestamp=now
        )

        # Create unit with initial event
        unit = self.unit_repo.create(
            repair_order_id=repair_order_id,
            unit_type=unit_type,
            current_status_id=initial_status_id,
            current_assignee_id=initial_assignee_id,
            serial=serial,
            model_id=model_id,
            events_json=[initial_event]
        )
        unit.updated_at = now

        self.session.commit()

        # Publish to order channel
        # Placeholder for async publish
        return self._serialize_unit(unit)

    def add_status_event(
        self,
        unit_id: int,
        status_id: int,
        assignee_id: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """
        Add a status event to a repair unit.

        Updates current_status_id, current_assignee_id, and updated_at
        to match the new status event. Owns the transaction.

        Publishes to order channel after update.
        """
        unit = self.unit_repo.get_by_id(unit_id)
        if not unit:
            return None

        # Create new status event
        now = datetime.utcnow()
        status_event = self._create_status_event(
            status_id=status_id,
            assignee_id=assignee_id,
            timestamp=now
        )

        # Add event and sync fields
        events = unit.events_json or []
        events.append(status_event)

        self.unit_repo.update(
            unit_id=unit_id,
            events_json=events,
            current_status_id=status_id,
            current_assignee_id=assignee_id,
            updated_at=now
        )

        self.session.commit()

        # Publish to order channel
        # Placeholder for async publish
        return self._serialize_unit(unit)

    # Event creation helpers
    def _create_status_event(
        self,
        status_id: int,
        assignee_id: Optional[int],
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Create a status event dictionary."""
        return {
            'id': str(uuid.uuid4()),
            'type': 'status',
            'assignee': f"AS-{assignee_id}" if assignee_id else None,
            'timestamp': timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
            'status_key': f"ST-{status_id}"
        }

    # Serialization helpers
    def _serialize_assignee(self, assignee) -> Dict[str, Any]:
        """Serialize an Assignee object."""
        return {
            'id': assignee.id,
            'key': f"AS-{assignee.id}",
            'name': assignee.name,
            'is_active': assignee.is_active
        }

    def _serialize_status(self, status) -> Dict[str, Any]:
        """Serialize a Status object."""
        return {
            'id': status.id,
            'key': f"ST-{status.id}",
            'status': status.status,
            'color': status.color,
            'is_ending_status': status.is_ending_status,
            'can_use_for_order': status.can_use_for_order,
            'can_use_for_machine': status.can_use_for_machine,
            'can_use_for_hashboard': status.can_use_for_hashboard
        }

    def _serialize_unit_model(self, model) -> Dict[str, Any]:
        """Serialize a UnitModel object."""
        return {
            'id': model.id,
            'key': f"UM-{model.id}",
            'name': model.name
        }

    def _serialize_order(self, order) -> Dict[str, Any]:
        """Serialize a RepairOrder object (metadata only)."""
        return {
            'id': order.id,
            'key': f"RO-{order.id}",
            'name': order.name,
            'status_id': order.status_id,
            'summary': order.summary,
            'color': order.color,
            'created': order.created.isoformat() if order.created else None,
            'received': order.received.isoformat() if order.received else None,
            'received_quantity': order.received_quantity,
            'started': order.started.isoformat() if order.started else None,
            'finished': order.finished.isoformat() if order.finished else None
        }

    def _serialize_order_with_units(self, order) -> Dict[str, Any]:
        """Serialize a RepairOrder with its units."""
        order_data = self._serialize_order(order)
        order_data['units'] = [
            self._serialize_unit(unit) for unit in order.units
        ]
        return order_data

    def _serialize_unit(self, unit) -> Dict[str, Any]:
        """Serialize a RepairUnit object."""
        return {
            'id': unit.id,
            'key': f"RU-{unit.id}",
            'serial': unit.serial,
            'type': unit.type.value if unit.type else None,
            'model_id': unit.model_id,
            'current_status_id': unit.current_status_id,
            'current_assignee_id': unit.current_assignee_id,
            'repair_order_id': unit.repair_order_id,
            'created': unit.created.isoformat() if unit.created else None,
            'updated_at': (
                unit.updated_at.isoformat() if unit.updated_at else None
            ),
            'events_json': unit.events_json or []
        }
