"""
T56 — User Input-Based Prediction
==================================
Validates user inputs, transforms them with the saved pipeline,
and returns genuine predictions. Never retrains on page load.
"""

import json
import logging
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd

from src.model_persistence import load_model, load_threshold
from src.feature_engineering import add_engineered_features

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"

# Valid UCI ranges (for user input validation)
INPUT_CONSTRAINTS = {
    "season": {"type": int, "min": 1, "max": 4},
    "yr": {"type": int, "min": 0, "max": 1},
    "mnth": {"type": int, "min": 1, "max": 12},
    "hr": {"type": int, "min": 0, "max": 23},
    "holiday": {"type": int, "min": 0, "max": 1},
    "weekday": {"type": int, "min": 0, "max": 6},
    "workingday": {"type": int, "min": 0, "max": 1},
    "weathersit": {"type": int, "min": 1, "max": 4},
    "temp": {"type": float, "min": 0.0, "max": 41.0, "unit": "°C", "normalized_by": 41.0},
    "atemp": {"type": float, "min": 0.0, "max": 50.0, "unit": "°C", "normalized_by": 50.0},
    "hum": {"type": float, "min": 0.0, "max": 100.0, "unit": "%", "normalized_by": 100.0},
    "windspeed": {"type": float, "min": 0.0, "max": 67.0, "unit": "km/h", "normalized_by": 67.0},
}

SEASON_MAP = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
WEATHER_MAP = {
    1: "Clear/Partly Cloudy",
    2: "Mist/Cloudy",
    3: "Light Snow/Rain",
    4: "Heavy Rain/Snow+Fog",
}


def validate_user_input(raw_inputs: dict) -> tuple[dict, list[str]]:
    """
    Validate user-provided inputs against documented UCI ranges.

    Parameters
    ----------
    raw_inputs : dict  Keys matching UCI column names, values in human units.
                      Temperatures in °C, humidity in %, wind in km/h.

    Returns
    -------
    (validated_inputs, errors) where errors is empty if all OK.
    """
    validated = {}
    errors = []

    for col, constraint in INPUT_CONSTRAINTS.items():
        if col not in raw_inputs:
            errors.append(f"Missing required input: '{col}'")
            continue

        val = raw_inputs[col]
        try:
            val = constraint["type"](val)
        except (ValueError, TypeError):
            errors.append(f"'{col}' must be {constraint['type'].__name__}, got {raw_inputs[col]!r}.")
            continue

        lo, hi = constraint["min"], constraint["max"]
        if val < lo or val > hi:
            unit = constraint.get("unit", "")
            errors.append(f"'{col}' = {val} {unit} out of range [{lo}, {hi}].")
            continue

        validated[col] = val

    # Cross-field validation
    if "workingday" in validated and "holiday" in validated and "weekday" in validated:
        if validated["holiday"] == 1 and validated["workingday"] == 1:
            errors.append("'workingday' cannot be 1 when 'holiday' is 1.")

    return validated, errors


def transform_user_input(validated: dict) -> pd.DataFrame:
    """
    Convert validated human-unit inputs to UCI normalized values
    and construct a single-row DataFrame for model prediction.

    UCI normalizations (from Readme.txt):
      temp / 41, atemp / 50, hum / 100, windspeed / 67
    """
    row = validated.copy()

    # Normalize continuous variables to match training representation
    row["temp"] = row["temp"] / 41.0
    row["atemp"] = row["atemp"] / 50.0
    row["hum"] = row["hum"] / 100.0
    row["windspeed"] = row["windspeed"] / 67.0

    # Add dteday placeholder (not used as feature, needed for add_engineered_features)
    row["dteday"] = pd.Timestamp("2012-01-01")

    df_row = pd.DataFrame([row])
    df_row = add_engineered_features(df_row)
    return df_row


def predict_demand(validated_inputs: dict) -> dict[str, Any]:
    """
    Run prediction using saved best models (T56).

    Loads pipeline from disk (never retrains on inference).
    Returns rental count forecast and high-demand category.

    Parameters
    ----------
    validated_inputs : dict  Already validated, in human units (°C, %, km/h).

    Returns
    -------
    dict with predicted_count, demand_category, confidence_note, model_provenance.
    """
    # Load models (from saved .joblib files)
    try:
        reg_pipeline, reg_meta = load_model("best_regressor")
        cls_pipeline, cls_meta = load_model("best_classifier")
        threshold = load_threshold()
    except FileNotFoundError as e:
        return {
            "error": str(e),
            "suggestion": "Please run model training first from the Model Training page.",
        }

    # Build feature row
    df_row = transform_user_input(validated_inputs)
    feature_cols = reg_meta.get("feature_schema", [])

    # Ensure all required columns are present
    missing_cols = [c for c in feature_cols if c not in df_row.columns]
    if missing_cols:
        return {
            "error": f"Missing engineered features after transform: {missing_cols}",
            "suggestion": "Check that add_engineered_features is up to date.",
        }

    X_input = df_row[feature_cols]

    # Regression prediction
    try:
        predicted_count = float(reg_pipeline.predict(X_input)[0])
        predicted_count = max(0.0, round(predicted_count, 1))
    except Exception as exc:
        return {"error": f"Regression prediction failed: {exc}"}

    # Classification prediction
    try:
        cls_pred = int(cls_pipeline.predict(X_input)[0])
        demand_label = "High Demand" if cls_pred == 1 else "Low/Normal Demand"
        # Probability if available
        prob = None
        if hasattr(cls_pipeline, "predict_proba"):
            proba = cls_pipeline.predict_proba(X_input)[0]
            prob = float(proba[1])
    except Exception as exc:
        return {"error": f"Classification prediction failed: {exc}"}

    season_desc = SEASON_MAP.get(validated_inputs.get("season", 0), "Unknown")
    weather_desc = WEATHER_MAP.get(validated_inputs.get("weathersit", 0), "Unknown")

    return {
        "predicted_count": predicted_count,
        "demand_category": demand_label,
        "high_demand_probability": round(prob, 4) if prob is not None else "N/A",
        "high_demand_threshold": round(threshold, 1),
        "season": season_desc,
        "weather": weather_desc,
        "hour": validated_inputs.get("hr"),
        "is_working_day": bool(validated_inputs.get("workingday", 0)),
        "regressor_used": reg_meta.get("model_name", "best_regressor"),
        "classifier_used": cls_meta.get("model_name", "best_classifier"),
        "regressor_test_r2": reg_meta.get("test_metrics", {}).get("R2", "N/A"),
        "classifier_test_f1": cls_meta.get("test_metrics", {}).get("F1", "N/A"),
        "model_trained_on": reg_meta.get("split_info", {}).get("train_start", "N/A"),
        "note": (
            "Predictions based on 2011-2012 Capital Bikeshare data. "
            "Do not interpret as real-time demand forecasts. "
            "Models loaded from saved .joblib artifacts — not retrained on this request."
        ),
    }
