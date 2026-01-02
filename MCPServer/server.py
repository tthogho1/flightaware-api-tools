import sys
import logging
from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Optional

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


def validate_time_range(start_str: Optional[str], end_str: Optional[str]):
    now = datetime.now(timezone.utc)

    if start_str:
        try:
            # Replace Z with +00:00 and parse
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(
                f"Invalid start time format: {start_str}. Use ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)."
            )
    else:
        start = now - timedelta(hours=1)

    if end_str:
        try:
            # Replace Z with +00:00 and parse
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError(
                f"Invalid end time format: {end_str}. Use ISO 8601 (YYYY-MM-DDTHH:MM:SSZ)."
            )
    else:
        end = now + timedelta(hours=1)

    # Ensure timezone awareness
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)

    min_start = now - timedelta(days=MAX_PAST_DAYS)
    max_end = now + timedelta(hours=MAX_FUTURE_HOURS)

    if start < min_start:
        raise ValueError(f"start must be within the last {MAX_PAST_DAYS} days.")
    if end > max_end:
        raise ValueError(f"end must be within the next {MAX_FUTURE_HOURS} hours.")
    if end <= start:
        raise ValueError("end must be after start.")

    return (
        start.isoformat().replace("+00:00", "Z"),
        end.isoformat().replace("+00:00", "Z"),
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


# Initialize MCP Server
mcp = FastMCP("FlightAware-Tracker")


@mcp.tool()
def get_departures(
    airport_code: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    fetch_all: bool = False,
):
    """Retrieves the list of departures for a specified airport.

    Args:
        airport_code: The ICAO code of the airport.
        start: Start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ). Defaults to 1 hour ago. Must be within the last 10 days.
        end: End time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ). Defaults to 1 hour from now. Must be within the next 24 hours.
        fetch_all: If True, retrieves all data using pagination.
    """
    logging.info(
        f"get_departures called with airport_code={airport_code}, start={start}, end={end}, fetch_all={fetch_all}"
    )

    try:
        start_param, end_param = validate_time_range(start, end)
    except ValueError as e:
        logging.error(f"Validation Error: {e}")
        return f"Input Error: {e}"

    url = f"https://aeroapi.flightaware.com/aeroapi/airports/{airport_code}/flights/departures"

    params = {"start": start_param, "end": end_param}

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
        departures = data.get("departures", [])
        all_data.extend(departures)

        if not fetch_all:
            break

        next_link = data.get("links", {}).get("next")
        if not next_link:
            break

        url = f"https://aeroapi.flightaware.com{next_link}"
        params = None  # Clear params for subsequent requests

    return localize_flight_data(all_data)


@mcp.tool()
def get_arrivals(
    airport_code: str,
    start: Optional[str] = None,
    end: Optional[str] = None,
    fetch_all: bool = False,
):
    """Retrieves the list of arrivals for a specified airport.

    Args:
        airport_code: The ICAO code of the airport.
        start: Start time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ). Defaults to 1 hour ago. Must be within the last 10 days.
        end: End time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ). Defaults to 1 hour from now. Must be within the next 24 hours.
        fetch_all: If True, retrieves all data using pagination.
    """
    logging.info(
        f"get_arrivals called with airport_code={airport_code}, start={start}, end={end}, fetch_all={fetch_all}"
    )

    try:
        start_param, end_param = validate_time_range(start, end)
    except ValueError as e:
        logging.error(f"Validation Error: {e}")
        return f"Input Error: {e}"

    url = f"https://aeroapi.flightaware.com/aeroapi/airports/{airport_code}/flights/arrivals"

    params = {"start": start_param, "end": end_param}

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
        arrivals = data.get("arrivals", [])
        all_data.extend(arrivals)

        if not fetch_all:
            break

        next_link = data.get("links", {}).get("next")
        if not next_link:
            break

        url = f"https://aeroapi.flightaware.com{next_link}"
        params = None  # Clear params for subsequent requests

    return localize_flight_data(all_data)


if __name__ == "__main__":
    mcp.run()
