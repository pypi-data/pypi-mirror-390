"""Unit tests for error handler module."""

import pytest
import httpx
from unittest.mock import AsyncMock, Mock, patch
from openf1_mcp.error_handler import safe_fetch


@pytest.mark.asyncio
async def test_successful_fetch():
    """Test that successful fetches return data correctly."""
    mock_data = [
        {"driver_number": 1, "full_name": "Max VERSTAPPEN"},
        {"driver_number": 11, "full_name": "Sergio PEREZ"}
    ]
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await safe_fetch("drivers", "driver_number=1")
        
        assert result == mock_data
        assert isinstance(result, list)
        mock_fetch.assert_called_once_with("drivers", "driver_number=1")


@pytest.mark.asyncio
async def test_http_status_error_404():
    """Test HTTPStatusError handling for 404 errors."""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_response.text = "Not Found"
    
    http_error = httpx.HTTPStatusError(
        "404 Not Found",
        request=Mock(),
        response=mock_response
    )
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = http_error
        
        result = await safe_fetch("invalid_endpoint")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "message" in result
        assert result["error"] == "API error: 404"
        assert result["message"] == "Not Found"


@pytest.mark.asyncio
async def test_http_status_error_500():
    """Test HTTPStatusError handling for 500 errors."""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    
    http_error = httpx.HTTPStatusError(
        "500 Internal Server Error",
        request=Mock(),
        response=mock_response
    )
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = http_error
        
        result = await safe_fetch("drivers")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "message" in result
        assert result["error"] == "API error: 500"
        assert result["message"] == "Internal Server Error"


@pytest.mark.asyncio
async def test_http_status_error_429():
    """Test HTTPStatusError handling for rate limit errors."""
    mock_response = Mock()
    mock_response.status_code = 429
    mock_response.text = "Rate limit exceeded"
    
    http_error = httpx.HTTPStatusError(
        "429 Too Many Requests",
        request=Mock(),
        response=mock_response
    )
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = http_error
        
        result = await safe_fetch("car_data", "session_key=9158")
        
        assert isinstance(result, dict)
        assert result["error"] == "API error: 429"
        assert result["message"] == "Rate limit exceeded"


@pytest.mark.asyncio
async def test_timeout_exception():
    """Test TimeoutException handling."""
    timeout_error = httpx.TimeoutException("Request timed out")
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = timeout_error
        
        result = await safe_fetch("car_data", "session_key=9158")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "message" in result
        assert result["error"] == "Request timeout"
        assert result["message"] == "The OpenF1 API did not respond in time"


@pytest.mark.asyncio
async def test_request_error_connect():
    """Test RequestError handling for connection errors."""
    connect_error = httpx.ConnectError("Failed to connect to api.openf1.org")
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = connect_error
        
        result = await safe_fetch("drivers")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "message" in result
        assert result["error"] == "Connection error"
        assert "connect" in result["message"].lower()


@pytest.mark.asyncio
async def test_request_error_network():
    """Test RequestError handling for network errors."""
    network_error = httpx.NetworkError("Network unreachable")
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = network_error
        
        result = await safe_fetch("sessions")
        
        assert isinstance(result, dict)
        assert result["error"] == "Connection error"
        assert "network" in result["message"].lower()


@pytest.mark.asyncio
async def test_generic_exception():
    """Test generic exception handling."""
    generic_error = ValueError("Unexpected value error")
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = generic_error
        
        result = await safe_fetch("drivers")
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "message" in result
        assert result["error"] == "Unexpected error"
        assert result["message"] == "Unexpected value error"


@pytest.mark.asyncio
async def test_error_dict_format():
    """Test that all error responses have consistent format."""
    # Test with HTTPStatusError
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    
    http_error = httpx.HTTPStatusError(
        "400 Bad Request",
        request=Mock(),
        response=mock_response
    )
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = http_error
        
        result = await safe_fetch("drivers")
        
        # Verify dict structure
        assert isinstance(result, dict)
        assert len(result) == 2
        assert set(result.keys()) == {"error", "message"}
        assert isinstance(result["error"], str)
        assert isinstance(result["message"], str)


@pytest.mark.asyncio
async def test_empty_query_string():
    """Test safe_fetch with empty query string."""
    mock_data = [{"session_key": 9158}]
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await safe_fetch("sessions", "")
        
        assert result == mock_data
        mock_fetch.assert_called_once_with("sessions", "")


@pytest.mark.asyncio
async def test_no_query_string():
    """Test safe_fetch without query string parameter."""
    mock_data = [{"meeting_key": 1219}]
    
    with patch('openf1_mcp.error_handler.fetch_openf1_data', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await safe_fetch("meetings")
        
        assert result == mock_data
        mock_fetch.assert_called_once_with("meetings", "")
