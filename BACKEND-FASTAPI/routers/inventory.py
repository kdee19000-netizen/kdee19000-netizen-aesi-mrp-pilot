"""Inventory management router."""

import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from dependencies import get_db
from models.inventory import Inventory
from schemas.inventory import InventoryCreate, InventoryResponse, InventoryUpdate

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


@router.get("/", response_model=List[InventoryResponse])
def list_inventory(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Return a paginated list of inventory items."""
    return db.query(Inventory).offset(skip).limit(limit).all()


@router.post("/", response_model=InventoryResponse, status_code=201)
def create_inventory_item(item: InventoryCreate, db: Session = Depends(get_db)):
    """Create a new inventory item."""
    existing = db.query(Inventory).filter(Inventory.sku == item.sku).first()
    if existing:
        raise HTTPException(status_code=409, detail="SKU already exists")

    db_item = Inventory(
        id=str(uuid.uuid4()),
        **item.model_dump(),
        quantity_available=item.quantity_on_hand,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=InventoryResponse)
def get_inventory_item(item_id: str, db: Session = Depends(get_db)):
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=InventoryResponse)
def update_inventory_item(
    item_id: str, update: InventoryUpdate, db: Session = Depends(get_db)
):
    item = db.query(Inventory).filter(Inventory.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    item.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item
