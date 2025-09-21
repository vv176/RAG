"""
Order Pydantic schemas
"""

from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, validator
from app.models.order import OrderStatus


class OrderItemBase(BaseModel):
    """Base order item schema"""
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderItemCreate(OrderItemBase):
    """Order item creation schema"""
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be greater than 0')
        return v


class OrderItemResponse(OrderItemBase):
    """Order item response schema"""
    id: int
    order_id: int
    total_price: Decimal
    created_at: str
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order schema"""
    shipping_address: str
    billing_address: Optional[str] = None
    notes: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation schema"""
    items: List[OrderItemCreate]
    
    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must have at least one item')
        return v


class OrderUpdate(BaseModel):
    """Order update schema"""
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None
    billing_address: Optional[str] = None
    notes: Optional[str] = None


class OrderResponse(OrderBase):
    """Order response schema"""
    id: int
    user_id: int
    order_number: str
    status: OrderStatus
    subtotal: Decimal
    tax_amount: Decimal
    shipping_amount: Decimal
    total_amount: Decimal
    item_count: int
    created_at: str
    updated_at: Optional[str] = None
    items: List[OrderItemResponse] = []
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Order list response schema"""
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
