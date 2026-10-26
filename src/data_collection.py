"""
T01 + T02 + T03 — Web Scraping, HTML Parsing, Data Collection
=============================================================
Fetches UCI Bike Sharing Dataset metadata via requests + BeautifulSoup.
Falls back to a local cached metadata JSON if network is unavailable.
CSV ingestion is completely separate from web scraping.
"""

import json
import hashlib
import logging
import time
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
UCI_URL = "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset"
CACHE_DIR = Path(__file__).parent.parent / "data" / "raw"
CACHE_FILE = CACHE_DIR / "uci_metadata_cache.json"
HOUR_CSV = CACHE_DIR / "hour.csv"

# Official UCI schema for hour.csv
REQUIRED_COLUMNS = [
    "instant", "dteday", "season", "yr", "mnth", "hr",
    "holiday", "weekday", "workingday", "weathersit",
    "temp", "atemp", "hum", "windspeed",
    "casual", "registered", "cnt",
]

SEASON_MAP = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
WEATHER_MAP = {
    1: "Clear/Partly Cloudy",
    2: "Mist/Cloudy",
    3: "Light Snow/Rain",
    4: "Heavy Rain/Snow+Fog",
}


# ---------------------------------------------------------------------------
# T01 — Web Scraping
# ---------------------------------------------------------------------------
def scrape_uci_metadata(url: str = UCI_URL, timeout: int = 10,
                        use_cache: bool = True) -> dict:
    """
    Fetch UCI page HTML and extract dataset metadata (T01, T02).

    Falls back to local cache if network is unavailable.

    Parameters
    ----------
    url : str
        Public UCI dataset page URL.
    timeout : int
        HTTP request timeout in seconds.
    use_cache : bool
        If True, save result to cache and use cached file on failure.

    Returns
    -------
    dict
        Metadata dict with keys: title, description, variables, source_url,
        fetch_timestamp, from_cache.
    """
    # Try cache first if it exists and network fetch not forced
    if use_cache and CACHE_FILE.exists():
        cached = _load_cache()
        if cached:
            logger.info("Loaded UCI metadata from local cache.")
            cached["from_cache"] = True
            return cached

    metadata = _fetch_and_parse(url, timeout)

    if use_cache and metadata:
        _save_cache(metadata)

    return metadata


def _fetch_and_parse(url: str, timeout: int) -> dict:
    """Perform HTTP GET and parse HTML for metadata (T01, T02)."""
    headers = {
        "User-Agent": (
            "BIKEPULSE-AI-Academic/1.0 "
            "(Educational project; respecting robots.txt)"
        )
    }
    try:
        time.sleep(1)  # polite crawl delay
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        html = resp.text
        logger.info("Successfully fetched UCI page (%d bytes).", len(html))
        return _parse_html(html, url)
    except requests.exceptions.RequestException as exc:
        logger.warning("Network error fetching UCI page: %s", exc)
        # Fallback: try disk cache
        cached = _load_cache()
        if cached:
            cached["from_cache"] = True
            return cached
        # Last resort: return static embedded metadata
        return _static_fallback_metadata(url)


# ---------------------------------------------------------------------------
# T02 — HTML Parsing
# ---------------------------------------------------------------------------
def _parse_html(html: str, source_url: str) -> dict:
    """Extract title, description and variable metadata from UCI HTML (T02)."""
    soup = BeautifulSoup(html, "lxml")

    # Page title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else "UCI Bike Sharing Dataset"

    # Description: look for meta description or first meaningful paragraph
    meta_desc = soup.find("meta", attrs={"name": "description"})
    description = ""
    if meta_desc:
        description = meta_desc.get("content", "")
    if not description:
        # Try the first long paragraph
        for p in soup.find_all("p"):
            text = p.get_text(strip=True)
            if len(text) > 80:
                description = text[:500]
                break

    # Variable names / attributes mentioned in the page
    variables = _extract_variables(soup)

    return {
        "title": title,
        "description": description or "UCI Bike Sharing Dataset — hourly bike rental data 2011-2012.",
        "variables": variables,
        "source_url": source_url,
        "fetch_timestamp": pd.Timestamp.now().isoformat(),
        "from_cache": False,
    }


def _extract_variables(soup: BeautifulSoup) -> list[dict]:
    """Extract variable/attribute metadata listed on the UCI page."""
    variables = []
    # Common patterns: tables, definition lists, or bullet lists
    # Try table rows first
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows:
            cells = [td.get_text(strip=True) for td in row.find_all(["td", "th"])]
            if len(cells) >= 2 and cells[0]:
                variables.append({"name": cells[0], "description": cells[1]})
        if variables:
            break

    # If nothing found from tables, use static known variables
    if not variables:
        variables = _known_variable_metadata()

    return variables


