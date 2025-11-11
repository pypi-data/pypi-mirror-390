"""Unit tests for client module."""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from openf1_mcp.client import fetch_openf1_data, BASE_URL


@pytest.mark.asyncio
async def test_successful_api_response():
    """Test that successful API responses are returned correctly."""
    mock_response_data = [
        {
            "driver_number": 1,
            "full_name": "Max VERSTAPPEN",
            "team_name": "Red Bull Racing"
        },
        {
            "driver_number": 11,
            "full_name": "Sergio PEREZ",
            "team_name": "Red Bull Racing"
        }
    ]
    
    mock_response = Mock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = Mock()
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await fetch_openf1_data("drivers", "driver_number=1")
        
        assert result == mock_response_data
        assert len(result) == 2
        assert result[0]["driver_number"] == 1
        mock_client.get.assert_called_once_with(f"{BASE_URL}/drivers?driver_number=1")


@pytest.mark.asyncio
async def test_successful_api_response_no_query():
    """Test successful API response without query parameters."""
    mock_response_data = [{"session_key": 9158}]
    
    mock_response = Mock()
    mock_response.json.return_value = mock_response_data
    mock_response.raise_for_status = Mock()
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await fetch_openf1_data("sessions")
        
        assert result == mock_response_data
        mock_client.get.assert_called_once_with(f"{BASE_URL}/sessions")


@pytest.mark.asyncio
async def test_http_error_4xx():
    """Test that 4xx HTTP errors are raised correctly."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=mock_response
    )
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await fetch_openf1_data("invalid_endpoint")
        
        assert exc_info.value.response.status_code == 404


@pytest.mark.asyncio
async def test_http_error_5xx():
    """Test that 5xx HTTP errors are raised correctly."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "500 Internal Server Error",
        request=Mock(),
        response=mock_response
    )
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await fetch_openf1_data("drivers")
        
        assert exc_info.value.response.status_code == 500


@pytest.mark.asyncio
async def test_timeout_handling():
    """Test that timeout exceptions are raised correctly."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.TimeoutException("Request timed out"))
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(httpx.TimeoutException) as exc_info:
            await fetch_openf1_data("car_data", "session_key=9158")
        
        assert "timed out" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_connection_error():
    """Test that connection errors are raised correctly."""
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(
            side_effect=httpx.ConnectError("Failed to connect to api.openf1.org")
        )
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        with pytest.raises(httpx.RequestError) as exc_info:
            await fetch_openf1_data("drivers")
        
        assert "connect" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_client_timeout_configuration():
    """Test that AsyncClient is configured with correct timeout."""
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = Mock()
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        await fetch_openf1_data("drivers")
        
        # Verify AsyncClient was called with timeout=30.0
        mock_client_class.assert_called_once_with(timeout=30.0)


@pytest.mark.asyncio
async def test_empty_response():
    """Test that empty API responses are handled correctly."""
    mock_response = Mock()
    mock_response.json.return_value = []
    mock_response.raise_for_status = Mock()
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        result = await fetch_openf1_data("drivers", "driver_number=999")
        
        assert result == []
        assert isinstance(result, list)
