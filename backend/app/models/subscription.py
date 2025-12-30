from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class SubscriptionBase(BaseModel):
    plan: str = Field(..., pattern="^(free|trial|basic|premium|enterprise)$")
    status: str = Field(default="active", pattern="^(active|cancelled|expired)$")
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool = False


class SubscriptionCreate(SubscriptionBase):
    tenant_id: UUID


class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = Field(None, pattern="^(free|trial|basic|premium|enterprise)$")
    status: Optional[str] = Field(None, pattern="^(active|cancelled|expired)$")
    current_period_start: Optional[datetime] = None
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: Optional[bool] = None


class Subscription(SubscriptionBase):
    id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    amount: Decimal
    currency: str = "USD"
    status: str = Field(default="pending", pattern="^(pending|paid|failed)$")
    due_date: Optional[datetime] = None
    invoice_data: Optional[Dict[str, Any]] = Field(default_factory=dict)


class InvoiceCreate(InvoiceBase):
    tenant_id: UUID
    subscription_id: Optional[UUID] = None


class InvoiceUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|paid|failed)$")
    paid_at: Optional[datetime] = None


class Invoice(InvoiceBase):
    id: UUID
    tenant_id: UUID
    subscription_id: Optional[UUID] = None
    paid_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

