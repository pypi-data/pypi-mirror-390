from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Region:
    """Represents a surf region or taxonomy item."""

    id: str
    name: str
    type: str
    subregion: Optional[str] = None
    spot: Optional[str] = None


@dataclass
class SpotForecast:
    """Represents a surf spot forecast."""

    spot_id: str
    days: int
    forecast_data: dict


@dataclass
class SpotReport:
    """Represents a detailed surf spot report."""

    spot_id: str
    days: int
    report_data: dict


@dataclass
class SurflineSearchResult:
    """Represents a single search result from Surfline."""

    id: str
    name: str
    breadcrumbs: List[str]
    type: str
