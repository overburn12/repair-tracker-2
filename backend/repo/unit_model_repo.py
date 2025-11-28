"""
Data Access Layer: Unit Model Repository

Handles CRUD operations for the UnitModel model.
Encapsulates all database queries for the unit_models table.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from db_models import UnitModel


class UnitModelRepository:
    """Repository for UnitModel data access operations."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, model_id: int) -> Optional[UnitModel]:
        """
        Retrieve a unit model by ID.

        Args:
            model_id: Primary key ID

        Returns:
            UnitModel object or None if not found
        """
        return self.session.query(UnitModel).filter(
            UnitModel.id == model_id
        ).first()

    def get_by_name(self, name: str) -> Optional[UnitModel]:
        """
        Retrieve a unit model by name.

        Args:
            name: Model name

        Returns:
            UnitModel object or None if not found
        """
        return self.session.query(UnitModel).filter(
            UnitModel.name == name
        ).first()

    def get_all(self) -> List[UnitModel]:
        """
        Retrieve all unit models.

        Returns:
            List of all UnitModel objects
        """
        return self.session.query(UnitModel).all()

    def create(self, name: str) -> UnitModel:
        """
        Create a new unit model.

        Args:
            name: Model name

        Returns:
            Created UnitModel object
        """
        model = UnitModel(name=name)
        self.session.add(model)
        return model

    def update(self, model_id: int, name: str) -> Optional[UnitModel]:
        """
        Update an existing unit model.

        Args:
            model_id: Primary key ID
            name: New model name

        Returns:
            Updated UnitModel object or None if not found
        """
        model = self.get_by_id(model_id)
        if not model:
            return None

        model.name = name
        return model

    def delete(self, model_id: int) -> bool:
        """
        Delete a unit model.

        Args:
            model_id: Primary key ID

        Returns:
            True if deleted, False if not found
        """
        model = self.get_by_id(model_id)
        if not model:
            return False

        self.session.delete(model)
        return True