def _known_variable_metadata() -> list[dict]:
    """Return well-known variable descriptions from the UCI readme."""
    return [
        {"name": "instant", "description": "Record index"},
        {"name": "dteday", "description": "Date"},
        {"name": "season", "description": "Season (1:Spring 2:Summer 3:Fall 4:Winter)"},
        {"name": "yr", "description": "Year (0:2011 1:2012)"},
        {"name": "mnth", "description": "Month (1-12)"},
        {"name": "hr", "description": "Hour (0-23)"},
        {"name": "holiday", "description": "Whether day is holiday"},
        {"name": "weekday", "description": "Day of the week (0-6)"},
        {"name": "workingday", "description": "1 if working day else 0"},
        {"name": "weathersit", "description": "Weather situation (1-4)"},
        {"name": "temp", "description": "Normalized temperature / 41 °C"},
        {"name": "atemp", "description": "Normalized feeling temperature / 50 °C"},
        {"name": "hum", "description": "Normalized humidity / 100"},
        {"name": "windspeed", "description": "Normalized wind speed / 67 km/h"},
        {"name": "casual", "description": "Count of casual users"},
        {"name": "registered", "description": "Count of registered users"},
        {"name": "cnt", "description": "Total rental count (casual + registered)"},
    ]


def _static_fallback_metadata(url: str) -> dict:
    """Return hard-coded metadata when network and cache are both unavailable."""
    return {
        "title": "Bike Sharing Dataset — UCI Machine Learning Repository",
        "description": (
            "Bike sharing systems record the duration of travel, departure and "
            "arrival position. Historical hourly logs (2011-2012) from Capital "
            "Bikeshare, Washington D.C., augmented with weather and seasonal data."
        ),
        "variables": _known_variable_metadata(),
        "source_url": url,
        "fetch_timestamp": pd.Timestamp.now().isoformat(),
        "from_cache": True,
        "note": "Static fallback — network and cache unavailable.",
    }


def _save_cache(metadata: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    logger.info("Cached UCI metadata to %s", CACHE_FILE)


def _load_cache() -> dict | None:
    if not CACHE_FILE.exists():
        return None
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as exc:
        logger.warning("Failed to read metadata cache: %s", exc)
        return None


# ---------------------------------------------------------------------------
# T03 — Data Collection / CSV Loading
# ---------------------------------------------------------------------------
def load_hour_csv(path: str | Path = HOUR_CSV) -> pd.DataFrame:
    """
    Load and perform initial validation of the UCI hour.csv file (T03).

    Parameters
    ----------
    path : str | Path
        Path to hour.csv.

    Returns
    -------
    pd.DataFrame
        Raw dataframe with validated schema.

    Raises
    ------
    FileNotFoundError
        If CSV not found at the given path.
    ValueError
        If required columns are missing.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"hour.csv not found at {path}. "
            "Please ensure the UCI Bike Sharing Dataset is in data/raw/."
        )

    df = pd.read_csv(path)
    _validate_schema(df)
    logger.info("Loaded hour.csv: %d rows × %d cols from %s", *df.shape, path)
    return df


def _validate_schema(df: pd.DataFrame) -> None:
    """Confirm required columns are present and cnt = casual + registered."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Audit: cnt must equal casual + registered
    mismatch = df[df["cnt"] != df["casual"] + df["registered"]]
    if not mismatch.empty:
        logger.warning(
            "%d rows where cnt != casual + registered (audit only; not used as feature).",
            len(mismatch),
        )


def compute_checksum(path: str | Path) -> str:
    """Return SHA-256 hex digest of a file for data provenance."""
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def get_data_provenance(path: str | Path = HOUR_CSV) -> dict:
    """Return data provenance information for the raw dataset."""
    path = Path(path)
    return {
        "file": str(path),
        "sha256": compute_checksum(path) if path.exists() else "N/A",
        "source": "UCI Machine Learning Repository — Bike Sharing Dataset",
        "url": "https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset",
        "original_authors": "Hadi Fanaee-T, LIAAD/INESC Porto",
        "years_covered": "2011–2012",
        "system": "Capital Bikeshare, Washington D.C., USA",
        "license": "CC BY 4.0 — cite Fanaee-T & Gama (2013)",
    }
