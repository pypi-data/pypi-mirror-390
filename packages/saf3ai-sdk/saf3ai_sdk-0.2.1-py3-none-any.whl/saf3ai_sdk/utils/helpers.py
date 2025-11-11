"""Helper utility functions for Saf3AI SDK."""

import time
from typing import Any, Dict, Union


def get_timestamp() -> int:
    """Get current timestamp in nanoseconds."""
    return int(time.time() * 1_000_000_000)


def format_duration(nanoseconds: int) -> str:
    """Format duration from nanoseconds to human readable string."""
    if nanoseconds < 1_000:
        return f"{nanoseconds}ns"
    elif nanoseconds < 1_000_000:
        return f"{nanoseconds / 1_000:.2f}μs"
    elif nanoseconds < 1_000_000_000:
        return f"{nanoseconds / 1_000_000:.2f}ms"
    else:
        return f"{nanoseconds / 1_000_000_000:.2f}s"


def sanitize_attributes(attributes: Dict[str, Any]) -> Dict[str, Union[str, int, float, bool]]:
    """
    Sanitize attributes to ensure they are compatible with OpenTelemetry.
    
    Args:
        attributes: Dictionary of attributes to sanitize
        
    Returns:
        Sanitized dictionary with only compatible types
    """
    sanitized = {}
    
    for key, value in attributes.items():
        if isinstance(value, (str, int, float, bool)):
            sanitized[key] = value
        elif value is None:
            continue  # Skip None values
        else:
            # Convert other types to string
            sanitized[key] = str(value)
    
    return sanitized
