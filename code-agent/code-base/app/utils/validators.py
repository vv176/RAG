"""
Validation utilities
"""

import re
from typing import Optional
from decimal import Decimal


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15


def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"


def validate_sku(sku: str) -> bool:
    """Validate product SKU format"""
    # SKU should be alphanumeric with optional hyphens/underscores
    pattern = r'^[A-Z0-9-_]+$'
    return re.match(pattern, sku) is not None


def validate_price(price: Decimal) -> bool:
    """Validate price value"""
    return price > 0 and price <= Decimal('999999.99')


def validate_stock_quantity(quantity: int) -> bool:
    """Validate stock quantity"""
    return 0 <= quantity <= 999999


def validate_dimensions(dimensions: str) -> bool:
    """Validate product dimensions format (LxWxH)"""
    pattern = r'^\d+(\.\d+)?x\d+(\.\d+)?x\d+(\.\d+)?$'
    return re.match(pattern, dimensions) is not None


def sanitize_string(value: str) -> str:
    """Sanitize string input"""
    # Remove leading/trailing whitespace
    value = value.strip()
    # Replace multiple spaces with single space
    value = re.sub(r'\s+', ' ', value)
    return value


def validate_slug(slug: str) -> bool:
    """Validate URL slug format"""
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return re.match(pattern, slug) is not None


def generate_slug(text: str) -> str:
    """Generate URL slug from text"""
    # Convert to lowercase
    slug = text.lower()
    # Replace spaces and special characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug
