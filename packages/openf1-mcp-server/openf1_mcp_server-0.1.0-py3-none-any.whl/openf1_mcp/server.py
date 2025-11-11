"""OpenF1 MCP Server - Main server implementation."""

from mcp.server.fastmcp import FastMCP
from typing import Any, Union
from .query_builder import build_query_params
from .error_handler import safe_fetch

# Initialize FastMCP server
mcp = FastMCP("openf1")


async def query_openf1(
    endpoint: str,
    **params: Any
) -> Union[list[dict[str, Any]], dict[str, str]]:
    """
    Helper function to query OpenF1 API with parameters.
    
    Builds query string from parameters and invokes safe_fetch.
    
    Args:
        endpoint: API endpoint name (e.g., "drivers", "car_data")
        **params: Query parameters as keyword arguments
    
    Returns:
        List of data records on success, error dict on failure
    """
    # Build query string from parameters
    query_string = build_query_params(params)
    
    # Fetch data with error handling
    return await safe_fetch(endpoint, query_string)


@mcp.tool()
async def get_meetings(
    meeting_key: int | str | None = None,
    year: int | None = None,
    country_name: str | None = None,
    circuit_short_name: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 meetings (Grand Prix events and testing weekends).
    
    A meeting represents a Grand Prix weekend or testing event that contains multiple
    sessions (practice, qualifying, sprint, race). Use this tool to find information
    about F1 events, including dates, locations, and circuit details.
    
    Args:
        meeting_key: Unique identifier for the meeting. Use "latest" to get the most
            recent meeting, or provide a specific meeting_key number.
        year: Filter meetings by year (e.g., 2024, 2023).
        country_name: Filter by country name (e.g., "Monaco", "Italy", "United States").
        circuit_short_name: Filter by circuit short name (e.g., "Monza", "Silverstone").
        date_start: Filter meetings starting from this date (ISO 8601 format, e.g.,
            "2024-03-01T00:00:00Z").
        date_end: Filter meetings ending before this date (ISO 8601 format).
    
    Returns:
        List of meeting records, each containing:
        - meeting_key: Unique meeting identifier
        - meeting_name: Official name of the meeting
        - meeting_official_name: Full official name
        - location: City/location name
        - country_name: Country name
        - country_code: ISO country code
        - circuit_key: Unique circuit identifier
        - circuit_short_name: Short circuit name
        - date_start: Meeting start date
        - gmt_offset: GMT offset for the location
        - year: Year of the meeting
        
        On error, returns a dict with "error" and "message" keys.
    
    Examples:
        - Get the latest meeting: get_meetings(meeting_key="latest")
        - Get all 2024 meetings: get_meetings(year=2024)
        - Get Monaco Grand Prix: get_meetings(country_name="Monaco")
        - Get meetings in date range: get_meetings(date_start="2024-01-01T00:00:00Z",
            date_end="2024-06-30T23:59:59Z")
    """
    return await query_openf1(
        "meetings",
        meeting_key=meeting_key,
        year=year,
        country_name=country_name,
        circuit_short_name=circuit_short_name,
        date_start=date_start,
        date_end=date_end
    )


@mcp.tool()
async def get_sessions(
    session_key: int | str | None = None,
    meeting_key: int | str | None = None,
    session_name: str | None = None,
    session_type: str | None = None,
    country_name: str | None = None,
    year: int | None = None,
    date_start: str | None = None,
    date_end: str | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 sessions within meetings.
    
    A session represents a distinct period of track activity such as practice, qualifying,
    sprint, or race. Use this tool to find information about specific sessions, including
    timing, type, and status.
    
    Args:
        session_key: Unique identifier for the session. Use "latest" to get the most
            recent session, or provide a specific session_key number.
        meeting_key: Filter sessions by meeting identifier. Use "latest" for the most
            recent meeting.
        session_name: Filter by session name (e.g., "Practice 1", "Qualifying", "Race").
        session_type: Filter by session type (e.g., "Practice", "Qualifying", "Sprint",
            "Race").
        country_name: Filter by country name (e.g., "Monaco", "Italy").
        year: Filter sessions by year (e.g., 2024, 2023).
        date_start: Filter sessions starting from this date (ISO 8601 format, e.g.,
            "2024-03-01T00:00:00Z").
        date_end: Filter sessions ending before this date (ISO 8601 format).
    
    Returns:
        List of session records, each containing:
        - session_key: Unique session identifier
        - session_name: Name of the session (e.g., "Race", "Qualifying")
        - session_type: Type of session
        - date_start: Session start date and time
        - date_end: Session end date and time
        - gmt_offset: GMT offset for the location
        - meeting_key: Associated meeting identifier
        - location: City/location name
        - country_name: Country name
        - country_code: ISO country code
        - circuit_key: Unique circuit identifier
        - circuit_short_name: Short circuit name
        - year: Year of the session
        
        On error, returns a dict with "error" and "message" keys.
    
    Examples:
        - Get the latest session: get_sessions(session_key="latest")
        - Get all sessions for a meeting: get_sessions(meeting_key=1234)
        - Get all race sessions in 2024: get_sessions(session_type="Race", year=2024)
        - Get qualifying sessions: get_sessions(session_name="Qualifying")
        - Get sessions in date range: get_sessions(date_start="2024-03-01T00:00:00Z",
            date_end="2024-03-31T23:59:59Z")
    """
    return await query_openf1(
        "sessions",
        session_key=session_key,
        meeting_key=meeting_key,
        session_name=session_name,
        session_type=session_type,
        country_name=country_name,
        year=year,
        date_start=date_start,
        date_end=date_end
    )


@mcp.tool()
async def get_drivers(
    driver_number: int | None = None,
    session_key: int | str | None = None,
    meeting_key: int | str | None = None,
    name_acronym: str | None = None,
    team_name: str | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 driver information and participation data.
    
    Use this tool to get information about F1 drivers, including their names, numbers,
    teams, and participation in specific sessions or meetings. Driver data includes
    biographical information, team affiliations, and visual assets like headshots.
    
    Args:
        driver_number: The driver's racing number (e.g., 1 for Verstappen, 44 for Hamilton).
            Each driver has a unique number they use throughout their career.
        session_key: Filter drivers by session identifier. Use "latest" to get drivers
            from the most recent session.
        meeting_key: Filter drivers by meeting identifier. Use "latest" for the most
            recent meeting.
        name_acronym: Filter by driver's three-letter acronym (e.g., "VER" for Verstappen,
            "HAM" for Hamilton, "LEC" for Leclerc).
        team_name: Filter by team name (e.g., "Red Bull Racing", "Ferrari", "Mercedes").
    
    Returns:
        List of driver records, each containing:
        - driver_number: Driver's racing number
        - broadcast_name: Name as displayed in broadcasts
        - full_name: Driver's full name
        - first_name: Driver's first name
        - last_name: Driver's last name
        - name_acronym: Three-letter acronym
        - team_name: Current team name
        - team_colour: Team color in hex format
        - country_code: Driver's country code (ISO 3166-1 alpha-3)
        - headshot_url: URL to driver's headshot image
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Examples:
        - Get all drivers in latest session: get_drivers(session_key="latest")
        - Get specific driver by number: get_drivers(driver_number=1)
        - Get driver by acronym: get_drivers(name_acronym="VER")
        - Get all Ferrari drivers: get_drivers(team_name="Ferrari")
        - Get drivers in specific session: get_drivers(session_key=9158)
    """
    return await query_openf1(
        "drivers",
        driver_number=driver_number,
        session_key=session_key,
        meeting_key=meeting_key,
        name_acronym=name_acronym,
        team_name=team_name
    )


@mcp.tool()
async def get_laps(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    lap_number: int | None = None,
    lap_duration_min: float | None = None,
    lap_duration_max: float | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 lap timing data and performance information.
    
    Use this tool to get detailed lap-by-lap timing data for drivers during sessions.
    Lap data includes lap times, sector times, and lap-specific information like
    whether the lap was completed under yellow flags or if it was deleted.
    
    Args:
        session_key: Filter laps by session identifier. Use "latest" to get laps from
            the most recent session. Required to get meaningful lap data.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16).
        lap_number: Filter by specific lap number (e.g., 1 for first lap, 58 for lap 58).
        lap_duration_min: Minimum lap duration in seconds (e.g., 80.5 for laps faster
            than or equal to 1:20.5). Use to filter for fast laps.
        lap_duration_max: Maximum lap duration in seconds (e.g., 90.0 for laps slower
            than or equal to 1:30.0). Use to filter out slow laps.
    
    Returns:
        List of lap records, each containing:
        - lap_number: The lap number
        - driver_number: Driver's racing number
        - lap_duration: Total lap time in seconds
        - is_pit_out_lap: Boolean indicating if this was a pit exit lap
        - duration_sector_1: Sector 1 time in seconds
        - duration_sector_2: Sector 2 time in seconds
        - duration_sector_3: Sector 3 time in seconds
        - segments_sector_1: Sector 1 mini-sectors array (green/yellow/purple flags)
        - segments_sector_2: Sector 2 mini-sectors array
        - segments_sector_3: Sector 3 mini-sectors array
        - st_speed: Speed trap measurement in km/h
        - date_start: Lap start timestamp (ISO 8601)
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Examples:
        - Get all laps in latest session: get_laps(session_key="latest")
        - Get laps for specific driver: get_laps(session_key=9158, driver_number=1)
        - Get fastest laps under 85 seconds: get_laps(session_key=9158, lap_duration_max=85.0)
        - Get specific lap: get_laps(session_key=9158, driver_number=1, lap_number=10)
        - Get laps in time range: get_laps(session_key=9158, lap_duration_min=80.0,
            lap_duration_max=85.0)
    """
    return await query_openf1(
        "laps",
        session_key=session_key,
        driver_number=driver_number,
        lap_number=lap_number,
        lap_duration_min=lap_duration_min,
        lap_duration_max=lap_duration_max
    )


@mcp.tool()
async def get_position(
    session_key: int | str | None = None,
    meeting_key: int | str | None = None,
    driver_number: int | None = None,
    position_min: int | None = None,
    position_max: int | None = None,
    date_start: str | None = None,
    date_end: str | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 driver position data throughout sessions.
    
    Use this tool to track driver positions over time during a session. Position data
    is updated frequently (multiple times per second during live sessions) and shows
    the running order of drivers on track. This is useful for analyzing position changes,
    battles, and race progression.
    
    Args:
        session_key: Filter positions by session identifier. Use "latest" to get positions
            from the most recent session. Highly recommended to specify a session.
        meeting_key: Filter positions by meeting identifier. Use "latest" for the most
            recent meeting.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16).
        position_min: Minimum position to include (e.g., 1 for leaders, 10 for top 10).
            Use to filter for drivers in specific position ranges.
        position_max: Maximum position to include (e.g., 5 for top 5, 10 for top 10).
        date_start: Filter positions from this timestamp onwards (ISO 8601 format, e.g.,
            "2024-03-24T15:00:00Z"). Useful for analyzing specific race periods.
        date_end: Filter positions up to this timestamp (ISO 8601 format).
    
    Returns:
        List of position records, each containing:
        - date: Timestamp of the position update (ISO 8601)
        - driver_number: Driver's racing number
        - position: Driver's position in the running order (1 = first place)
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Note:
        Position data can be very large for full sessions as it updates multiple times
        per second. Consider using date_start/date_end or position filters to limit
        the result set.
    
    Examples:
        - Get current positions in latest session: get_position(session_key="latest")
        - Get position history for driver: get_position(session_key=9158, driver_number=1)
        - Get top 3 positions only: get_position(session_key=9158, position_max=3)
        - Get positions in time range: get_position(session_key=9158,
            date_start="2024-03-24T15:00:00Z", date_end="2024-03-24T15:30:00Z")
        - Get midfield battle (P5-P10): get_position(session_key=9158, position_min=5,
            position_max=10)
    """
    return await query_openf1(
        "position",
        session_key=session_key,
        meeting_key=meeting_key,
        driver_number=driver_number,
        position_min=position_min,
        position_max=position_max,
        date_start=date_start,
        date_end=date_end
    )


@mcp.tool()
async def get_car_data(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    speed_min: int | None = None,
    speed_max: int | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    brake: int | None = None,
    drs: int | None = None,
    n_gear: int | None = None,
    rpm_min: int | None = None,
    rpm_max: int | None = None,
    throttle_min: int | None = None,
    throttle_max: int | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 car telemetry data including speed, throttle, brake, DRS, gear, and RPM.
    
    Use this tool to access detailed car telemetry data captured during sessions. Telemetry
    data is sampled at high frequency (multiple times per second) and provides insights into
    driver inputs, car performance, and driving style. This data is essential for performance
    analysis, comparing drivers, and understanding racing lines.
    
    Note: Telemetry data may not be available during live sessions and typically becomes
    available after the session concludes.
    
    Args:
        session_key: Filter telemetry by session identifier. Use "latest" to get data from
            the most recent session. Highly recommended to specify a session.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16). Recommended to
            specify a driver to limit the large dataset.
        speed_min: Minimum speed in km/h (e.g., 300 for speeds >= 300 km/h). Use to filter
            for high-speed sections or specific speed ranges.
        speed_max: Maximum speed in km/h (e.g., 350 for speeds <= 350 km/h).
        date_start: Filter telemetry from this timestamp onwards (ISO 8601 format, e.g.,
            "2024-03-24T15:00:00Z"). Useful for analyzing specific laps or race periods.
        date_end: Filter telemetry up to this timestamp (ISO 8601 format).
        brake: Brake status value. Typically 0 (not braking) or 100 (full braking). Use to
            find braking zones or analyze braking patterns.
        drs: DRS (Drag Reduction System) status value. Values indicate DRS state (e.g., 0 for
            closed, higher values for open/available). Use to analyze DRS usage.
        n_gear: Gear number from 0 to 8 (0 = neutral, 1-8 = gears 1-8). Use to analyze gear
            selection in different track sections.
        rpm_min: Minimum engine RPM (e.g., 10000 for RPM >= 10000). Use to filter for
            high-rev sections or specific RPM ranges.
        rpm_max: Maximum engine RPM (e.g., 12000 for RPM <= 12000).
        throttle_min: Minimum throttle percentage from 0-100 (e.g., 50 for >= 50% throttle).
            Use to analyze full-throttle sections or throttle application.
        throttle_max: Maximum throttle percentage from 0-100 (e.g., 100 for <= 100% throttle).
    
    Returns:
        List of telemetry records, each containing:
        - date: Timestamp of the telemetry sample (ISO 8601)
        - driver_number: Driver's racing number
        - speed: Speed in km/h
        - throttle: Throttle percentage (0-100)
        - brake: Brake status (0 or 100)
        - drs: DRS status value
        - n_gear: Current gear (0-8)
        - rpm: Engine RPM
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Warning:
        Car telemetry data can be extremely large (millions of records per session). Always
        use filters like driver_number, date ranges, or specific parameter ranges to limit
        the result set. Requesting all telemetry for a session without filters may result
        in timeouts or very large responses.
    
    Examples:
        - Get telemetry for specific driver: get_car_data(session_key=9158, driver_number=1)
        - Get high-speed telemetry: get_car_data(session_key=9158, driver_number=1,
            speed_min=300)
        - Get braking zones: get_car_data(session_key=9158, driver_number=1, brake=100)
        - Get DRS usage: get_car_data(session_key=9158, driver_number=1, drs=10)
        - Get telemetry in time range: get_car_data(session_key=9158, driver_number=1,
            date_start="2024-03-24T15:00:00Z", date_end="2024-03-24T15:05:00Z")
        - Get full-throttle sections: get_car_data(session_key=9158, driver_number=1,
            throttle_min=99)
    """
    return await query_openf1(
        "car_data",
        session_key=session_key,
        driver_number=driver_number,
        speed_min=speed_min,
        speed_max=speed_max,
        date_start=date_start,
        date_end=date_end,
        brake=brake,
        drs=drs,
        n_gear=n_gear,
        rpm_min=rpm_min,
        rpm_max=rpm_max,
        throttle_min=throttle_min,
        throttle_max=throttle_max
    )


@mcp.tool()
async def get_location(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    x_min: int | None = None,
    x_max: int | None = None,
    y_min: int | None = None,
    y_max: int | None = None,
    z_min: int | None = None,
    z_max: int | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 car location data with track coordinates.
    
    Use this tool to access car position data on the track using a 3D coordinate system.
    Location data is sampled at high frequency (multiple times per second) and provides
    the exact position of each car on the circuit. This data is useful for visualizing
    car positions, analyzing racing lines, tracking overtakes, and understanding spatial
    relationships between cars.
    
    The coordinate system uses X, Y, and Z values where:
    - X and Y represent the horizontal position on the track
    - Z represents elevation/height
    
    Args:
        session_key: Filter location data by session identifier. Use "latest" to get data
            from the most recent session. Highly recommended to specify a session.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16). Recommended to
            specify a driver to limit the large dataset.
        date_start: Filter location data from this timestamp onwards (ISO 8601 format, e.g.,
            "2024-03-24T15:00:00Z"). Useful for analyzing specific laps or race periods.
        date_end: Filter location data up to this timestamp (ISO 8601 format).
        x_min: Minimum X coordinate value. Use to filter for specific track sections or
            geographic areas on the circuit.
        x_max: Maximum X coordinate value.
        y_min: Minimum Y coordinate value. Use to filter for specific track sections or
            geographic areas on the circuit.
        y_max: Maximum Y coordinate value.
        z_min: Minimum Z coordinate value (elevation). Use to filter for specific elevation
            ranges or track sections.
        z_max: Maximum Z coordinate value (elevation).
    
    Returns:
        List of location records, each containing:
        - date: Timestamp of the location sample (ISO 8601)
        - driver_number: Driver's racing number
        - x: X coordinate on the track
        - y: Y coordinate on the track
        - z: Z coordinate (elevation)
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Warning:
        Location data can be extremely large (millions of records per session). Always use
        filters like driver_number, date ranges, or coordinate ranges to limit the result
        set. Requesting all location data for a session without filters may result in
        timeouts or very large responses.
    
    Examples:
        - Get location for specific driver: get_location(session_key=9158, driver_number=1)
        - Get location in time range: get_location(session_key=9158, driver_number=1,
            date_start="2024-03-24T15:00:00Z", date_end="2024-03-24T15:05:00Z")
        - Get location in specific track area: get_location(session_key=9158, driver_number=1,
            x_min=1000, x_max=2000, y_min=500, y_max=1500)
        - Get location at specific elevation: get_location(session_key=9158, driver_number=1,
            z_min=100, z_max=200)
        - Compare two drivers' positions: First call get_location for driver 1, then for
            driver 2 with the same date range
    """
    return await query_openf1(
        "location",
        session_key=session_key,
        driver_number=driver_number,
        date_start=date_start,
        date_end=date_end,
        x_min=x_min,
        x_max=x_max,
        y_min=y_min,
        y_max=y_max,
        z_min=z_min,
        z_max=z_max
    )


@mcp.tool()
async def get_race_control(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    category: str | None = None,
    flag: str | None = None,
    scope: str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    lap_number: int | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 race control messages and flag information.
    
    Use this tool to access official race control messages, including flag signals, safety
    car periods, track status changes, penalties, and other race direction communications.
    Race control messages are critical for understanding race incidents, track conditions,
    and official decisions during sessions.
    
    Race control messages include various categories such as:
    - Flag signals (yellow, red, green, blue, etc.)
    - Safety car and virtual safety car periods
    - Track status changes
    - Penalties and investigations
    - DRS status changes
    - Other official race direction messages
    
    Args:
        session_key: Filter messages by session identifier. Use "latest" to get messages
            from the most recent session. Highly recommended to specify a session.
        driver_number: Filter messages related to a specific driver's racing number
            (e.g., 1, 44, 16). Use when looking for driver-specific penalties or incidents.
        category: Filter by message category (e.g., "Flag", "SafetyCar", "Drs", "CarEvent").
            Use to focus on specific types of race control communications.
        flag: Filter by flag type (e.g., "YELLOW", "RED", "GREEN", "BLUE", "CHEQUERED").
            Use when analyzing flag periods or track status.
        scope: Filter by message scope (e.g., "Track", "Sector", "Driver"). Indicates
            whether the message applies to the entire track, a specific sector, or a
            specific driver.
        date_start: Filter messages from this timestamp onwards (ISO 8601 format, e.g.,
            "2024-03-24T15:00:00Z"). Useful for analyzing specific race periods.
        date_end: Filter messages up to this timestamp (ISO 8601 format).
        lap_number: Filter messages by lap number. Use to find messages from a specific
            lap of the race or session.
    
    Returns:
        List of race control message records, each containing:
        - date: Timestamp of the message (ISO 8601)
        - lap_number: Lap number when the message was issued
        - driver_number: Driver number if message is driver-specific (may be null)
        - category: Message category
        - message: Full text of the race control message
        - flag: Flag type if applicable (may be null)
        - scope: Message scope (Track, Sector, or Driver)
        - sector: Sector number if scope is Sector (may be null)
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Examples:
        - Get all race control messages: get_race_control(session_key=9158)
        - Get yellow flag periods: get_race_control(session_key=9158, flag="YELLOW")
        - Get safety car messages: get_race_control(session_key=9158, category="SafetyCar")
        - Get driver-specific messages: get_race_control(session_key=9158, driver_number=1)
        - Get messages in time range: get_race_control(session_key=9158,
            date_start="2024-03-24T15:00:00Z", date_end="2024-03-24T16:00:00Z")
        - Get messages from specific lap: get_race_control(session_key=9158, lap_number=10)
        - Get track-wide messages: get_race_control(session_key=9158, scope="Track")
    """
    return await query_openf1(
        "race_control",
        session_key=session_key,
        driver_number=driver_number,
        category=category,
        flag=flag,
        scope=scope,
        date_start=date_start,
        date_end=date_end,
        lap_number=lap_number
    )


@mcp.tool()
async def get_pit(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    lap_number: int | None = None,
    pit_duration_min: float | None = None,
    pit_duration_max: float | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 pit stop data and timing information.
    
    Use this tool to access detailed pit stop data including pit entry/exit times, pit
    stop duration, and lap numbers. Pit stop data is essential for analyzing race strategy,
    comparing team performance, and understanding how pit stops affect race outcomes.
    
    Pit stop records include timing for the complete pit stop from pit lane entry to exit,
    allowing analysis of both pit crew performance and the strategic timing of stops.
    
    Args:
        session_key: Filter pit stops by session identifier. Use "latest" to get pit stops
            from the most recent session. Highly recommended to specify a session.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16). Use to analyze
            a specific driver's pit stop strategy and performance.
        lap_number: Filter pit stops by the lap number on which they occurred. Use to find
            pit stops during a specific lap or analyze pit stop timing.
        pit_duration_min: Minimum pit stop duration in seconds (e.g., 2.0 for stops >= 2.0s).
            Use to filter for fast pit stops or identify minimum stop times.
        pit_duration_max: Maximum pit stop duration in seconds (e.g., 5.0 for stops <= 5.0s).
            Use to filter out slow stops or find stops within a specific time range.
    
    Returns:
        List of pit stop records, each containing:
        - date: Timestamp when the pit stop occurred (ISO 8601)
        - driver_number: Driver's racing number
        - lap_number: Lap number on which the pit stop occurred
        - pit_duration: Total pit stop duration in seconds (from pit entry to exit)
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Examples:
        - Get all pit stops in session: get_pit(session_key=9158)
        - Get pit stops for specific driver: get_pit(session_key=9158, driver_number=1)
        - Get fast pit stops under 3 seconds: get_pit(session_key=9158, pit_duration_max=3.0)
        - Get pit stops on specific lap: get_pit(session_key=9158, lap_number=20)
        - Get pit stops in duration range: get_pit(session_key=9158, pit_duration_min=2.0,
            pit_duration_max=3.0)
        - Compare team pit stop performance: First call get_pit for one driver, then for
            their teammate to compare pit_duration values
    """
    return await query_openf1(
        "pit",
        session_key=session_key,
        driver_number=driver_number,
        lap_number=lap_number,
        pit_duration_min=pit_duration_min,
        pit_duration_max=pit_duration_max
    )


@mcp.tool()
async def get_intervals(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    interval_min: float | None = None,
    interval_max: float | None = None,
    date_start: str | None = None,
    date_end: str | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 interval and gap data between drivers.
    
    Use this tool to access time gaps and intervals between drivers during sessions.
    Interval data shows the time difference between consecutive drivers in the running
    order, while gap data shows the time difference to the race leader. This data is
    essential for analyzing race battles, understanding field spread, and tracking how
    gaps evolve throughout a session.
    
    Interval data is updated frequently during sessions and provides insights into:
    - Battle intensity between drivers
    - Pace differences between cars
    - Effect of pit stops on gaps
    - Race strategy effectiveness
    
    Args:
        session_key: Filter intervals by session identifier. Use "latest" to get intervals
            from the most recent session. Highly recommended to specify a session.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16). Use to track
            a specific driver's gaps to others throughout the session.
        interval_min: Minimum interval in seconds (e.g., 0.5 for intervals >= 0.5s).
            Use to filter for close battles or specific gap ranges.
        interval_max: Maximum interval in seconds (e.g., 2.0 for intervals <= 2.0s).
            Use to find tight battles or filter out large gaps.
        date_start: Filter intervals from this timestamp onwards (ISO 8601 format, e.g.,
            "2024-03-24T15:00:00Z"). Useful for analyzing specific race periods.
        date_end: Filter intervals up to this timestamp (ISO 8601 format).
    
    Returns:
        List of interval records, each containing:
        - date: Timestamp of the interval measurement (ISO 8601)
        - driver_number: Driver's racing number
        - gap_to_leader: Time gap to the race leader in seconds (null for leader)
        - interval: Time gap to the car directly ahead in seconds (null for leader)
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Note:
        - The race leader will have null values for both gap_to_leader and interval
        - Interval represents the gap to the car immediately ahead
        - Gap_to_leader represents the total time behind the leader
    
    Examples:
        - Get all intervals in session: get_intervals(session_key=9158)
        - Get intervals for specific driver: get_intervals(session_key=9158, driver_number=1)
        - Get close battles (< 1 second): get_intervals(session_key=9158, interval_max=1.0)
        - Get intervals in time range: get_intervals(session_key=9158,
            date_start="2024-03-24T15:00:00Z", date_end="2024-03-24T16:00:00Z")
        - Find tight battles: get_intervals(session_key=9158, interval_min=0.1,
            interval_max=0.5)
        - Track gap evolution: Query intervals at different time ranges to see how gaps
            change throughout the race
    """
    return await query_openf1(
        "intervals",
        session_key=session_key,
        driver_number=driver_number,
        interval_min=interval_min,
        interval_max=interval_max,
        date_start=date_start,
        date_end=date_end
    )


@mcp.tool()
async def get_stints(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    stint_number: int | None = None,
    compound: str | None = None,
    tyre_age_at_start_min: int | None = None,
    tyre_age_at_start_max: int | None = None,
    lap_start_min: int | None = None,
    lap_start_max: int | None = None,
    lap_end_min: int | None = None,
    lap_end_max: int | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 tyre stint data and strategy information.
    
    Use this tool to access detailed information about tyre stints during sessions. A stint
    represents a continuous period of running on the same set of tyres, from when they are
    fitted (usually during a pit stop) until they are changed. Stint data is essential for
    analyzing tyre strategy, compound performance, tyre degradation, and race strategy.
    
    Stint data includes information about:
    - Tyre compound used (SOFT, MEDIUM, HARD, INTERMEDIATE, WET)
    - Stint duration in laps
    - Tyre age at the start of the stint
    - Lap numbers when the stint started and ended
    
    Args:
        session_key: Filter stints by session identifier. Use "latest" to get stints from
            the most recent session. Highly recommended to specify a session.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16). Use to analyze
            a specific driver's tyre strategy and stint performance.
        stint_number: Filter by stint number. Stints are numbered sequentially starting at 1
            for each driver. Use to analyze specific stints (e.g., first stint, final stint).
        compound: Filter by tyre compound. Common values include "SOFT", "MEDIUM", "HARD"
            for dry conditions, and "INTERMEDIATE", "WET" for wet conditions. Use to analyze
            performance of specific compounds or compare compound strategies.
        tyre_age_at_start_min: Minimum tyre age in laps at the start of the stint (e.g., 0
            for new tyres, 5 for tyres with >= 5 laps). Use to filter for fresh or used tyres.
        tyre_age_at_start_max: Maximum tyre age in laps at the start of the stint (e.g., 10
            for tyres with <= 10 laps). Use to analyze stints on tyres of specific age.
        lap_start_min: Minimum lap number when the stint started (e.g., 1 for stints starting
            on or after lap 1). Use to filter stints by when they began in the race.
        lap_start_max: Maximum lap number when the stint started (e.g., 20 for stints starting
            on or before lap 20).
        lap_end_min: Minimum lap number when the stint ended (e.g., 30 for stints ending on
            or after lap 30). Use to filter by stint end timing.
        lap_end_max: Maximum lap number when the stint ended (e.g., 50 for stints ending on
            or before lap 50).
    
    Returns:
        List of stint records, each containing:
        - driver_number: Driver's racing number
        - stint_number: Sequential stint number (starts at 1 for each driver)
        - lap_start: Lap number when the stint started
        - lap_end: Lap number when the stint ended
        - compound: Tyre compound used (SOFT, MEDIUM, HARD, INTERMEDIATE, WET)
        - tyre_age_at_start: Age of the tyres in laps at the start of the stint
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Note:
        - Stint 1 is the first stint of the session for each driver
        - Tyre age of 0 indicates brand new tyres
        - Lap_end may be null for ongoing stints in live sessions
        - Compound names are uppercase (e.g., "SOFT" not "soft")
    
    Examples:
        - Get all stints in session: get_stints(session_key=9158)
        - Get stints for specific driver: get_stints(session_key=9158, driver_number=1)
        - Get first stints only: get_stints(session_key=9158, stint_number=1)
        - Get soft tyre stints: get_stints(session_key=9158, compound="SOFT")
        - Get stints on new tyres: get_stints(session_key=9158, tyre_age_at_start_max=0)
        - Get stints starting in first 10 laps: get_stints(session_key=9158, lap_start_max=10)
        - Get long stints (30+ laps): get_stints(session_key=9158, lap_end_min=30)
        - Compare strategies: Query stints for different drivers to compare compound choices
            and stint lengths
        - Analyze tyre degradation: Get stints with specific compounds and compare lap times
            at different tyre ages
    """
    return await query_openf1(
        "stints",
        session_key=session_key,
        driver_number=driver_number,
        stint_number=stint_number,
        compound=compound,
        tyre_age_at_start_min=tyre_age_at_start_min,
        tyre_age_at_start_max=tyre_age_at_start_max,
        lap_start_min=lap_start_min,
        lap_start_max=lap_start_max,
        lap_end_min=lap_end_min,
        lap_end_max=lap_end_max
    )


@mcp.tool()
async def get_team_radio(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    date_start: str | None = None,
    date_end: str | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 team radio communications between drivers and their teams.
    
    Use this tool to access team radio messages exchanged between drivers and their pit
    crews during sessions. Team radio provides insights into race strategy, driver feedback,
    team instructions, and real-time decision making. Each radio message includes a
    recording URL where you can listen to the actual audio communication.
    
    Team radio data is valuable for:
    - Understanding strategic decisions and their timing
    - Analyzing driver-team communication patterns
    - Reviewing key moments and incidents from the driver's perspective
    - Studying how teams manage races and respond to situations
    
    Args:
        session_key: Filter team radio by session identifier. Use "latest" to get radio
            messages from the most recent session. Highly recommended to specify a session.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16). Use to get
            radio communications for a specific driver. Recommended to specify a driver
            as sessions can have many radio messages.
        date_start: Filter radio messages from this timestamp onwards (ISO 8601 format,
            e.g., "2024-03-24T15:00:00Z"). Useful for finding radio messages during
            specific race periods or incidents.
        date_end: Filter radio messages up to this timestamp (ISO 8601 format). Use with
            date_start to analyze radio communications during a specific time window.
    
    Returns:
        List of team radio records, each containing:
        - date: Timestamp when the radio message was broadcast (ISO 8601)
        - driver_number: Driver's racing number
        - recording_url: URL to the audio recording of the radio message (MP3 format)
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Note:
        - Not all radio communications are broadcast or recorded
        - Recording URLs point to audio files that can be played or downloaded
        - Radio messages are typically available shortly after they are broadcast
        - Some sessions may have limited or no team radio data available
    
    Examples:
        - Get all team radio in session: get_team_radio(session_key=9158)
        - Get radio for specific driver: get_team_radio(session_key=9158, driver_number=1)
        - Get radio in time range: get_team_radio(session_key=9158,
            date_start="2024-03-24T15:00:00Z", date_end="2024-03-24T16:00:00Z")
        - Get radio during specific lap: First get lap timing data to find the timestamp
            range for a lap, then query team radio with those timestamps
        - Analyze strategy calls: Get team radio around pit stop times to hear strategy
            discussions
        - Review incident communications: Get radio messages during the time window of
            a specific incident or race event
    """
    return await query_openf1(
        "team_radio",
        session_key=session_key,
        driver_number=driver_number,
        date_start=date_start,
        date_end=date_end
    )


@mcp.tool()
async def get_weather(
    session_key: int | str | None = None,
    meeting_key: int | str | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
    air_temperature_min: float | None = None,
    air_temperature_max: float | None = None,
    track_temperature_min: float | None = None,
    track_temperature_max: float | None = None,
    humidity_min: float | None = None,
    humidity_max: float | None = None,
    rainfall: int | None = None,
    wind_speed_min: float | None = None,
    wind_speed_max: float | None = None,
    wind_direction_min: int | None = None,
    wind_direction_max: int | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 weather conditions and track temperature data.
    
    Use this tool to access weather data during sessions, including air temperature, track
    temperature, humidity, rainfall, wind speed, and wind direction. Weather conditions
    significantly impact car performance, tyre behavior, and race strategy. Weather data
    is updated at approximately one-minute intervals during sessions.
    
    Weather data is essential for:
    - Understanding how conditions affect lap times and tyre performance
    - Analyzing the impact of temperature on car setup and strategy
    - Tracking changing conditions during sessions
    - Correlating weather with driver performance and incidents
    - Predicting tyre degradation based on track temperature
    
    Args:
        session_key: Filter weather data by session identifier. Use "latest" to get weather
            from the most recent session. Highly recommended to specify a session.
        meeting_key: Filter weather data by meeting identifier. Use "latest" for the most
            recent meeting. Can be used instead of session_key for meeting-wide weather.
        date_start: Filter weather data from this timestamp onwards (ISO 8601 format, e.g.,
            "2024-03-24T15:00:00Z"). Useful for analyzing weather during specific periods.
        date_end: Filter weather data up to this timestamp (ISO 8601 format). Use with
            date_start to analyze weather changes during a specific time window.
        air_temperature_min: Minimum air temperature in degrees Celsius (e.g., 20.0 for
            temperatures >= 20°C). Use to filter for specific temperature conditions.
        air_temperature_max: Maximum air temperature in degrees Celsius (e.g., 30.0 for
            temperatures <= 30°C).
        track_temperature_min: Minimum track temperature in degrees Celsius (e.g., 35.0 for
            track temps >= 35°C). Track temperature is typically higher than air temperature
            and significantly affects tyre performance.
        track_temperature_max: Maximum track temperature in degrees Celsius (e.g., 50.0 for
            track temps <= 50°C).
        humidity_min: Minimum humidity percentage (e.g., 40.0 for humidity >= 40%). Humidity
            affects air density and engine performance.
        humidity_max: Maximum humidity percentage (e.g., 80.0 for humidity <= 80%).
        rainfall: Rainfall indicator value. Use to filter for wet or dry conditions. Typically
            0 for dry, higher values indicate rain intensity.
        wind_speed_min: Minimum wind speed in meters per second (e.g., 2.0 for wind >= 2 m/s).
            Wind affects car balance and straight-line speed.
        wind_speed_max: Maximum wind speed in meters per second (e.g., 10.0 for wind <= 10 m/s).
        wind_direction_min: Minimum wind direction in degrees (0-360, where 0/360 is North,
            90 is East, 180 is South, 270 is West). Use to filter for specific wind directions.
        wind_direction_max: Maximum wind direction in degrees (0-360).
    
    Returns:
        List of weather records, each containing:
        - date: Timestamp of the weather measurement (ISO 8601)
        - air_temperature: Air temperature in degrees Celsius
        - track_temperature: Track surface temperature in degrees Celsius
        - humidity: Humidity percentage (0-100)
        - pressure: Atmospheric pressure in millibars
        - rainfall: Rainfall indicator (0 for dry, higher values for rain)
        - wind_speed: Wind speed in meters per second
        - wind_direction: Wind direction in degrees (0-360)
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Note:
        - Weather data is updated approximately every minute during sessions
        - Track temperature is typically 10-20°C higher than air temperature in sunny conditions
        - All temperature values are in degrees Celsius
        - Wind direction follows standard meteorological convention (0° = North)
        - Rainfall values indicate intensity, with 0 meaning no rain
    
    Examples:
        - Get all weather in session: get_weather(session_key=9158)
        - Get weather for latest session: get_weather(session_key="latest")
        - Get hot conditions: get_weather(session_key=9158, track_temperature_min=45.0)
        - Get weather in time range: get_weather(session_key=9158,
            date_start="2024-03-24T15:00:00Z", date_end="2024-03-24T16:00:00Z")
        - Get rainy conditions: get_weather(session_key=9158, rainfall=1)
        - Get high humidity conditions: get_weather(session_key=9158, humidity_min=70.0)
        - Get windy conditions: get_weather(session_key=9158, wind_speed_min=5.0)
        - Track temperature evolution: Query weather throughout a session to see how track
            temperature changes and affects lap times
        - Compare conditions: Get weather for different sessions to compare how conditions
            varied between practice, qualifying, and race
    """
    return await query_openf1(
        "weather",
        session_key=session_key,
        meeting_key=meeting_key,
        date_start=date_start,
        date_end=date_end,
        air_temperature_min=air_temperature_min,
        air_temperature_max=air_temperature_max,
        track_temperature_min=track_temperature_min,
        track_temperature_max=track_temperature_max,
        humidity_min=humidity_min,
        humidity_max=humidity_max,
        rainfall=rainfall,
        wind_speed_min=wind_speed_min,
        wind_speed_max=wind_speed_max,
        wind_direction_min=wind_direction_min,
        wind_direction_max=wind_direction_max
    )


@mcp.tool()
async def get_session_result(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    position_min: int | None = None,
    position_max: int | None = None,
    dnf: bool | None = None,
    dns: bool | None = None,
    dsq: bool | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 session results and final standings.
    
    Use this tool to access final classification and results for sessions, including race
    results, qualifying results, and practice session standings. Session results provide
    comprehensive information about each driver's final position, status, and performance
    metrics. For qualifying sessions, results include Q1, Q2, and Q3 times.
    
    Session results are essential for:
    - Analyzing final race outcomes and podium finishes
    - Reviewing qualifying performance and grid positions
    - Understanding driver and team performance in sessions
    - Identifying DNFs (Did Not Finish), DNS (Did Not Start), and DSQ (Disqualified) drivers
    - Comparing lap times and gaps between drivers
    
    Args:
        session_key: Filter results by session identifier. Use "latest" to get results from
            the most recent session. Highly recommended to specify a session.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16). Use to get
            results for a specific driver.
        position_min: Minimum finishing position (e.g., 1 for winners, 3 for podium finishers).
            Use to filter for drivers finishing in specific position ranges.
        position_max: Maximum finishing position (e.g., 10 for top 10 finishers, 20 for
            points scorers). Use to focus on specific finishing positions.
        dnf: Filter for drivers who Did Not Finish. Set to True to get only DNF drivers,
            False to exclude DNF drivers, or omit to include all drivers regardless of DNF status.
        dns: Filter for drivers who Did Not Start. Set to True to get only DNS drivers,
            False to exclude DNS drivers, or omit to include all drivers regardless of DNS status.
        dsq: Filter for drivers who were Disqualified. Set to True to get only disqualified
            drivers, False to exclude disqualified drivers, or omit to include all drivers
            regardless of disqualification status.
    
    Returns:
        List of session result records, each containing:
        - driver_number: Driver's racing number
        - position: Final classification position (1 = winner, 2 = second, etc.)
        - points: Championship points earned (for race results)
        - status: Result status (e.g., "Finished", "DNF", "DNS", "DSQ")
        - time: Total race time or time behind winner (for race results)
        - gap_to_leader: Time gap to the race winner
        - laps_completed: Number of laps completed
        - dnf: Boolean indicating Did Not Finish
        - dns: Boolean indicating Did Not Start
        - dsq: Boolean indicating Disqualified
        - duration: Array of qualifying times [Q1, Q2, Q3] for qualifying sessions
        - gap_to_leader: Array of gaps [Q1, Q2, Q3] for qualifying sessions
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Note:
        - For qualifying sessions, duration and gap_to_leader are arrays with Q1, Q2, Q3 values
        - Position may be null for drivers who did not set a time (DNS, DSQ)
        - Points are only awarded in race sessions, not practice or qualifying
        - Status field provides detailed information about why a driver didn't finish
        - DNF, DNS, and DSQ are mutually exclusive status indicators
    
    Examples:
        - Get all results for session: get_session_result(session_key=9158)
        - Get race winner: get_session_result(session_key=9158, position_max=1)
        - Get podium finishers: get_session_result(session_key=9158, position_max=3)
        - Get top 10 finishers: get_session_result(session_key=9158, position_max=10)
        - Get specific driver result: get_session_result(session_key=9158, driver_number=1)
        - Get DNF drivers: get_session_result(session_key=9158, dnf=True)
        - Get disqualified drivers: get_session_result(session_key=9158, dsq=True)
        - Get finishers only: get_session_result(session_key=9158, dnf=False, dns=False,
            dsq=False)
        - Get midfield results: get_session_result(session_key=9158, position_min=5,
            position_max=10)
        - Compare qualifying performance: Get session_result for qualifying session to see
            Q1, Q2, Q3 progression
    """
    return await query_openf1(
        "session_result",
        session_key=session_key,
        driver_number=driver_number,
        position_min=position_min,
        position_max=position_max,
        dnf=dnf,
        dns=dns,
        dsq=dsq
    )


@mcp.tool()
async def get_starting_grid(
    session_key: int | str | None = None,
    driver_number: int | None = None,
    position_min: int | None = None,
    position_max: int | None = None,
    lap_duration_min: float | None = None,
    lap_duration_max: float | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 starting grid positions and qualifying lap times.
    
    Use this tool to access starting grid information for race sessions, showing where each
    driver will start the race based on qualifying results. Starting grid data includes
    the grid position and the qualifying lap time that determined that position. Grid
    positions may differ from qualifying results due to penalties or other factors.
    
    Starting grid data is essential for:
    - Analyzing race starting positions and their impact on race outcomes
    - Understanding qualifying performance and lap time differences
    - Identifying grid penalties and position changes
    - Comparing qualifying pace between drivers and teams
    - Predicting race strategy based on starting position
    
    Args:
        session_key: Filter starting grid by session identifier. Use "latest" to get the
            starting grid from the most recent session. Highly recommended to specify a session.
        driver_number: Filter by driver's racing number (e.g., 1, 44, 16). Use to get
            starting position for a specific driver.
        position_min: Minimum grid position (e.g., 1 for pole position, 5 for top 5 starters).
            Use to filter for drivers starting in specific grid position ranges.
        position_max: Maximum grid position (e.g., 10 for top 10 starters, 20 for all starters).
            Use to focus on specific starting positions.
        lap_duration_min: Minimum qualifying lap time in seconds (e.g., 80.0 for lap times
            >= 1:20.0). Use to filter for fast qualifying laps.
        lap_duration_max: Maximum qualifying lap time in seconds (e.g., 85.0 for lap times
            <= 1:25.0). Use to filter for specific lap time ranges.
    
    Returns:
        List of starting grid records, each containing:
        - driver_number: Driver's racing number
        - position: Starting grid position (1 = pole position, 2 = front row, etc.)
        - lap_duration: Qualifying lap time in seconds that determined the grid position
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Note:
        - Position 1 is pole position (front of the grid)
        - Grid positions may differ from qualifying results due to penalties
        - Lap_duration represents the best qualifying lap time for that driver
        - Starting grid is typically determined by qualifying session results
        - Some drivers may start from pit lane and not appear in the grid data
    
    Examples:
        - Get full starting grid: get_starting_grid(session_key=9158)
        - Get pole position: get_starting_grid(session_key=9158, position_max=1)
        - Get front row starters: get_starting_grid(session_key=9158, position_max=2)
        - Get top 10 starters: get_starting_grid(session_key=9158, position_max=10)
        - Get specific driver's grid position: get_starting_grid(session_key=9158,
            driver_number=1)
        - Get fastest qualifiers: get_starting_grid(session_key=9158, lap_duration_max=82.0)
        - Get midfield starters: get_starting_grid(session_key=9158, position_min=5,
            position_max=10)
        - Compare qualifying pace: Get starting grid to see lap time differences between
            drivers and identify performance gaps
        - Analyze grid penalties: Compare starting_grid positions with session_result
            qualifying positions to identify penalty-affected drivers
    """
    return await query_openf1(
        "starting_grid",
        session_key=session_key,
        driver_number=driver_number,
        position_min=position_min,
        position_max=position_max,
        lap_duration_min=lap_duration_min,
        lap_duration_max=lap_duration_max
    )


@mcp.tool()
async def get_overtakes(
    session_key: int | str | None = None,
    overtaking_driver_number: int | None = None,
    overtaken_driver_number: int | None = None,
    position: int | None = None,
    date_start: str | None = None,
    date_end: str | None = None
) -> list[dict[str, Any]] | dict[str, str]:
    """
    Query Formula 1 overtake information and position changes during races.
    
    Use this tool to access data about overtaking maneuvers during race sessions. Overtake
    data captures when one driver passes another, including which drivers were involved,
    the position after the overtake, and the exact timing. This data is essential for
    analyzing race action, wheel-to-wheel battles, and understanding how positions change
    throughout a race.
    
    Overtake data is valuable for:
    - Analyzing race action and exciting moments
    - Understanding driver racecraft and overtaking ability
    - Tracking position changes throughout the race
    - Identifying key battles and rivalries
    - Evaluating the impact of car performance on overtaking
    - Studying overtaking zones and track characteristics
    
    Note: Overtake data is typically only available for race sessions, not practice or
    qualifying sessions.
    
    Args:
        session_key: Filter overtakes by session identifier. Use "latest" to get overtakes
            from the most recent session. Highly recommended to specify a session. Note that
            overtake data is only meaningful for race sessions.
        overtaking_driver_number: Filter by the driver number of the driver who performed
            the overtake (e.g., 1, 44, 16). Use to analyze a specific driver's overtaking
            performance and see who they passed during the race.
        overtaken_driver_number: Filter by the driver number of the driver who was overtaken
            (e.g., 1, 44, 16). Use to see who passed a specific driver or analyze defensive
            performance.
        position: Filter by the position value after the overtake. This represents the
            overtaking driver's position immediately after completing the pass (e.g., 3 means
            the overtaking driver moved into 3rd place). Use to focus on overtakes for
            specific positions like podium places or points positions.
        date_start: Filter overtakes from this timestamp onwards (ISO 8601 format, e.g.,
            "2024-03-24T15:00:00Z"). Useful for analyzing overtakes during specific race
            periods or after key events like safety cars or pit stops.
        date_end: Filter overtakes up to this timestamp (ISO 8601 format). Use with
            date_start to analyze overtaking activity during a specific time window.
    
    Returns:
        List of overtake records, each containing:
        - date: Timestamp when the overtake occurred (ISO 8601)
        - overtaking_driver_number: Driver number of the driver who performed the overtake
        - overtaken_driver_number: Driver number of the driver who was overtaken
        - position: The overtaking driver's position after completing the overtake
        - session_key: Associated session identifier
        - meeting_key: Associated meeting identifier
        
        On error, returns a dict with "error" and "message" keys.
    
    Note:
        - Overtake data is only available for race sessions, not practice or qualifying
        - Position represents the overtaking driver's position after the pass
        - Not all position changes are recorded as overtakes (e.g., pit stop position changes)
        - Overtakes under yellow flags or safety car may still be recorded but are typically
          penalized
        - Some overtakes may be off-track or result in penalties
    
    Examples:
        - Get all overtakes in race: get_overtakes(session_key=9158)
        - Get overtakes by specific driver: get_overtakes(session_key=9158,
            overtaking_driver_number=1)
        - Get who overtook a specific driver: get_overtakes(session_key=9158,
            overtaken_driver_number=44)
        - Get overtakes for podium positions: get_overtakes(session_key=9158, position=3)
        - Get overtakes in time range: get_overtakes(session_key=9158,
            date_start="2024-03-24T15:00:00Z", date_end="2024-03-24T16:00:00Z")
        - Analyze specific battle: get_overtakes(session_key=9158,
            overtaking_driver_number=1, overtaken_driver_number=44)
        - Get overtakes for points positions: Query with position values 1-10 to see
            overtakes affecting points-scoring positions
        - Track race action: Get all overtakes and sort by date to see the sequence of
          position changes throughout the race
        - Compare overtaking performance: Get overtakes for different drivers to compare
          their wheel-to-wheel racing ability
    """
    return await query_openf1(
        "overtakes",
        session_key=session_key,
        overtaking_driver_number=overtaking_driver_number,
        overtaken_driver_number=overtaken_driver_number,
        position=position,
        date_start=date_start,
        date_end=date_end
    )



def main():
    """Run the OpenF1 MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
