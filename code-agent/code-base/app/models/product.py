"""
Product model and related schemas
"""

from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Product(Base):
    """Product model"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    sku = Column(String(100), unique=True, index=True, nullable=False)
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    weight = Column(Numeric(8, 2), nullable=True)
    dimensions = Column(String(100), nullable=True)  # "LxWxH"
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="products")
    images = relationship("ProductImage", back_populates="product", cascade="all, delete-orphan")
    order_items = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}')>"
    
    @property
    def is_in_stock(self) -> bool:
        """Check if product is in stock"""
        return self.stock_quantity > 0
    
    def to_dict(self) -> dict:
        """Convert product to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price else None,
            "sku": self.sku,
            "stock_quantity": self.stock_quantity,
            "is_active": self.is_active,
            "is_in_stock": self.is_in_stock,
            "weight": float(self.weight) if self.weight else None,
            "dimensions": self.dimensions,
            "category_id": self.category_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class ProductImage(Base):
    """Product image model"""
    __tablename__ = "product_images"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    image_url = Column(String(500), nullable=False)
    alt_text = Column(String(255), nullable=True)
    is_primary = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product", back_populates="images")
    
    def __repr__(self):
        return f"<ProductImage(id={self.id}, product_id={self.product_id}, url='{self.image_url}')>"
    
    def to_dict(self) -> dict:
        """Convert product image to dictionary"""
        return {
            "id": self.id,
            "product_id": self.product_id,
            "image_url": self.image_url,
            "alt_text": self.alt_text,
            "is_primary": self.is_primary,
            "sort_order": self.sort_order,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
