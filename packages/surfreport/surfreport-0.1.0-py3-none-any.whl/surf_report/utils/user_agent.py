"""
Helpers for determining an up-to-date User-Agent string.
"""

from __future__ import annotations

import html
import os
import re
from typing import Optional

import requests

from surf_report.utils.logger import logger

UA_SOURCE_URL = "https://www.useragents.me/"
UA_FETCH_TIMEOUT = 5
UA_TEXTAREA_PATTERN = re.compile(
    r"<textarea[^>]*class=[\"'][^\"']*\bua-textarea\b[^\"']*[\"'][^>]*>(.*?)</textarea>",
    re.IGNORECASE | re.DOTALL,
)
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
ENV_USER_AGENT = "SURFREPORT_USER_AGENT"

_cached_user_agent: Optional[str] = None


def _fetch_latest_user_agent() -> Optional[str]:
    """Fetch the first user agent entry from useragents.me."""
    try:
        response = requests.get(UA_SOURCE_URL, timeout=UA_FETCH_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.debug("Failed to fetch user agent list: %s", exc)
        return None

    match = UA_TEXTAREA_PATTERN.search(response.text)
    if not match:
        logger.debug("No <textarea> entry found in useragents.me response.")
        return None

    candidate = html.unescape(match.group(1)).strip()
    if not candidate:
        return None
    # Collapse whitespace/newlines
    return re.sub(r"\s+", " ", candidate)


def get_user_agent() -> str:
    """
    Return the preferred User-Agent string.

    Precedence:
        1. SURFREPORT_USER_AGENT environment variable
        2. Cached value fetched from useragents.me
        3. Hard-coded default fallback
    """
    global _cached_user_agent

    env_user_agent = os.environ.get(ENV_USER_AGENT)
    if env_user_agent:
        logger.debug("Using SURFREPORT_USER_AGENT override.")
        return env_user_agent

    if _cached_user_agent:
        return _cached_user_agent

    latest = _fetch_latest_user_agent()
    if latest:
        logger.debug("Fetched latest user agent from useragents.me.")
        _cached_user_agent = latest
    else:
        logger.debug("Falling back to default user agent.")
        _cached_user_agent = DEFAULT_USER_AGENT

    return _cached_user_agent


def clear_cached_user_agent() -> None:
    """Reset cached user agent (useful for tests)."""
    global _cached_user_agent
    _cached_user_agent = None
