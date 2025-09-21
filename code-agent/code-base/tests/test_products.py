"""
Product tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from main import app
from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.core.security import get_password_hash, create_access_token


client = TestClient(app)


@pytest.fixture
def admin_user(db: Session):
    """Create admin user"""
    user = User(
        email="admin@example.com",
        username="admin",
        hashed_password=get_password_hash("adminpassword"),
        first_name="Admin",
        last_name="User",
        is_admin=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db: Session):
    """Create regular user"""
    user = User(
        email="user@example.com",
        username="user",
        hashed_password=get_password_hash("userpassword"),
        first_name="Regular",
        last_name="User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_category(db: Session):
    """Create test category"""
    category = Category(
        name="Electronics",
        slug="electronics",
        description="Electronic devices and accessories"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def test_product(db: Session, test_category):
    """Create test product"""
    product = Product(
        name="Test Product",
        description="A test product",
        price=Decimal("99.99"),
        sku="TEST-001",
        stock_quantity=10,
        category_id=test_category.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def get_auth_headers(user: User):
    """Get authorization headers for user"""
    token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}


def test_get_products():
    """Test getting products list"""
    response = client.get("/api/v1/products/")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert "total" in data


def test_get_products_with_filters(test_product):
    """Test getting products with filters"""
    response = client.get("/api/v1/products/?search=Test&in_stock_only=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data["products"]) >= 1


def test_get_product_by_id(test_product):
    """Test getting product by ID"""
    response = client.get(f"/api/v1/products/{test_product.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Product"
    assert data["sku"] == "TEST-001"


def test_get_nonexistent_product():
    """Test getting non-existent product"""
    response = client.get("/api/v1/products/99999")
    assert response.status_code == 404


def test_create_product_as_admin(db: Session, admin_user, test_category):
    """Test creating product as admin"""
    product_data = {
        "name": "New Product",
        "description": "A new product",
        "price": 149.99,
        "sku": "NEW-001",
        "stock_quantity": 5,
        "category_id": test_category.id
    }
    
    response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=get_auth_headers(admin_user)
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Product"
    assert data["sku"] == "NEW-001"


def test_create_product_as_regular_user(regular_user):
    """Test creating product as regular user (should fail)"""
    product_data = {
        "name": "New Product",
        "description": "A new product",
        "price": 149.99,
        "sku": "NEW-002",
        "stock_quantity": 5
    }
    
    response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=get_auth_headers(regular_user)
    )
    
    assert response.status_code == 403


def test_create_product_duplicate_sku(db: Session, admin_user, test_product):
    """Test creating product with duplicate SKU"""
    product_data = {
        "name": "Another Product",
        "description": "Another product",
        "price": 199.99,
        "sku": "TEST-001",  # Same SKU as test_product
        "stock_quantity": 3
    }
    
    response = client.post(
        "/api/v1/products/",
        json=product_data,
        headers=get_auth_headers(admin_user)
    )
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_update_product_as_admin(db: Session, admin_user, test_product):
    """Test updating product as admin"""
    update_data = {
        "name": "Updated Product",
        "price": 129.99
    }
    
    response = client.put(
        f"/api/v1/products/{test_product.id}",
        json=update_data,
        headers=get_auth_headers(admin_user)
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Product"
    assert float(data["price"]) == 129.99


def test_delete_product_as_admin(db: Session, admin_user, test_product):
    """Test deleting product as admin"""
    response = client.delete(
        f"/api/v1/products/{test_product.id}",
        headers=get_auth_headers(admin_user)
    )
    
    assert response.status_code == 204
    
    # Verify product is deleted
    get_response = client.get(f"/api/v1/products/{test_product.id}")
    assert get_response.status_code == 404
