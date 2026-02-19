"""Pydantic schemas for inventory items."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InventoryCreate(BaseModel):
    sku: str = Field(..., description="Stock-keeping unit")
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    quantity_on_hand: int = 0
    reorder_point: int = 0
    min_stock: int = 0
    max_stock: int = 0
    unit_cost: Optional[float] = None
    warehouse_id: Optional[str] = None


class InventoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity_on_hand: Optional[int] = None
    quantity_reserved: Optional[int] = None
    reorder_point: Optional[int] = None
    min_stock: Optional[int] = None
    max_stock: Optional[int] = None
    unit_cost: Optional[float] = None


class InventoryResponse(BaseModel):
    id: str
    sku: str
    name: str
    category: Optional[str]
    unit: Optional[str]
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: Optional[int]
    reorder_point: int
    unit_cost: Optional[float]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
