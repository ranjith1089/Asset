from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from uuid import UUID


class AssetBase(BaseModel):
    asset_tag: str = Field(..., description="Unique asset identifier (e.g., LAP-001)")
    name: str
    category: str = Field(..., description="Asset category (laptop, headphone, etc.)")
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    status: str = Field(default="available", description="available, assigned, maintenance, retired")
    notes: Optional[str] = None


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    asset_tag: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    status: Optional[str] = None
    notes: Optional[str] = None


class Asset(AssetBase):
    id: UUID
    tenant_id: UUID
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

