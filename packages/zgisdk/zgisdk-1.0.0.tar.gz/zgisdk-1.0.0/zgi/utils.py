"""
Utility functions for ZGI library
"""

import copy
import time
import random
import string
from datetime import datetime
from typing import Any, Callable, TypeVar
from functools import wraps

T = TypeVar('T')


def is_empty(value: Any) -> bool:
    """
    Check if a value is empty (None, empty string, empty list, or empty dict)
    
    Args:
        value: The value to check
        
    Returns:
        True if the value is empty, False otherwise
    """
    if value is None:
        return True
    if isinstance(value, str):
        return len(value.strip()) == 0
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0
    return False


def deep_clone(obj: T) -> T:
    """
    Create a deep copy of an object
    
    Args:
        obj: The object to clone
        
    Returns:
        A deep copy of the object
    """
    return copy.deepcopy(obj)


def debounce(wait: float = 0.3):
    """
    Decorator to debounce a function
    
    Args:
        wait: The delay in seconds
        
    Returns:
        The debounced function decorator
    """
    def decorator(func: Callable) -> Callable:
        last_call = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - last_call[0] >= wait:
                last_call[0] = current_time
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def sleep(seconds: float) -> None:
    """
    Sleep for a specified duration
    
    Args:
        seconds: The duration in seconds
    """
    time.sleep(seconds)


def random_string(length: int = 10) -> str:
    """
    Generate a random alphanumeric string
    
    Args:
        length: The length of the string (default: 10)
        
    Returns:
        A random string
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def format_date(date: datetime = None, fmt: str = "%Y-%m-%d") -> str:
    """
    Format a date to a string
    
    Args:
        date: The date to format (default: current date)
        fmt: The format string (default: "%Y-%m-%d")
        
    Returns:
        The formatted date string
    """
    if date is None:
        date = datetime.now()
    return date.strftime(fmt)
