"""
Category Pydantic schemas
"""

from typing import Optional
from pydantic import BaseModel, validator


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    """Category creation schema"""
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 2:
            raise ValueError('Category name must be at least 2 characters long')
        return v
    
    @validator('slug')
    def validate_slug(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must contain only alphanumeric characters, hyphens, and underscores')
        return v


class CategoryUpdate(BaseModel):
    """Category update schema"""
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    """Category response schema"""
    id: int
    is_active: bool
    product_count: int
    created_at: str
    updated_at: Optional[str] = None
    
    class Config:
        from_attributes = True
