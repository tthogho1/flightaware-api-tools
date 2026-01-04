import sys
import logging
from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Union

# Log configuration (output to file)
log_file_path = os.path.join(os.path.dirname(__file__), "server.log")
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    force=True,
)
logging.info("MCP Server is starting...")

# Get API key from .env
load_dotenv()
API_KEY = os.getenv("FLIGHTAWARE_API_KEY")
headers = {"x-apikey": API_KEY}

MAX_PAST_DAYS = 10
MAX_FUTURE_HOURS = 24


def construct_time_range(
    year: Optional[int],
    month: Optional[int],
    day: Optional[int],
    start_time: Optional[str],
    end_time: Optional[str],
):
    now = datetime.now(timezone.utc)

    # If no parameters are provided, use default 1 hour window around now
    if all(p is None for p in [year, month, day, start_time, end_time]):
        start = now - timedelta(hours=1)
        end = now + timedelta(hours=1)
        return (
            start.isoformat().replace("+00:00", "Z"),
            end.isoformat().replace("+00:00", "Z"),
        )

    # Use current date parts if not provided
    y = year if year is not None else now.year
    m = month if month is not None else now.month
    d = day if day is not None else now.day

    try:
        # Construct base date in UTC
        base_date = datetime(y, m, d, tzinfo=timezone.utc)

        if start_time:
            sh, sm = map(int, start_time.split(":"))
            start = base_date.replace(hour=sh, minute=sm, second=0)
        else:
            # Default to beginning of day if date specified
            start = base_date.replace(hour=0, minute=0, second=0)

        if end_time:
            eh, em = map(int, end_time.split(":"))
            end = base_date.replace(hour=eh, minute=em, second=0)
        else:
            # Default to end of day if date specified
            end = base_date.replace(hour=23, minute=59, second=59)

    except ValueError as e:
        raise ValueError(f"Invalid date/time components: {e}")

    # Validation logic (MAX_PAST_DAYS, MAX_FUTURE_HOURS)
    min_start = now - timedelta(days=MAX_PAST_DAYS)
    max_end = now + timedelta(hours=MAX_FUTURE_HOURS)

    if start < min_start:
        raise ValueError(f"start must be within the last {MAX_PAST_DAYS} days.")
    if end > max_end:
        raise ValueError(f"end must be within the next {MAX_FUTURE_HOURS} hours.")
    if end <= start:
        raise ValueError("end must be after start.")

    return (
        start.isoformat(timespec="seconds").replace("+00:00", "Z"),
        end.isoformat(timespec="seconds").replace("+00:00", "Z"),
    )


def convert_to_jst(iso_str):
    """Converts ISO format datetime string to Japan Standard Time (JST)."""
    if not iso_str:
        return None
    try:
        # Replace Z with +00:00 and parse
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        jst = timezone(timedelta(hours=9), "JST")
        return dt.astimezone(jst).isoformat()
    except ValueError:
        return iso_str


def localize_flight_data(flights):
    """Converts time fields in flight data to JST."""
    time_fields = [
        "scheduled_out",
        "estimated_out",
        "actual_out",
        "scheduled_in",
        "estimated_in",
        "actual_in",
        "scheduled_off",
        "estimated_off",
        "actual_off",
        "scheduled_on",
        "estimated_on",
        "actual_on",
    ]
    for flight in flights:
        for field in time_fields:
            if field in flight and flight[field]:
                flight[field] = convert_to_jst(flight[field])
    return flights


def fetch_paginated_data(
    url: str,
    params: Optional[Dict[str, Any]],
    data_key: str,
    fetch_all: bool = False,
) -> Union[List[Dict[str, Any]], str]:
    """Fetches paginated data from the FlightAware API.

    Args:
        url: The API endpoint URL.
        params: Query parameters for the request.
        data_key: The key to extract data from the response (e.g., "departures", "arrivals", "scheduled").
        fetch_all: If True, retrieves all data using pagination.

    Returns:
        List of flight data with times converted to JST, or error message string.
    """
    all_data = []

    while True:
        logging.info(f"API Request: {url} params={params}")
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            logging.warning(f"API Request Failed: status_code={response.status_code}")
            if not all_data:
                return "Failed to retrieve data."
            break

        logging.info(f"API Response: status_code={response.status_code}")
        data = response.json()
        items = data.get(data_key, [])
        all_data.extend(items)

        if not fetch_all:
            break

        next_link = data.get("links", {}).get("next")
        if not next_link:
            break

        url = f"https://aeroapi.flightaware.com{next_link}"
        params = None  # Clear params for subsequent requests

    return localize_flight_data(all_data)


