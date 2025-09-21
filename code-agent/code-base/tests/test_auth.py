"""
Authentication tests
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from main import app
from app.core.database import get_db
from app.models.user import User
from app.core.security import get_password_hash


client = TestClient(app)


@pytest.fixture
def test_user(db: Session):
    """Create test user"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("testpassword"),
        first_name="Test",
        last_name="User"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_register_user(db: Session):
    """Test user registration"""
    response = client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "newpassword123",
        "first_name": "New",
        "last_name": "User"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_duplicate_email(db: Session, test_user):
    """Test registration with duplicate email"""
    response = client.post("/api/v1/auth/register", json={
        "email": "test@example.com",
        "username": "differentuser",
        "password": "password123"
    })
    
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_login_success(db: Session, test_user):
    """Test successful login"""
    response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(db: Session, test_user):
    """Test login with invalid credentials"""
    response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    assert "Incorrect" in response.json()["detail"]


def test_get_current_user(db: Session, test_user):
    """Test getting current user"""
    # First login to get token
    login_response = client.post("/api/v1/auth/login", data={
        "username": "test@example.com",
        "password": "testpassword"
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_get_current_user_invalid_token():
    """Test getting current user with invalid token"""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401
