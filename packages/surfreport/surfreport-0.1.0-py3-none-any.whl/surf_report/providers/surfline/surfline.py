from enum import Enum
from typing import List, Optional

import requests

from surf_report.providers.surfline.models import (
    Region,
    SpotForecast,
    SpotReport,
    SurflineSearchResult,
)
from surf_report.utils.logger import logger
from surf_report.utils.user_agent import get_user_agent


class Endpoints(Enum):
    TAXONOMY = "https://services.surfline.com/taxonomy"
    REGION_OVERVIEW = "https://services.surfline.com/kbyg/regions/overview"
    SEARCH = "https://services.surfline.com/search/site"
    SPOT_FORECAST = "https://services.surfline.com/kbyg/spots/forecasts/conditions"
    KBYG_BASE = "https://services.surfline.com/kbyg/spots/forecasts"


DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://www.surfline.com",
    "Referer": "https://www.surfline.com/",
    "Connection": "keep-alive",
    "DNT": "1",
}


class SurflineAPI:
    def __init__(self, session: Optional[requests.Session] = None):
        logger.info("Initializing SurflineAPI")
        self.session = session or requests.Session()
        self._configure_session_headers()

    def _configure_session_headers(self) -> None:
        headers = DEFAULT_HEADERS.copy()
        headers["User-Agent"] = get_user_agent()
        self.session.headers.update(headers)

    def _get(self, url: str, params: dict) -> Optional[dict]:
        """A generic GET request handler."""
        try:
            full_url = requests.Request("GET", url, params=params).prepare().url
            logger.debug(f"Requesting {full_url}")
            response = self.session.get(url, params=params)
            response.raise_for_status()
            logger.info(f"Successful API response from {url}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from {url} with params {params}: {e}")
            return None

    def search_surfline(self, query: str) -> List[SurflineSearchResult]:
        """Search for a query on the Surfline API and return structured data."""
        params = {"q": query, "querySize": 5, "suggestionSize": 5}
        data = self._get(Endpoints.SEARCH.value, params)
        if not data or not isinstance(data, list):
            logger.error("Unexpected response format for search_surfline.")
            return []

        # Find the first valid result with "hits"
        valid_hits = []
        for entry in data:
            if (
                "hits" in entry
                and "hits" in entry["hits"]
                and entry["hits"]["total"] > 0
            ):
                valid_hits = entry["hits"]["hits"]
                break  # Stop after finding the first valid result

        if not valid_hits:
            logger.info("No matching surf spots found.")
            return []

        return [
            SurflineSearchResult(
                id=item["_id"],
                name=item["_source"]["name"],
                breadcrumbs=item["_source"].get("breadCrumbs", []),
                type=item["_type"],
            )
            for item in valid_hits
        ]

    def get_region_list(self, taxonomy_id: str, max_depth: int = 0) -> List[Region]:
        """Get a list of regions from the Surfline API and return structured data."""
        params = {"type": "taxonomy", "id": taxonomy_id, "maxDepth": max_depth}
        data = self._get(Endpoints.TAXONOMY.value, params)
        if not data or "contains" not in data:
            logger.error(f"Invalid response data for taxonomy ID {taxonomy_id}")
            return []

        raw_data = data["contains"]
        return [
            Region(
                id=item["_id"],
                name=item["name"],
                type=item["type"],
                subregion=item.get("subregion"),
                spot=item.get("spot"),
            )
            for item in raw_data
        ]

    def get_region_overview(self, region_id: str) -> Optional[dict]:
        """Get the overview of a region."""
        params = {"subregionId": region_id}
        return self._get(Endpoints.REGION_OVERVIEW.value, params)

    def get_spot_forecast(self, spot_id: str, days: int = 5) -> Optional[SpotForecast]:
        """Fetch and return a structured spot forecast."""
        params = {"spotId": spot_id, "days": days}
        data = self._get(Endpoints.SPOT_FORECAST.value, params)
        if data:
            return SpotForecast(spot_id=spot_id, days=days, forecast_data=data)
        return None

    def get_spot_report(
        self, spot_id: str, days: int = 3, interval_hours: int = 6
    ) -> Optional[SpotReport]:
        """
        Fetch and return a structured spot report by iterating over several endpoints.
        """
        endpoints = [
            "/wave",
            "/weather",
            "/tides",
            "/surf",
            "/sunlight",
            "/wind",
            "/swells",
        ]
        params = {"spotId": spot_id, "days": days, "intervalHours": interval_hours}
        report_data = {}

        for endpoint in endpoints:
            url = Endpoints.KBYG_BASE.value + endpoint
            data = self._get(url, params)
            report_data[endpoint.lstrip("/")] = data

        return SpotReport(spot_id=spot_id, days=days, report_data=report_data)
