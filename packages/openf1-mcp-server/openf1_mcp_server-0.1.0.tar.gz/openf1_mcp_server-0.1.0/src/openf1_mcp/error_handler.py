"""Error handling utilities for OpenF1 API requests."""

import httpx
from typing import Any, Union
from .client import fetch_openf1_data


async def safe_fetch(
    endpoint: str,
    query_string: str = ""
) -> Union[list[dict[str, Any]], dict[str, str]]:
    """
    Safely fetch data from OpenF1 API with comprehensive error handling.
    
    Wraps fetch_openf1_data() and catches all possible exceptions,
    returning either the successful data or a consistent error dict.
    
    Args:
        endpoint: API endpoint (e.g., "car_data", "drivers")
        query_string: Pre-built query string with parameters
    
    Returns:
        On success: List of data records from the API
        On failure: Dict with "error" and "message" keys
    
    Examples:
        Success: [{"driver_number": 1, "name": "Max Verstappen"}]
        Error: {"error": "API error: 404", "message": "Not Found"}
    """
    try:
        return await fetch_openf1_data(endpoint, query_string)
    
    except httpx.HTTPStatusError as e:
        # API returned an error status code (4xx, 5xx)
        return {
            "error": f"API error: {e.response.status_code}",
            "message": e.response.text
        }
    
    except httpx.TimeoutException:
        # Request timed out (exceeded 30 second timeout)
        return {
            "error": "Request timeout",
            "message": "The OpenF1 API did not respond in time"
        }
    
    except httpx.RequestError as e:
        # Connection error (network failure, DNS resolution, etc.)
        return {
            "error": "Connection error",
            "message": str(e)
        }
    
    except Exception as e:
        # Catch any unexpected errors
        return {
            "error": "Unexpected error",
            "message": str(e)
        }