# Initialize MCP Server
mcp = FastMCP("FlightAware-Tracker")


@mcp.tool()
def get_departures(
    airport_code: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    fetch_all: bool = False,
):
    """Retrieves the list of departures for a specified airport.

    Args:
        airport_code: The ICAO code of the airport.
        year: Year (e.g., 2026). Defaults to current year.
        month: Month (1-12). Defaults to current month.
        day: Day (1-31). Defaults to current day.
        start_time: Start time in HH:MM format (e.g., "09:00"). Defaults to 00:00 if date is specified, or 1 hour ago if no date/time provided.
        end_time: End time in HH:MM format (e.g., "18:00"). Defaults to 23:59 if date is specified, or 1 hour from now if no date/time provided.
        fetch_all: If True, retrieves all data using pagination.
    """
    logging.info(
        f"get_departures called with airport_code={airport_code}, year={year}, month={month}, day={day}, start_time={start_time}, end_time={end_time}, fetch_all={fetch_all}"
    )

    try:
        start_param, end_param = construct_time_range(
            year, month, day, start_time, end_time
        )
    except ValueError as e:
        logging.error(f"Validation Error: {e}")
        return f"Input Error: {e}"

    url = f"https://aeroapi.flightaware.com/aeroapi/airports/{airport_code}/flights/departures"
    params = {"start": start_param, "end": end_param}

    return fetch_paginated_data(url, params, "departures", fetch_all)


@mcp.tool()
def get_arrivals(
    airport_code: str,
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    fetch_all: bool = False,
):
    """Retrieves the list of arrivals for a specified airport.

    Args:
        airport_code: The ICAO code of the airport.
        year: Year (e.g., 2026). Defaults to current year.
        month: Month (1-12). Defaults to current month.
        day: Day (1-31). Defaults to current day.
        start_time: Start time in HH:MM format (e.g., "09:00"). Defaults to 00:00 if date is specified, or 1 hour ago if no date/time provided.
        end_time: End time in HH:MM format (e.g., "18:00"). Defaults to 23:59 if date is specified, or 1 hour from now if no date/time provided.
        fetch_all: If True, retrieves all data using pagination.
    """
    logging.info(
        f"get_arrivals called with airport_code={airport_code}, year={year}, month={month}, day={day}, start_time={start_time}, end_time={end_time}, fetch_all={fetch_all}"
    )

    try:
        start_param, end_param = construct_time_range(
            year, month, day, start_time, end_time
        )
    except ValueError as e:
        logging.error(f"Validation Error: {e}")
        return f"Input Error: {e}"

    url = f"https://aeroapi.flightaware.com/aeroapi/airports/{airport_code}/flights/arrivals"
    params = {"start": start_param, "end": end_param}

    return fetch_paginated_data(url, params, "arrivals", fetch_all)


@mcp.tool()
def get_schedules(
    year: Optional[int] = None,
    month: Optional[int] = None,
    day: Optional[int] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    airline: Optional[str] = None,
    flight_number: Optional[str] = None,
    fetch_all: bool = False,
):
    """Retrieves flight future schedules for a specified time range.

    Args:
        year: Year (e.g., 2026). Defaults to current year.
        month: Month (1-12). Defaults to current month.
        day: Day (1-31). Defaults to current day.
        start_time: Start time in HH:MM format (e.g., "09:00"). Defaults to 00:00 if date is specified, or 1 hour ago if no date/time provided.
        end_time: End time in HH:MM format (e.g., "18:00"). Defaults to 23:59 if date is specified, or 1 hour from now if no date/time provided.
        origin: Origin airport code (ICAO).
        destination: Destination airport code (ICAO).
        airline: Airline code (ICAO).
        flight_number: Flight number.
        fetch_all: If True, retrieves all data using pagination.
    """
    logging.info(
        f"get_schedules called with year={year}, month={month}, day={day}, start_time={start_time}, end_time={end_time}, origin={origin}, destination={destination}, airline={airline}, flight_number={flight_number}, fetch_all={fetch_all}"
    )

    try:
        start_date, end_date = construct_time_range(
            year, month, day, start_time, end_time
        )
    except ValueError as e:
        logging.error(f"Validation Error: {e}")
        return f"Input Error: {e}"

    url = f"https://aeroapi.flightaware.com/aeroapi/schedules/{start_date}/{end_date}"

    params = {}
    if origin:
        params["origin"] = origin
    if destination:
        params["destination"] = destination
    if airline:
        params["airline"] = airline
    if flight_number:
        params["flight_number"] = flight_number

    return fetch_paginated_data(url, params if params else None, "scheduled", fetch_all)


if __name__ == "__main__":
    mcp.run()
