import argparse
from datetime import datetime, timedelta, timezone


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Surf Region Explorer")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Increase output verbosity"
    )
    parser.add_argument("-s", "--search", action="store_true", help="Search for spot")
    parser.add_argument(
        "search_string",
        type=str,
        default=None,
        nargs="?",
        help="An optional string value passed from the CLI",
    )
    parser.add_argument(
        "--days",
        "-d",
        type=int,
        default=3,
        nargs="?",
        help="Number of days to get surf report for.",
    )
    return parser.parse_args()


def sort_regions(regions):
    """Sort list of regions alphabetically."""
    return sorted(regions, key=lambda x: x.name.lower() if hasattr(x, "name") else "")


def convert_timestamp_to_datetime(timestamp, utc_offset):
    """
    Converts a Unix timestamp and UTC offset to a human-readable datetime string.

    Args:
        timestamp (int): The Unix timestamp to convert.
        utc_offset (int): The UTC offset in hours.

    Returns:
        str: The human-readable datetime string in the format %Y-%m-%d %H:%M:%S.
    """
    # Convert the timestamp to a UTC datetime object
    dt = datetime.fromtimestamp(timestamp)

    # Apply the UTC offset to the datetime object
    local_dt = dt.astimezone(timezone(timedelta(hours=utc_offset)))

    # Format the datetime object as a string
    datetime_str = local_dt.strftime("%a %Y-%m-%d %H:%M:%S")

    return datetime_str
