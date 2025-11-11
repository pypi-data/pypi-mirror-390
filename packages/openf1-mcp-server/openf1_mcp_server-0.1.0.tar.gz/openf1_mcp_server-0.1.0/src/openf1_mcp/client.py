"""HTTP client for OpenF1 API."""

import httpx
from typing import Any

BASE_URL = "https://api.openf1.org/v1"


async def fetch_openf1_data(
    endpoint: str,
    query_string: str = ""
) -> list[dict[str, Any]]:
    """
    Fetch data from OpenF1 API.
    
    Args:
        endpoint: API endpoint (e.g., "car_data", "drivers")
        query_string: Pre-built query string with parameters
    
    Returns:
        List of data records from the API
    
    Raises:
        httpx.HTTPStatusError: If API returns error status (4xx, 5xx)
        httpx.TimeoutException: If request times out
        httpx.RequestError: If connection fails
    """
    url = f"{BASE_URL}/{endpoint}"
    if query_string:
        url += f"?{query_string}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
