"""
Helper utility functions
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from decimal import Decimal


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())


def generate_short_id(length: int = 8) -> str:
    """Generate a short random ID"""
    return uuid.uuid4().hex[:length].upper()


def generate_hash(data: str) -> str:
    """Generate SHA-256 hash of data"""
    return hashlib.sha256(data.encode()).hexdigest()


def format_currency(amount: Decimal, currency: str = "USD") -> str:
    """Format currency amount"""
    return f"${amount:.2f} {currency}"


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object"""
    return dt.strftime(format_str)


def parse_datetime(date_string: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse datetime string"""
    try:
        return datetime.strptime(date_string, format_str)
    except ValueError:
        return None


def calculate_tax(amount: Decimal, tax_rate: float = 0.08) -> Decimal:
    """Calculate tax amount"""
    return amount * Decimal(str(tax_rate))


def calculate_shipping(weight: Decimal, base_rate: Decimal = Decimal('5.00')) -> Decimal:
    """Calculate shipping cost based on weight"""
    if weight <= Decimal('1.0'):
        return base_rate
    elif weight <= Decimal('5.0'):
        return base_rate + Decimal('2.00')
    else:
        return base_rate + Decimal('5.00')


def paginate_results(
    items: List[Any],
    page: int = 1,
    page_size: int = 20
) -> Dict[str, Any]:
    """Paginate a list of items"""
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    
    paginated_items = items[start:end]
    total_pages = (total + page_size - 1) // page_size
    
    return {
        "items": paginated_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def filter_dict(data: Dict[str, Any], allowed_keys: List[str]) -> Dict[str, Any]:
    """Filter dictionary to only include allowed keys"""
    return {key: value for key, value in data.items() if key in allowed_keys}


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        result.update(d)
    return result


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split list into chunks of specified size"""
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def remove_duplicates(items: List[Any]) -> List[Any]:
    """Remove duplicates from list while preserving order"""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def safe_divide(numerator: Decimal, denominator: Decimal) -> Decimal:
    """Safely divide two decimals, returning 0 if denominator is 0"""
    if denominator == 0:
        return Decimal('0')
    return numerator / denominator


def round_to_cents(amount: Decimal) -> Decimal:
    """Round amount to 2 decimal places (cents)"""
    return amount.quantize(Decimal('0.01'))


def is_valid_date_range(start_date: datetime, end_date: datetime) -> bool:
    """Check if date range is valid (start < end)"""
    return start_date < end_date


def get_date_range_days(start_date: datetime, end_date: datetime) -> int:
    """Get number of days between two dates"""
    return (end_date - start_date).days


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate string to maximum length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
