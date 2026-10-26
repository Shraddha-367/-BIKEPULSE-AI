"""
T04 + T05 — Data Cleaning and Preprocessing / Missing & Duplicate Handling
===========================================================================
Provides a fully validated, chronologically ordered, type-correct
cleaned DataFrame ready for downstream EDA and modelling.
"""

import logging
from pathlib import Path
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Official UCI normalisation denominators (from Readme.txt)
# ---------------------------------------------------------------------------
TEMP_MAX = 41.0      # degrees Celsius
ATEMP_MAX = 50.0     # degrees Celsius (feeling temperature)
HUM_MAX = 100.0      # percent
WIND_MAX = 67.0      # km/h

SEASON_MAP = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
WEATHER_MAP = {
    1: "Clear/Partly Cloudy",
    2: "Mist/Cloudy",
    3: "Light Snow/Rain",
    4: "Heavy Rain/Snow+Fog",
}

NUMERIC_COLS = ["temp", "atemp", "hum", "windspeed", "cnt", "casual", "registered"]
CATEGORICAL_COLS = ["season", "yr", "mnth", "hr", "holiday", "weekday", "workingday", "weathersit"]


# ---------------------------------------------------------------------------
# T04 — Cleaning Pipeline
# ---------------------------------------------------------------------------
def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Full data cleaning pipeline (T04).

    Steps:
    1. Drop non-feature index column.
    2. Parse dteday to datetime.
    3. Construct a proper datetime_hour column.
    4. Cast integer categoricals.
    5. Validate numeric ranges.
    6. Handle missing values and duplicates (T05).

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataframe from load_hour_csv().

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe sorted chronologically by datetime_hour.
    """
    df = df.copy()

    # -- Step 1: parse date
    df["dteday"] = pd.to_datetime(df["dteday"], format="%Y-%m-%d", errors="coerce")
    invalid_dates = df["dteday"].isna().sum()
    if invalid_dates:
        logger.warning("Found %d rows with unparseable dates — dropping.", invalid_dates)
        df = df.dropna(subset=["dteday"])

    # -- Step 2: construct chronological datetime_hour
    df["datetime_hour"] = df["dteday"] + pd.to_timedelta(df["hr"], unit="h")
    df = df.sort_values("datetime_hour").reset_index(drop=True)

    # -- Step 3: integer cast for categoricals
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # -- Step 4: validate numeric ranges
    df = _validate_ranges(df)

    # -- Step 5: missing / duplicate handling (T05)
    audit = run_missing_duplicate_audit(df)
    df = _handle_missing(df, audit)
    df = _handle_duplicates(df)

    # -- Step 6: derive decoded columns for human-readable display
    df["season_label"] = df["season"].map(SEASON_MAP)
    df["weather_label"] = df["weathersit"].map(WEATHER_MAP)
    df["temp_celsius"] = (df["temp"] * TEMP_MAX).round(2)
    df["atemp_celsius"] = (df["atemp"] * ATEMP_MAX).round(2)
    df["hum_percent"] = (df["hum"] * HUM_MAX).round(2)
    df["windspeed_kmh"] = (df["windspeed"] * WIND_MAX).round(2)

    logger.info("Cleaning complete. Final shape: %s", df.shape)
    return df


def _validate_ranges(df: pd.DataFrame) -> pd.DataFrame:
    """Clip/flag values outside official documented ranges."""
    clipping = {
        "temp": (0.0, 1.0),
        "atemp": (0.0, 1.0),
        "hum": (0.0, 1.0),
        "windspeed": (0.0, 1.0),
        "hr": (0, 23),
        "mnth": (1, 12),
        "season": (1, 4),
        "weathersit": (1, 4),
        "cnt": (0, None),
        "casual": (0, None),
        "registered": (0, None),
    }
    for col, (lo, hi) in clipping.items():
        if col not in df.columns:
            continue
        out_lo = (df[col] < lo).sum() if lo is not None else 0
        out_hi = (df[col] > hi).sum() if hi is not None else 0
        if out_lo + out_hi > 0:
            logger.warning(
                "Column '%s': %d values out of range [%s, %s] — clipping.",
                col, out_lo + out_hi, lo, hi,
            )
            df[col] = df[col].clip(lower=lo, upper=hi)
    return df


# ---------------------------------------------------------------------------
# T05 — Missing Values & Duplicate Handling
# ---------------------------------------------------------------------------
def run_missing_duplicate_audit(df: pd.DataFrame) -> dict:
    """
    Audit missing values and duplicates (T05).

    Returns
    -------
    dict
        Audit report with missing_counts, duplicate_count, policy notes.
    """
    missing_counts = df.isnull().sum()
    missing_pct = (missing_counts / len(df) * 100).round(2)

    # Duplicates: rows where dteday + hr are identical
    dup_mask = df.duplicated(subset=["dteday", "hr"], keep="first")
    dup_count = dup_mask.sum()

    # Count = casual + registered mismatch audit
    cnt_mismatch = (df["cnt"] != df["casual"] + df["registered"]).sum()

    report = {
        "total_rows": len(df),
        "missing_counts": missing_counts[missing_counts > 0].to_dict(),
        "missing_pct": missing_pct[missing_pct > 0].to_dict(),
        "duplicate_rows": int(dup_count),
        "cnt_mismatch_rows": int(cnt_mismatch),
        "policy": {
            "missing": "Forward-fill for numeric; mode for categorical; drop if dteday missing.",
            "duplicates": "Keep first occurrence per (dteday, hr) pair.",
        },
    }
    logger.info(
        "Audit — missing cols: %d, duplicate rows: %d",
        len(report["missing_counts"]),
        dup_count,
    )
    return report


def inject_synthetic_issues(df: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """
    Inject controlled missing values and duplicates for testing purposes.
    Clearly labelled as a test fixture — never silently mixed with real data.
    """
    rng = np.random.default_rng(seed)
    corrupted = df.copy()
    n = len(corrupted)

    # Inject 5 missing values in temp column
    idx_missing = rng.choice(n, size=5, replace=False)
    corrupted.loc[idx_missing, "temp"] = np.nan

    # Inject 3 duplicate rows
    dup_rows = corrupted.iloc[rng.choice(n, size=3, replace=False)].copy()
    corrupted = pd.concat([corrupted, dup_rows], ignore_index=True)

    corrupted.attrs["is_synthetic_fixture"] = True
    return corrupted


def _handle_missing(df: pd.DataFrame, audit: dict) -> pd.DataFrame:
    """Forward-fill numeric; mode-fill categorical; drop if dteday missing."""
    if not audit["missing_counts"]:
        return df

    numeric_missing = [c for c in audit["missing_counts"] if c in NUMERIC_COLS]
    cat_missing = [c for c in audit["missing_counts"] if c in CATEGORICAL_COLS]

    if numeric_missing:
        df[numeric_missing] = df[numeric_missing].ffill().bfill()

    for col in cat_missing:
        mode_val = df[col].mode()
        if not mode_val.empty:
            df[col] = df[col].fillna(mode_val.iloc[0])

    # Drop any remaining rows with missing dteday or hr
    df = df.dropna(subset=["dteday", "hr"])
    return df


def _handle_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop duplicate (dteday, hr) rows, keeping first."""
    before = len(df)
    df = df.drop_duplicates(subset=["dteday", "hr"], keep="first").reset_index(drop=True)
    removed = before - len(df)
    if removed:
        logger.info("Removed %d duplicate (dteday, hr) rows.", removed)
    return df


# ---------------------------------------------------------------------------
# Export cleaned CSV
# ---------------------------------------------------------------------------
def export_cleaned_csv(df: pd.DataFrame,
                       output_path: str | Path = None) -> Path:
    """Export the cleaned dataframe to data/processed/hour_clean.csv."""
    if output_path is None:
        output_path = Path(__file__).parent.parent / "data" / "processed" / "hour_clean.csv"
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info("Exported cleaned CSV to %s (%d rows).", output_path, len(df))
    return output_path


def load_cleaned_csv(path: str | Path = None) -> pd.DataFrame:
    """Load previously exported cleaned CSV."""
    if path is None:
        path = Path(__file__).parent.parent / "data" / "processed" / "hour_clean.csv"
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Cleaned CSV not found at {path}. Run preprocessing first.")
    df = pd.read_csv(path, parse_dates=["dteday", "datetime_hour"])
    return df
