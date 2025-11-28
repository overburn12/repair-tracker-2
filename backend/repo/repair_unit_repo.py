"""
Data Access Layer: Repair Unit Repository

Handles CRUD operations for the RepairUnit model.
Encapsulates all database queries for the repair_units table.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from db_models import RepairUnit, UnitType


class RepairUnitRepository:
    """Repository for RepairUnit data access operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(
        self,
        unit_id: int,
        load_relationships: bool = False
    ) -> Optional[RepairUnit]:
        """
        Retrieve a repair unit by ID.

        Args:
            unit_id: Primary key ID
            load_relationships: Load order, model, status, assignee rels

        Returns:
            RepairUnit object or None if not found
        """
        query = self.session.query(RepairUnit).filter(
            RepairUnit.id == unit_id
        )

        if load_relationships:
            query = query.options(
                joinedload(RepairUnit.order),
                joinedload(RepairUnit.model),
                joinedload(RepairUnit.current_status),
                joinedload(RepairUnit.current_assignee)
            )

        return query.first()

    def get_by_order(
        self,
        order_id: int,
        load_relationships: bool = False
    ) -> List[RepairUnit]:
        """
        Retrieve all units for a repair order.

        Args:
            order_id: Repair order ID
            load_relationships: Load order, model, status, assignee rels

        Returns:
            List of RepairUnit objects
        """
        query = self.session.query(RepairUnit).filter(
            RepairUnit.repair_order_id == order_id
        )

        if load_relationships:
            query = query.options(
                joinedload(RepairUnit.order),
                joinedload(RepairUnit.model),
                joinedload(RepairUnit.current_status),
                joinedload(RepairUnit.current_assignee)
            )

        return query.all()

    def get_by_assignee(
        self,
        assignee_id: int,
        load_relationships: bool = False
    ) -> List[RepairUnit]:
        """
        Retrieve all units assigned to an assignee.

        Args:
            assignee_id: Assignee ID
            load_relationships: Load order, model, status, assignee rels

        Returns:
            List of RepairUnit objects
        """
        query = self.session.query(RepairUnit).filter(
            RepairUnit.current_assignee_id == assignee_id
        )

        if load_relationships:
            query = query.options(
                joinedload(RepairUnit.order),
                joinedload(RepairUnit.model),
                joinedload(RepairUnit.current_status),
                joinedload(RepairUnit.current_assignee)
            )

        return query.all()

    def get_by_status(
        self,
        status_id: int,
        load_relationships: bool = False
    ) -> List[RepairUnit]:
        """
        Retrieve all units with a specific status.

        Args:
            status_id: Status ID
            load_relationships: Load order, model, status, assignee rels

        Returns:
            List of RepairUnit objects
        """
        query = self.session.query(RepairUnit).filter(
            RepairUnit.current_status_id == status_id
        )

        if load_relationships:
            query = query.options(
                joinedload(RepairUnit.order),
                joinedload(RepairUnit.model),
                joinedload(RepairUnit.current_status),
                joinedload(RepairUnit.current_assignee)
            )

        return query.all()

    def create(
        self,
        repair_order_id: int,
        unit_type: UnitType,
        current_status_id: int,
        current_assignee_id: Optional[int] = None,
        serial: Optional[str] = None,
        model_id: Optional[int] = None,
        events_json: Optional[list] = None
    ) -> RepairUnit:
        """
        Create a new repair unit.

        Args:
            repair_order_id: Parent repair order ID
            unit_type: UnitType enum (MACHINE or HASHBOARD)
            current_status_id: Initial status ID
            current_assignee_id: Initial assignee ID (optional)
            serial: Serial number (optional)
            model_id: Unit model ID (optional)
            events_json: Initial events list (optional)

        Returns:
            Created RepairUnit object
        """
        unit = RepairUnit(
            repair_order_id=repair_order_id,
            type=unit_type,
            current_status_id=current_status_id,
            current_assignee_id=current_assignee_id,
            serial=serial,
            model_id=model_id,
            events_json=events_json or []
        )
        self.session.add(unit)
        return unit

    def update(
        self,
        unit_id: int,
        serial: Optional[str] = None,
        model_id: Optional[int] = None,
        current_status_id: Optional[int] = None,
        current_assignee_id: Optional[int] = None,
        updated_at: Optional[datetime] = None,
        events_json: Optional[list] = None
    ) -> Optional[RepairUnit]:
        """
        Update an existing repair unit.

        Args:
            unit_id: Primary key ID
            serial: New serial (optional)
            model_id: New model ID (optional)
            current_status_id: New status ID (optional)
            current_assignee_id: New assignee ID (optional)
            updated_at: New updated timestamp (optional)
            events_json: New events list (optional)

        Returns:
            Updated RepairUnit object or None if not found
        """
        unit = self.get_by_id(unit_id)
        if not unit:
            return None

        if serial is not None:
            unit.serial = serial
        if model_id is not None:
            unit.model_id = model_id
        if current_status_id is not None:
            unit.current_status_id = current_status_id
        if current_assignee_id is not None:
            unit.current_assignee_id = current_assignee_id
        if updated_at is not None:
            unit.updated_at = updated_at
        if events_json is not None:
            unit.events_json = events_json

        return unit

    def delete(self, unit_id: int) -> bool:
        """
        Delete a repair unit.

        Args:
            unit_id: Primary key ID

        Returns:
            True if deleted, False if not found
        """
        unit = self.get_by_id(unit_id)
        if not unit:
            return False

        self.session.delete(unit)
        return True
