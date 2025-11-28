"""
Data Access Layer: Status Repository

Handles CRUD operations for the Status model.
Encapsulates all database queries for the statuses table.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from db_models import Status, UnitType


class StatusRepository:
    """Repository for Status data access operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, status_id: int) -> Optional[Status]:
        """
        Retrieve a status by ID.

        Args:
            status_id: Primary key ID

        Returns:
            Status object or None if not found
        """
        return self.session.query(Status).filter(
            Status.id == status_id
        ).first()

    def get_by_name(self, status: str) -> Optional[Status]:
        """
        Retrieve a status by name.

        Args:
            status: Status name

        Returns:
            Status object or None if not found
        """
        return self.session.query(Status).filter(
            Status.status == status
        ).first()

    def get_all(self) -> List[Status]:
        """
        Retrieve all statuses.

        Returns:
            List of all Status objects
        """
        return self.session.query(Status).all()

    def get_for_orders(self) -> List[Status]:
        """
        Retrieve statuses usable for repair orders.

        Returns:
            List of Status objects where can_use_for_order == 1
        """
        return self.session.query(Status).filter(
            Status.can_use_for_order == 1
        ).all()

    def get_for_unit_type(self, unit_type: UnitType) -> List[Status]:
        """
        Retrieve statuses usable for a specific unit type.

        Args:
            unit_type: UnitType enum (MACHINE or HASHBOARD)

        Returns:
            List of applicable Status objects
        """
        if unit_type == UnitType.MACHINE:
            return self.session.query(Status).filter(
                Status.can_use_for_machine == 1
            ).all()
        elif unit_type == UnitType.HASHBOARD:
            return self.session.query(Status).filter(
                Status.can_use_for_hashboard == 1
            ).all()
        return []

    def get_ending_statuses(self) -> List[Status]:
        """
        Retrieve all ending statuses.

        Returns:
            List of Status objects where is_ending_status == 1
        """
        return self.session.query(Status).filter(
            Status.is_ending_status == 1
        ).all()

    def create(
        self,
        status: str,
        color: str = '#bb86fc',
        is_ending_status: int = 0,
        can_use_for_order: int = 1,
        can_use_for_machine: int = 1,
        can_use_for_hashboard: int = 1
    ) -> Status:
        """
        Create a new status.

        Args:
            status: Status name
            color: Hex color code
            is_ending_status: Whether this is an ending status
            can_use_for_order: Can be used for repair orders
            can_use_for_machine: Can be used for machine units
            can_use_for_hashboard: Can be used for hashboard units

        Returns:
            Created Status object
        """
        status_obj = Status(
            status=status,
            color=color,
            is_ending_status=is_ending_status,
            can_use_for_order=can_use_for_order,
            can_use_for_machine=can_use_for_machine,
            can_use_for_hashboard=can_use_for_hashboard
        )
        self.session.add(status_obj)
        return status_obj

    def update(
        self,
        status_id: int,
        status: Optional[str] = None,
        color: Optional[str] = None,
        is_ending_status: Optional[int] = None,
        can_use_for_order: Optional[int] = None,
        can_use_for_machine: Optional[int] = None,
        can_use_for_hashboard: Optional[int] = None
    ) -> Optional[Status]:
        """
        Update an existing status.

        Args:
            status_id: Primary key ID
            status: New status name (optional)
            color: New color (optional)
            is_ending_status: New ending status flag (optional)
            can_use_for_order: New order flag (optional)
            can_use_for_machine: New machine flag (optional)
            can_use_for_hashboard: New hashboard flag (optional)

        Returns:
            Updated Status object or None if not found
        """
        status_obj = self.get_by_id(status_id)
        if not status_obj:
            return None

        if status is not None:
            status_obj.status = status
        if color is not None:
            status_obj.color = color
        if is_ending_status is not None:
            status_obj.is_ending_status = is_ending_status
        if can_use_for_order is not None:
            status_obj.can_use_for_order = can_use_for_order
        if can_use_for_machine is not None:
            status_obj.can_use_for_machine = can_use_for_machine
        if can_use_for_hashboard is not None:
            status_obj.can_use_for_hashboard = can_use_for_hashboard

        return status_obj

    def delete(self, status_id: int) -> bool:
        """
        Delete a status.

        Args:
            status_id: Primary key ID

        Returns:
            True if deleted, False if not found
        """
        status_obj = self.get_by_id(status_id)
        if not status_obj:
            return False

        self.session.delete(status_obj)
        return True
