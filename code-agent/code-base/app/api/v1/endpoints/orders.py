"""
Order management endpoints
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.security import require_auth
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderListResponse

router = APIRouter()


@router.get("/", response_model=OrderListResponse)
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = Query(None),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_auth)
):
    """Get user's orders"""
    query = db.query(Order).filter(Order.user_id == current_user_id)
    
    # Apply status filter
    if status:
        query = query.filter(Order.status == status)
    
    # Order by creation date (newest first)
    query = query.order_by(desc(Order.created_at))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    orders = query.offset(skip).limit(limit).all()
    
    # Calculate total pages
    total_pages = (total + limit - 1) // limit
    
    return OrderListResponse(
        orders=orders,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        total_pages=total_pages
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_auth)
):
    """Get order by ID"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user_id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_auth)
):
    """Create new order"""
    # Validate products and calculate totals
    total_amount = 0
    order_items = []
    
    for item_data in order_data.items:
        # Get product
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with ID {item_data.product_id} not found"
            )
        
        # Check stock
        if product.stock_quantity < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {product.name}"
            )
        
        # Calculate item total
        item_total = item_data.quantity * item_data.unit_price
        total_amount += item_total
        
        # Create order item
        order_item = OrderItem(
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total_price=item_total
        )
        order_items.append(order_item)
    
    # Generate order number
    import uuid
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    # Create order
    db_order = Order(
        user_id=current_user_id,
        order_number=order_number,
        shipping_address=order_data.shipping_address,
        billing_address=order_data.billing_address,
        notes=order_data.notes,
        subtotal=total_amount,
        tax_amount=0,  # TODO: Calculate tax
        shipping_amount=0,  # TODO: Calculate shipping
        total_amount=total_amount,
        items=order_items
    )
    
    db.add(db_order)
    
    # Update product stock
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock_quantity -= item.quantity
    
    db.commit()
    db.refresh(db_order)
    
    return db_order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_auth)
):
    """Update order (admin only)"""
    # Check if user is admin
    current_user = db.query(User).filter(User.id == current_user_id).first()
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update order fields
    update_data = order_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(require_auth)
):
    """Cancel order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user_id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Only allow cancellation of pending orders
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending orders can be cancelled"
        )
    
    # Update order status
    order.status = OrderStatus.CANCELLED
    
    # Restore product stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock_quantity += item.quantity
    
    db.commit()
    
    return None
