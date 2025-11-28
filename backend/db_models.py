##
# this database schema is SET IN STONE. DO NOT MODIFY!!!
# there is already production data in the postgres database container with this sqalchemy db schema.
##

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    ForeignKey,
    Enum as SQLEnum,
    func
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from enum import Enum as PyEnum

Base = declarative_base()


class UnitType(str, PyEnum):
    MACHINE = "machine"
    HASHBOARD = "hashboard"


class Assignee(Base):
    __tablename__ = 'assignees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    is_active = Column(Integer, nullable=False, default=1)


class UnitModel(Base):
    __tablename__ = 'unit_models'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, index=True)


class Status(Base):
    __tablename__ = 'statuses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String(50), nullable=False, unique=True, index=True)
    color = Column(String(7), nullable=False, default='#bb86fc')
    is_ending_status = Column(Integer, nullable=False, default=0)
    can_use_for_order = Column(Integer, nullable=False, default=1)
    can_use_for_machine = Column(Integer, nullable=False, default=1)
    can_use_for_hashboard = Column(Integer, nullable=False, default=1)


class RepairOrder(Base):
    __tablename__ = 'repair_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    status_id = Column(Integer, ForeignKey('statuses.id'), nullable=False)
    summary = Column(Text, nullable=True)
    color = Column(String(7), nullable=False, default='#FFFFFF')
    created = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    received = Column(DateTime(timezone=True), nullable=True, index=True)
    received_quantity = Column(Integer, nullable=True)
    started = Column(DateTime(timezone=True), nullable=True, index=True)
    finished = Column(DateTime(timezone=True), nullable=True, index=True)

    units = relationship("RepairUnit", back_populates="order")
    status = relationship("Status", foreign_keys=[status_id])


class RepairUnit(Base):
    __tablename__ = 'repair_units'

    id = Column(Integer, primary_key=True, autoincrement=True)
    serial = Column(String(100), nullable=True)
    created = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    # NOTE: updated_at is manually set to match the timestamp
    # of the most recent status event in events_json
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    type = Column(SQLEnum(UnitType), nullable=False)
    model_id = Column(Integer, ForeignKey('unit_models.id'), nullable=True)
    current_status_id = Column(
        Integer,
        ForeignKey('statuses.id'),
        nullable=False
    )
    current_assignee_id = Column(
        Integer,
        ForeignKey('assignees.id'),
        nullable=True
    )
    repair_order_id = Column(
        Integer,
        ForeignKey('repair_orders.id'),
        nullable=False,
        index=True
    )

    events_json = Column(JSON, nullable=True)

    order = relationship("RepairOrder", back_populates="units")
    model = relationship("UnitModel", foreign_keys=[model_id])
    current_status = relationship("Status", foreign_keys=[current_status_id])
    current_assignee = relationship(
        "Assignee",
        foreign_keys=[current_assignee_id]
    )
