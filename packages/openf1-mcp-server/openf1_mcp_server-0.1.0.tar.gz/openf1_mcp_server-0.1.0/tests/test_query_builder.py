"""Unit tests for query builder module."""

import pytest
from openf1_mcp.query_builder import build_query_params


def test_min_max_parameter_conversion():
    """Test that min/max parameters are converted to >= and <= operators."""
    params = {
        "speed_min": 300,
        "speed_max": 350
    }
    result = build_query_params(params)
    
    assert "speed>=300" in result
    assert "speed<=350" in result
    assert "&" in result


def test_min_max_with_exact_match():
    """Test combining min/max parameters with exact match parameters."""
    params = {
        "speed_min": 300,
        "speed_max": 350,
        "driver_number": 1
    }
    result = build_query_params(params)
    
    assert "speed>=300" in result
    assert "speed<=350" in result
    assert "driver_number=1" in result


def test_start_end_parameter_conversion():
    """Test that start/end parameters are converted to >= and < operators."""
    params = {
        "date_start": "2024-01-01T00:00:00",
        "date_end": "2024-12-31T23:59:59"
    }
    result = build_query_params(params)
    
    assert "date>=2024-01-01T00%3A00%3A00" in result
    assert "date<2024-12-31T23%3A59%3A59" in result


def test_exact_match_parameters():
    """Test that regular parameters use exact match with = operator."""
    params = {
        "driver_number": 1,
        "session_key": 9158,
        "meeting_key": 1219
    }
    result = build_query_params(params)
    
    assert "driver_number=1" in result
    assert "session_key=9158" in result
    assert "meeting_key=1219" in result


def test_none_value_handling():
    """Test that None values are skipped in query string."""
    params = {
        "driver_number": 1,
        "session_key": None,
        "speed_min": 300,
        "speed_max": None
    }
    result = build_query_params(params)
    
    assert "driver_number=1" in result
    assert "speed>=300" in result
    assert "session_key" not in result
    assert "speed<=" not in result


def test_all_none_values():
    """Test that all None values result in empty query string."""
    params = {
        "driver_number": None,
        "session_key": None,
        "speed_min": None
    }
    result = build_query_params(params)
    
    assert result == ""


def test_url_encoding_special_characters():
    """Test that special characters are URL-encoded."""
    params = {
        "country_name": "São Paulo",
        "date_start": "2024-01-01T00:00:00+00:00"
    }
    result = build_query_params(params)
    
    # Check that special characters are encoded
    assert "S%C3%A3o" in result  # ã is encoded
    assert "%3A" in result  # : is encoded
    assert "%2B" in result  # + is encoded


def test_url_encoding_spaces():
    """Test that spaces are URL-encoded."""
    params = {
        "team_name": "Red Bull Racing"
    }
    result = build_query_params(params)
    
    assert "team_name=Red%20Bull%20Racing" in result


def test_combining_multiple_parameter_types():
    """Test combining min/max, start/end, and exact match parameters."""
    params = {
        "session_key": 9158,
        "driver_number": 1,
        "speed_min": 300,
        "speed_max": 350,
        "date_start": "2024-01-01",
        "date_end": "2024-12-31",
        "brake": 100
    }
    result = build_query_params(params)
    
    # Check all parameter types are present
    assert "session_key=9158" in result
    assert "driver_number=1" in result
    assert "speed>=300" in result
    assert "speed<=350" in result
    assert "date>=2024-01-01" in result
    assert "date<2024-12-31" in result
    assert "brake=100" in result
    
    # Check proper separation with &
    assert result.count("&") == 6


def test_empty_params():
    """Test that empty parameter dict results in empty query string."""
    params = {}
    result = build_query_params(params)
    
    assert result == ""


def test_single_min_parameter():
    """Test single min parameter without corresponding max."""
    params = {
        "speed_min": 300
    }
    result = build_query_params(params)
    
    assert result == "speed>=300"


def test_single_max_parameter():
    """Test single max parameter without corresponding min."""
    params = {
        "speed_max": 350
    }
    result = build_query_params(params)
    
    assert result == "speed<=350"


def test_single_start_parameter():
    """Test single start parameter without corresponding end."""
    params = {
        "date_start": "2024-01-01"
    }
    result = build_query_params(params)
    
    assert result == "date>=2024-01-01"


def test_single_end_parameter():
    """Test single end parameter without corresponding start."""
    params = {
        "date_end": "2024-12-31"
    }
    result = build_query_params(params)
    
    assert result == "date<2024-12-31"


def test_numeric_values():
    """Test that numeric values are converted to strings correctly."""
    params = {
        "driver_number": 1,
        "speed_min": 300,
        "rpm_max": 15000,
        "throttle_min": 50
    }
    result = build_query_params(params)
    
    assert "driver_number=1" in result
    assert "speed>=300" in result
    assert "rpm<=15000" in result
    assert "throttle>=50" in result


def test_string_values():
    """Test that string values are handled correctly."""
    params = {
        "session_name": "Race",
        "compound": "SOFT",
        "flag": "YELLOW"
    }
    result = build_query_params(params)
    
    assert "session_name=Race" in result
    assert "compound=SOFT" in result
    assert "flag=YELLOW" in result


def test_special_value_latest():
    """Test that special value 'latest' is passed through correctly."""
    params = {
        "session_key": "latest"
    }
    result = build_query_params(params)
    
    assert result == "session_key=latest"


def test_multiple_ranges():
    """Test multiple range parameters for different fields."""
    params = {
        "speed_min": 200,
        "speed_max": 350,
        "rpm_min": 10000,
        "rpm_max": 15000,
        "throttle_min": 50,
        "throttle_max": 100
    }
    result = build_query_params(params)
    
    assert "speed>=200" in result
    assert "speed<=350" in result
    assert "rpm>=10000" in result
    assert "rpm<=15000" in result
    assert "throttle>=50" in result
    assert "throttle<=100" in result


def test_parameter_order_independence():
    """Test that parameter order doesn't affect correctness."""
    params1 = {
        "driver_number": 1,
        "speed_min": 300,
        "session_key": 9158
    }
    params2 = {
        "session_key": 9158,
        "driver_number": 1,
        "speed_min": 300
    }
    
    result1 = build_query_params(params1)
    result2 = build_query_params(params2)
    
    # Both should contain the same parameters (order may differ)
    assert "driver_number=1" in result1
    assert "driver_number=1" in result2
    assert "speed>=300" in result1
    assert "speed>=300" in result2
    assert "session_key=9158" in result1
    assert "session_key=9158" in result2
