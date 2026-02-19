"""
Input validators

Reusable validation helpers used across routers and services.
"""

import re


def is_valid_uuid(value: str) -> bool:
    """Return True if *value* is a valid UUID (any version)."""
    pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        re.IGNORECASE,
    )
    return bool(pattern.match(value))


def sanitize_string(value: str, max_length: int = 1024) -> str:
    """Strip leading/trailing whitespace and truncate to *max_length*."""
    return value.strip()[:max_length]


def is_valid_email(value: str) -> bool:
    """Basic email format check."""
    pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    return bool(pattern.match(value))
