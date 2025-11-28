"""
Data Access Layer: Assignee Repository

Handles CRUD operations for the Assignee (employee/repair tech) model.
Encapsulates all database queries for the assignees table.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from db_models import Assignee


class AssigneeRepository:
    """Repository for Assignee data access operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, assignee_id: int) -> Optional[Assignee]:
        """
        Retrieve an assignee by ID.

        Args:
            assignee_id: Primary key ID

        Returns:
            Assignee object or None if not found
        """
        return self.session.query(Assignee).filter(
            Assignee.id == assignee_id
        ).first()

    def get_by_name(self, name: str) -> Optional[Assignee]:
        """
        Retrieve an assignee by name.

        Args:
            name: Assignee name

        Returns:
            Assignee object or None if not found
        """
        return self.session.query(Assignee).filter(
            Assignee.name == name
        ).first()

    def get_all(self) -> List[Assignee]:
        """
        Retrieve all assignees.

        Returns:
            List of all Assignee objects
        """
        return self.session.query(Assignee).all()

    def get_active(self) -> List[Assignee]:
        """
        Retrieve all active assignees.

        Returns:
            List of active Assignee objects
        """
        return self.session.query(Assignee).filter(
            Assignee.is_active == 1
        ).all()

    def create(self, name: str, is_active: int = 1) -> Assignee:
        """
        Create a new assignee.

        Args:
            name: Assignee name
            is_active: Active status (0=inactive, 1=active)

        Returns:
            Created Assignee object
        """
        assignee = Assignee(name=name, is_active=is_active)
        self.session.add(assignee)
        return assignee

    def update(
        self,
        assignee_id: int,
        name: Optional[str] = None,
        is_active: Optional[int] = None
    ) -> Optional[Assignee]:
        """
        Update an existing assignee.

        Args:
            assignee_id: Primary key ID
            name: New name (optional)
            is_active: New active status (optional)

        Returns:
            Updated Assignee object or None if not found
        """
        assignee = self.get_by_id(assignee_id)
        if not assignee:
            return None

        if name is not None:
            assignee.name = name
        if is_active is not None:
            assignee.is_active = is_active

        return assignee

    def delete(self, assignee_id: int) -> bool:
        """
        Delete an assignee.

        Args:
            assignee_id: Primary key ID

        Returns:
            True if deleted, False if not found
        """
        assignee = self.get_by_id(assignee_id)
        if not assignee:
            return False

        self.session.delete(assignee)
        return True
