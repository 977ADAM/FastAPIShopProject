from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OrderItemCreate(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity (must be > 0)")


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=2, max_length=200)
    customer_email: EmailStr = Field(..., max_length=320)
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    price: float
    quantity: int

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_email: str
    total: float
    status: str
    created_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="New order status")
