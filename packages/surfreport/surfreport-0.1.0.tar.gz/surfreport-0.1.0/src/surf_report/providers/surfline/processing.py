from collections import defaultdict

from surf_report.utils.helpers import convert_timestamp_to_datetime


def extract_day_time(timestamp, utc_offset):
    """
    Convert a timestamp and UTC offset to day and time strings.
    """
    dt_parts = convert_timestamp_to_datetime(timestamp, utc_offset).split()
    # Assume dt_parts = [weekday, date, time, ...]
    return dt_parts[1], dt_parts[2] if len(dt_parts) >= 3 else (None, None)


def group_spot_report(report_data):
    """
    Groups the detailed spot report data by day.
    Returns a dictionary keyed by day containing grouped forecast details.
    """
    grouped_data = defaultdict(
        lambda: {
            "surf": [],
            "weather": [],
            "tides": [],
            "wind": [],
            "swells": [],
            "sunlight": [],
        }
    )

    # Extract data for each endpoint
    wave_data = report_data.get("wave", {}).get("data", {}).get("wave", [])
    weather_data = report_data.get("weather", {}).get("data", {}).get("weather", [])
    tides_data = report_data.get("tides", {}).get("data", {}).get("tides", [])
    wind_data = report_data.get("wind", {}).get("data", {}).get("wind", [])
    # swells_data = report_data.get("swells", {}).get("data", {}).get("swells", [])
    sunlight_data = report_data.get("sunlight", {}).get("data", {}).get("sunlight", [])

    # Group wave data (surf and swells)
    for wave in wave_data:
        timestamp = wave.get("timestamp")
        utc_offset = wave.get("utcOffset")
        if timestamp:
            day, time_str = extract_day_time(timestamp, utc_offset)
            if wave.get("surf"):
                surf = wave.get("surf")
                surf["time"] = time_str
                grouped_data[day]["surf"].append(surf)
            # Filter and process swells with height > 0
            for swell in wave.get("swells", []):
                if swell.get("height", 0) > 0:  # Only include swells with height > 0
                    swell["time"] = time_str
                    grouped_data[day]["swells"].append(swell)

    # Unused for now since we get this from the wave endpoint
    # for swell_item in swells_data:
    #     timestamp = swell_item.get("timestamp")
    #     utc_offset = swell_item.get("utcOffset")
    #     if timestamp:
    #         day, time_str = extract_day_time(timestamp, utc_offset)
    #         swells_list = swell_item.get("swells", [])
    #         for s in swells_list:
    #             s["time"] = time_str
    #             grouped_data[day]["swells"].append(s)

    # Group weather data
    for weather in weather_data:
        timestamp = weather.get("timestamp")
        utc_offset = weather.get("utcOffset")
        if timestamp:
            day, time_str = extract_day_time(timestamp, utc_offset)
            grouped_data[day]["weather"].append(
                {
                    "time": time_str,
                    "temperature": weather.get("temperature"),
                    "condition": weather.get("condition"),
                }
            )

    # Group tides data (only HIGH and LOW tides)
    for tide in tides_data:
        timestamp = tide.get("timestamp")
        utc_offset = tide.get("utcOffset")
        tide_type = tide.get("type")
        if timestamp and tide_type in ["HIGH", "LOW"]:
            day, time_str = extract_day_time(timestamp, utc_offset)
            grouped_data[day]["tides"].append(
                {
                    "height": tide.get("height"),
                    "type": tide_type,
                    "time": time_str,
                }
            )

    # Group wind data
    for wind in wind_data:
        timestamp = wind.get("timestamp")
        utc_offset = wind.get("utcOffset")
        if timestamp:
            day, time_str = extract_day_time(timestamp, utc_offset)
            grouped_data[day]["wind"].append(
                {
                    "time": time_str,
                    "speed": wind.get("speed"),
                    "direction": wind.get("direction"),
                    "directionType": wind.get("directionType"),
                }
            )

    # Group sunlight data
    for sunlight in sunlight_data:
        timestamp = sunlight.get("sunrise")  # Use sunrise timestamp for grouping
        if timestamp:
            day, _ = extract_day_time(timestamp, sunlight.get("sunriseUTCOffset"))
            grouped_data[day]["sunlight"].append(
                {
                    "dawn": convert_timestamp_to_datetime(
                        sunlight.get("dawn"), sunlight.get("dawnUTCOffset")
                    ).split()[2],
                    "sunrise": convert_timestamp_to_datetime(
                        sunlight.get("sunrise"), sunlight.get("sunriseUTCOffset")
                    ).split()[2],
                    "sunset": convert_timestamp_to_datetime(
                        sunlight.get("sunset"), sunlight.get("sunsetUTCOffset")
                    ).split()[2],
                    "dusk": convert_timestamp_to_datetime(
                        sunlight.get("dusk"), sunlight.get("duskUTCOffset")
                    ).split()[2],
                }
            )

    return grouped_data
