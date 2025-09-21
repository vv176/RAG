"""
Product Pydantic schemas
"""

from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, validator


class ProductImageBase(BaseModel):
    """Base product image schema"""
    image_url: str
    alt_text: Optional[str] = None
    is_primary: bool = False
    sort_order: int = 0


class ProductImageCreate(ProductImageBase):
    """Product image creation schema"""
    pass


class ProductImageResponse(ProductImageBase):
    """Product image response schema"""
    id: int
    product_id: int
    created_at: str
    
    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Base product schema"""
    name: str
    description: Optional[str] = None
    price: Decimal
    sku: str
    stock_quantity: int = 0
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    """Product creation schema"""
    
    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be greater than 0')
        return v
    
    @validator('stock_quantity')
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('Stock quantity cannot be negative')
        return v


class ProductUpdate(BaseModel):
    """Product update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    is_active: Optional[bool] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[str] = None
    category_id: Optional[int] = None


class ProductResponse(ProductBase):
    """Product response schema"""
    id: int
    is_active: bool
    is_in_stock: bool
    created_at: str
    updated_at: Optional[str] = None
    images: List[ProductImageResponse] = []
    
    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Product list response schema"""
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
