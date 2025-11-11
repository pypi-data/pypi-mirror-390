"""Query builder for OpenF1 API query string construction."""

from typing import Any
from urllib.parse import quote


def build_query_params(params: dict[str, Any]) -> str:
    """
    Build query string from parameters for OpenF1 API.
    
    Handles parameter patterns:
    - min/max patterns: {field}_min -> {field}>={value}, {field}_max -> {field}<={value}
    - start/end patterns: {field}_start -> {field}>={value}, {field}_end -> {field}<{value}
    - exact matches: {field} -> {field}={value}
    - None values are skipped
    - Special characters in values are URL-encoded
    
    Args:
        params: Dictionary of parameter names and values
    
    Returns:
        URL-encoded query string (without leading '?')
    
    Example:
        >>> build_query_params({"speed_min": 300, "speed_max": 350, "driver_number": 1})
        'speed>=300&speed<=350&driver_number=1'
        
        >>> build_query_params({"date_start": "2024-01-01", "date_end": "2024-12-31"})
        'date>=2024-01-01&date<2024-12-31'
        
        >>> build_query_params({"driver_number": None, "session_key": 123})
        'session_key=123'
    """
    query_parts = []
    
    for key, value in params.items():
        # Skip None values
        if value is None:
            continue
        
        # Convert value to string for URL encoding
        value_str = str(value)
        
        # Handle min/max patterns
        if key.endswith('_min'):
            field = key[:-4]  # Remove '_min' suffix
            encoded_value = quote(value_str, safe='')
            query_parts.append(f"{field}>={encoded_value}")
        elif key.endswith('_max'):
            field = key[:-4]  # Remove '_max' suffix
            encoded_value = quote(value_str, safe='')
            query_parts.append(f"{field}<={encoded_value}")
        # Handle start/end patterns
        elif key.endswith('_start'):
            field = key[:-6]  # Remove '_start' suffix
            encoded_value = quote(value_str, safe='')
            query_parts.append(f"{field}>={encoded_value}")
        elif key.endswith('_end'):
            field = key[:-4]  # Remove '_end' suffix
            encoded_value = quote(value_str, safe='')
            query_parts.append(f"{field}<{encoded_value}")
        # Handle exact match
        else:
            encoded_value = quote(value_str, safe='')
            query_parts.append(f"{key}={encoded_value}")
    
    return "&".join(query_parts)
