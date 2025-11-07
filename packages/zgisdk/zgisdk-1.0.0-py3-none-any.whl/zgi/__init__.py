"""
ZGI - A lightweight utility library for modern Python development
"""

__version__ = "1.0.0"
__author__ = "stark"

from .utils import (
    is_empty,
    deep_clone,
    debounce,
    sleep,
    random_string,
    format_date,
)

from .client import ZGI

__all__ = [
    "is_empty",
    "deep_clone",
    "debounce",
    "sleep",
    "random_string",
    "format_date",
    "ZGI",
]
