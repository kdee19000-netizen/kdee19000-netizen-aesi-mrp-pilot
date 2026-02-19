"""Inventory ORM model."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(String, primary_key=True)
    sku = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    unit = Column(String)
    quantity_on_hand = Column(Integer, default=0)
    quantity_reserved = Column(Integer, default=0)
    quantity_available = Column(Integer)
    reorder_point = Column(Integer, default=0)
    min_stock = Column(Integer, default=0)
    max_stock = Column(Integer, default=0)
    unit_cost = Column(Float)
    warehouse_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
