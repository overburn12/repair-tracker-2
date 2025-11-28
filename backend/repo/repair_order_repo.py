"""
Data Access Layer: Repair Order Repository

Handles CRUD operations for the RepairOrder model.
Encapsulates all database queries for the repair_orders table.
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from db_models import RepairOrder


class RepairOrderRepository:
    """Repository for RepairOrder data access operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(
        self,
        order_id: int,
        load_relationships: bool = False
    ) -> Optional[RepairOrder]:
        """
        Retrieve a repair order by ID.

        Args:
            order_id: Primary key ID
            load_relationships: Load units and status relationships

        Returns:
            RepairOrder object or None if not found
        """
        query = self.session.query(RepairOrder).filter(
            RepairOrder.id == order_id
        )

        if load_relationships:
            query = query.options(
                joinedload(RepairOrder.units),
                joinedload(RepairOrder.status)
            )

        return query.first()

    def get_all(self, load_relationships: bool = False) -> List[RepairOrder]:
        """
        Retrieve all repair orders.

        Args:
            load_relationships: Load units and status relationships

        Returns:
            List of all RepairOrder objects
        """
        query = self.session.query(RepairOrder)

        if load_relationships:
            query = query.options(
                joinedload(RepairOrder.units),
                joinedload(RepairOrder.status)
            )

        return query.all()

    def get_by_status(
        self,
        status_id: int,
        load_relationships: bool = False
    ) -> List[RepairOrder]:
        """
        Retrieve repair orders by status.

        Args:
            status_id: Status ID to filter by
            load_relationships: Load units and status relationships

        Returns:
            List of RepairOrder objects
        """
        query = self.session.query(RepairOrder).filter(
            RepairOrder.status_id == status_id
        )

        if load_relationships:
            query = query.options(
                joinedload(RepairOrder.units),
                joinedload(RepairOrder.status)
            )

        return query.all()

    def create(
        self,
        name: str,
        status_id: int,
        summary: Optional[str] = None,
        color: str = '#FFFFFF',
        received: Optional[datetime] = None,
        received_quantity: Optional[int] = None,
        started: Optional[datetime] = None,
        finished: Optional[datetime] = None
    ) -> RepairOrder:
        """
        Create a new repair order.

        Args:
            name: Order name
            status_id: Initial status ID
            summary: Order summary (optional)
            color: Hex color code
            received: Date received (optional)
            received_quantity: Quantity received (optional)
            started: Date started (optional)
            finished: Date finished (optional)

        Returns:
            Created RepairOrder object
        """
        order = RepairOrder(
            name=name,
            status_id=status_id,
            summary=summary,
            color=color,
            received=received,
            received_quantity=received_quantity,
            started=started,
            finished=finished
        )
        self.session.add(order)
        return order

    def update(
        self,
        order_id: int,
        name: Optional[str] = None,
        status_id: Optional[int] = None,
        summary: Optional[str] = None,
        color: Optional[str] = None,
        received: Optional[datetime] = None,
        received_quantity: Optional[int] = None,
        started: Optional[datetime] = None,
        finished: Optional[datetime] = None
    ) -> Optional[RepairOrder]:
        """
        Update an existing repair order.

        Args:
            order_id: Primary key ID
            name: New name (optional)
            status_id: New status ID (optional)
            summary: New summary (optional)
            color: New color (optional)
            received: New received date (optional)
            received_quantity: New received quantity (optional)
            started: New started date (optional)
            finished: New finished date (optional)

        Returns:
            Updated RepairOrder object or None if not found
        """
        order = self.get_by_id(order_id)
        if not order:
            return None

        if name is not None:
            order.name = name
        if status_id is not None:
            order.status_id = status_id
        if summary is not None:
            order.summary = summary
        if color is not None:
            order.color = color
        if received is not None:
            order.received = received
        if received_quantity is not None:
            order.received_quantity = received_quantity
        if started is not None:
            order.started = started
        if finished is not None:
            order.finished = finished

        return order

    def delete(self, order_id: int) -> bool:
        """
        Delete a repair order.

        Args:
            order_id: Primary key ID

        Returns:
            True if deleted, False if not found
        """
        order = self.get_by_id(order_id)
        if not order:
            return False

        self.session.delete(order)
        return True
