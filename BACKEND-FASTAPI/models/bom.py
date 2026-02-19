"""Bill of Materials ORM model."""

from sqlalchemy import Boolean, Column, Float, Integer, String

from .base import Base


class BillOfMaterials(Base):
    __tablename__ = "bom"

    id = Column(String, primary_key=True)
    parent_sku = Column(String, nullable=False, index=True)
    component_sku = Column(String, nullable=False, index=True)
    quantity_required = Column(Float, nullable=False)
    scrap_factor = Column(Float, default=0.0)
    unit = Column(String)
    level = Column(Integer, default=1)
    is_phantom = Column(Boolean, default=False)

    # Lead times
    lead_time_days = Column(Integer, default=0)
