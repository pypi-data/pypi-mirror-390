"""Integration tests for MCP tools."""

import pytest
from unittest.mock import AsyncMock, patch
from openf1_mcp.server import (
    get_meetings,
    get_sessions,
    get_drivers,
    get_laps,
    get_position,
    get_car_data,
    get_location,
    get_race_control,
    get_pit,
    get_intervals,
    get_stints,
    get_team_radio,
    get_weather,
    get_session_result,
    get_starting_grid,
    get_overtakes
)


@pytest.mark.asyncio
async def test_get_meetings_with_parameters():
    """Test get_meetings tool with valid parameters."""
    mock_data = [
        {
            "meeting_key": 1219,
            "meeting_name": "Monaco Grand Prix",
            "year": 2024,
            "country_name": "Monaco"
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_meetings(year=2024, country_name="Monaco")
        
        assert result == mock_data
        assert len(result) == 1
        assert result[0]["meeting_key"] == 1219


@pytest.mark.asyncio
async def test_get_meetings_no_parameters():
    """Test get_meetings tool with no parameters."""
    mock_data = [
        {"meeting_key": 1219, "meeting_name": "Monaco Grand Prix"},
        {"meeting_key": 1220, "meeting_name": "Spanish Grand Prix"}
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_meetings()
        
        assert result == mock_data
        assert len(result) == 2


@pytest.mark.asyncio
async def test_get_meetings_with_latest():
    """Test get_meetings tool with special 'latest' value."""
    mock_data = [
        {"meeting_key": 1220, "meeting_name": "Latest Grand Prix"}
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_meetings(meeting_key="latest")
        
        assert result == mock_data
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_get_sessions_with_parameters():
    """Test get_sessions tool with valid parameters."""
    mock_data = [
        {
            "session_key": 9158,
            "session_name": "Race",
            "session_type": "Race",
            "meeting_key": 1219
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_sessions(meeting_key=1219, session_type="Race")
        
        assert result == mock_data
        assert result[0]["session_name"] == "Race"


@pytest.mark.asyncio
async def test_get_sessions_no_parameters():
    """Test get_sessions tool with no parameters."""
    mock_data = [
        {"session_key": 9158, "session_name": "Race"},
        {"session_key": 9157, "session_name": "Qualifying"}
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_sessions()
        
        assert result == mock_data
        assert len(result) == 2


@pytest.mark.asyncio
async def test_get_drivers_with_parameters():
    """Test get_drivers tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "full_name": "Max VERSTAPPEN",
            "team_name": "Red Bull Racing",
            "name_acronym": "VER"
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_drivers(driver_number=1, session_key=9158)
        
        assert result == mock_data
        assert result[0]["driver_number"] == 1


@pytest.mark.asyncio
async def test_get_drivers_no_parameters():
    """Test get_drivers tool with no parameters."""
    mock_data = [
        {"driver_number": 1, "full_name": "Max VERSTAPPEN"},
        {"driver_number": 11, "full_name": "Sergio PEREZ"}
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_drivers()
        
        assert result == mock_data
        assert len(result) == 2


@pytest.mark.asyncio
async def test_get_laps_with_parameters():
    """Test get_laps tool with valid parameters."""
    mock_data = [
        {
            "lap_number": 1,
            "driver_number": 1,
            "lap_duration": 82.5,
            "session_key": 9158
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_laps(session_key=9158, driver_number=1, lap_number=1)
        
        assert result == mock_data
        assert result[0]["lap_duration"] == 82.5


@pytest.mark.asyncio
async def test_get_position_with_parameters():
    """Test get_position tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "position": 1,
            "date": "2024-03-24T15:00:00Z",
            "session_key": 9158
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_position(session_key=9158, driver_number=1, position_max=3)
        
        assert result == mock_data
        assert result[0]["position"] == 1


@pytest.mark.asyncio
async def test_get_car_data_with_parameters():
    """Test get_car_data tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "speed": 320,
            "throttle": 100,
            "brake": 0,
            "n_gear": 8,
            "rpm": 11500
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_car_data(
            session_key=9158,
            driver_number=1,
            speed_min=300,
            throttle_min=99
        )
        
        assert result == mock_data
        assert result[0]["speed"] == 320


@pytest.mark.asyncio
async def test_get_location_with_parameters():
    """Test get_location tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "x": 1500,
            "y": 2000,
            "z": 100,
            "date": "2024-03-24T15:00:00Z"
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_location(session_key=9158, driver_number=1)
        
        assert result == mock_data
        assert result[0]["x"] == 1500


@pytest.mark.asyncio
async def test_get_race_control_with_parameters():
    """Test get_race_control tool with valid parameters."""
    mock_data = [
        {
            "category": "Flag",
            "flag": "YELLOW",
            "scope": "Track",
            "message": "YELLOW FLAG",
            "lap_number": 10
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_race_control(session_key=9158, flag="YELLOW")
        
        assert result == mock_data
        assert result[0]["flag"] == "YELLOW"


@pytest.mark.asyncio
async def test_get_pit_with_parameters():
    """Test get_pit tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "lap_number": 20,
            "pit_duration": 2.3,
            "session_key": 9158
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_pit(session_key=9158, driver_number=1, pit_duration_max=3.0)
        
        assert result == mock_data
        assert result[0]["pit_duration"] == 2.3


@pytest.mark.asyncio
async def test_get_intervals_with_parameters():
    """Test get_intervals tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 2,
            "interval": 0.5,
            "gap_to_leader": 5.2,
            "session_key": 9158
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_intervals(session_key=9158, interval_max=1.0)
        
        assert result == mock_data
        assert result[0]["interval"] == 0.5


@pytest.mark.asyncio
async def test_get_stints_with_parameters():
    """Test get_stints tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "stint_number": 1,
            "compound": "SOFT",
            "tyre_age_at_start": 0,
            "lap_start": 1,
            "lap_end": 25
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_stints(session_key=9158, driver_number=1, compound="SOFT")
        
        assert result == mock_data
        assert result[0]["compound"] == "SOFT"


@pytest.mark.asyncio
async def test_get_team_radio_with_parameters():
    """Test get_team_radio tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "recording_url": "https://example.com/radio.mp3",
            "date": "2024-03-24T15:00:00Z"
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_team_radio(session_key=9158, driver_number=1)
        
        assert result == mock_data
        assert "recording_url" in result[0]


@pytest.mark.asyncio
async def test_get_weather_with_parameters():
    """Test get_weather tool with valid parameters."""
    mock_data = [
        {
            "air_temperature": 25.5,
            "track_temperature": 42.0,
            "humidity": 60.0,
            "rainfall": 0,
            "wind_speed": 3.5
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_weather(session_key=9158, air_temperature_min=20.0)
        
        assert result == mock_data
        assert result[0]["air_temperature"] == 25.5


@pytest.mark.asyncio
async def test_get_session_result_with_parameters():
    """Test get_session_result tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "position": 1,
            "points": 25,
            "status": "Finished",
            "dnf": False
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_session_result(session_key=9158, position_max=1)
        
        assert result == mock_data
        assert result[0]["position"] == 1


@pytest.mark.asyncio
async def test_get_starting_grid_with_parameters():
    """Test get_starting_grid tool with valid parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "position": 1,
            "lap_duration": 80.5,
            "session_key": 9158
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_starting_grid(session_key=9158, position_max=1)
        
        assert result == mock_data
        assert result[0]["position"] == 1


@pytest.mark.asyncio
async def test_get_overtakes_with_parameters():
    """Test get_overtakes tool with valid parameters."""
    mock_data = [
        {
            "overtaking_driver_number": 1,
            "overtaken_driver_number": 44,
            "position": 1,
            "date": "2024-03-24T15:30:00Z"
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_overtakes(session_key=9158, overtaking_driver_number=1)
        
        assert result == mock_data
        assert result[0]["overtaking_driver_number"] == 1


@pytest.mark.asyncio
async def test_tool_with_latest_session_key():
    """Test tools with 'latest' session_key value."""
    mock_data = [{"session_key": "latest", "data": "test"}]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_sessions(session_key="latest")
        
        assert result == mock_data
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_tool_error_response():
    """Test that tools properly return error responses."""
    error_response = {
        "error": "API error: 404",
        "message": "Not Found"
    }
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = error_response
        
        result = await get_drivers(driver_number=999)
        
        assert isinstance(result, dict)
        assert "error" in result
        assert result["error"] == "API error: 404"


@pytest.mark.asyncio
async def test_tool_empty_response():
    """Test that tools handle empty responses correctly."""
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = []
        
        result = await get_drivers(driver_number=999)
        
        assert result == []
        assert isinstance(result, list)


@pytest.mark.asyncio
async def test_multiple_filter_parameters():
    """Test tools with multiple filter parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "speed": 320,
            "throttle": 100,
            "n_gear": 8
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_car_data(
            session_key=9158,
            driver_number=1,
            speed_min=300,
            speed_max=350,
            throttle_min=99,
            n_gear=8
        )
        
        assert result == mock_data
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_date_range_parameters():
    """Test tools with date range parameters."""
    mock_data = [
        {
            "driver_number": 1,
            "date": "2024-03-24T15:30:00Z",
            "position": 1
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_position(
            session_key=9158,
            driver_number=1,
            date_start="2024-03-24T15:00:00Z",
            date_end="2024-03-24T16:00:00Z"
        )
        
        assert result == mock_data
        mock_fetch.assert_called_once()


@pytest.mark.asyncio
async def test_response_structure_verification():
    """Test that tool responses maintain expected structure."""
    mock_data = [
        {
            "driver_number": 1,
            "full_name": "Max VERSTAPPEN",
            "team_name": "Red Bull Racing",
            "session_key": 9158
        }
    ]
    
    with patch('openf1_mcp.server.safe_fetch', new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = mock_data
        
        result = await get_drivers(session_key=9158, driver_number=1)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], dict)
        assert "driver_number" in result[0]
        assert "full_name" in result[0]
        assert "team_name" in result[0]
