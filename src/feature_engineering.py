"""
T33 + T34 + T35 + T36 + T37 + T38 — Feature Engineering
==========================================================
Min-Max normalization, Z-score standardization, label encoding,
one-hot encoding, feature selection and chronological train/val/test split.
ALL preprocessing fitted on TRAINING DATA ONLY to prevent leakage.
"""

import json
import logging
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from sklearn.preprocessing import (
    MinMaxScaler, StandardScaler, LabelEncoder, OneHotEncoder
)
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectKBest, f_regression

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Feature definitions — no leakage from target components
# ---------------------------------------------------------------------------
# DO NOT include: casual, registered (cnt = casual + registered)
# instant is a row index — not a predictor
LEAKAGE_COLS = {"instant", "casual", "registered", "cnt", "high_demand"}
PASSTHROUGH_COLS = {"dteday", "datetime_hour", "season_label", "weather_label",
                    "temp_celsius", "atemp_celsius", "hum_percent", "windspeed_kmh"}

NUMERIC_FEATURES = ["temp", "atemp", "hum", "windspeed", "hr", "mnth"]
CATEGORICAL_FEATURES = ["season", "weathersit", "weekday"]
BOOL_FEATURES = ["holiday", "workingday", "yr"]

ALL_MODEL_FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES + BOOL_FEATURES

# Engineered time features (derived BEFORE split, no leakage)
def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived time/weather features (T37).

    All features derivable from existing columns without using target.
    """
    df = df.copy()
    # Hour categories
    df["is_rush_hour"] = df["hr"].isin([7, 8, 9, 17, 18, 19]).astype(int)
    df["is_night"] = df["hr"].isin(list(range(0, 6)) + list(range(22, 24))).astype(int)
    df["is_afternoon"] = df["hr"].isin(range(12, 17)).astype(int)

    # Cyclic encoding of hour (to capture periodicity)
    df["hr_sin"] = np.sin(2 * np.pi * df["hr"] / 24)
    df["hr_cos"] = np.cos(2 * np.pi * df["hr"] / 24)

    # Cyclic encoding of month
    df["mnth_sin"] = np.sin(2 * np.pi * df["mnth"] / 12)
    df["mnth_cos"] = np.cos(2 * np.pi * df["mnth"] / 12)

    # Temperature-humidity interaction
    df["temp_hum_interaction"] = df["temp"] * df["hum"]

    # Weekend flag
    df["is_weekend"] = (df["weekday"].isin([0, 6])).astype(int)

    return df


# ---------------------------------------------------------------------------
# T38 — Chronological Train / Validation / Test Split (70/15/15)
# ---------------------------------------------------------------------------
def chronological_split(df: pd.DataFrame,
                         train_frac: float = 0.70,
                         val_frac: float = 0.15) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Strictly chronological split — NO shuffling (T38).

    Records boundary dates in returned DataFrames' attrs.
    """
    n = len(df)
    train_end = int(n * train_frac)
    val_end = train_end + int(n * val_frac)

    train = df.iloc[:train_end].copy()
    val = df.iloc[train_end:val_end].copy()
    test = df.iloc[val_end:].copy()

    for split, name in [(train, "train"), (val, "val"), (test, "test")]:
        if "datetime_hour" in split.columns:
            split.attrs["start"] = str(split["datetime_hour"].min())
            split.attrs["end"] = str(split["datetime_hour"].max())
        split.attrs["split"] = name
        split.attrs["n"] = len(split)
        logger.info("Split %s: %d rows", name, len(split))

    logger.info(
        "Chronological split — train: %d, val: %d, test: %d",
        len(train), len(val), len(test),
    )
    return train, val, test


# ---------------------------------------------------------------------------
# T35 — Label Encoding
# ---------------------------------------------------------------------------
def encode_target(train: pd.DataFrame, threshold: float | None = None,
                  target_col: str = "cnt") -> tuple[pd.Series, pd.Series, float, LabelEncoder]:
    """
    Create binary high-demand label using TRAINING DATA percentile only (T35).

    Returns
    -------
    y_binary : pd.Series  Binary labels {0, 1}.
    threshold : float  Threshold used.
    le : LabelEncoder  Fitted encoder.
    """
    if threshold is None:
        threshold = float(np.percentile(train[target_col], 75))
        logger.info("High-demand threshold: %.1f (75th pct of training cnt).", threshold)

    binary = (train[target_col] >= threshold).astype(int)
    le = LabelEncoder()
    le.fit(binary)
    y_encoded = pd.Series(le.transform(binary), index=train.index, name="high_demand")
    return y_encoded, threshold, le


def apply_target_label(df: pd.DataFrame, threshold: float,
                        target_col: str = "cnt") -> pd.Series:
    """Apply pre-fitted threshold to any split (val/test/inference)."""
    return ((df[target_col] >= threshold).astype(int)
            .rename("high_demand"))


# ---------------------------------------------------------------------------
# T33 + T34 + T36 — Preprocessing Pipeline Builder
# ---------------------------------------------------------------------------
def build_preprocessor(numeric_features: list[str] | None = None,
                        categorical_features: list[str] | None = None,
                        bool_features: list[str] | None = None,
                        scaler_type: str = "standard") -> ColumnTransformer:
    """
    Build a ColumnTransformer with:
    - StandardScaler or MinMaxScaler for numeric (T33/T34).
    - OneHotEncoder(handle_unknown="ignore") for categoricals (T36).
    - Passthrough for boolean features.

    scaler_type : "standard" | "minmax"
    """
    if numeric_features is None:
        numeric_features = NUMERIC_FEATURES
    if categorical_features is None:
        categorical_features = CATEGORICAL_FEATURES
    if bool_features is None:
        bool_features = BOOL_FEATURES

    scaler = StandardScaler() if scaler_type == "standard" else MinMaxScaler()

    transformers = [
        ("num", scaler, numeric_features),
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            categorical_features,
        ),
        ("bool", "passthrough", bool_features),
    ]
    return ColumnTransformer(transformers=transformers, remainder="drop")


def get_feature_names_after_transform(preprocessor: ColumnTransformer,
                                       numeric_features: list[str],
                                       categorical_features: list[str],
                                       bool_features: list[str]) -> list[str]:
    """Return ordered feature names after ColumnTransformer transform."""
    cat_encoder = preprocessor.named_transformers_["cat"]
    ohe_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
    return numeric_features + ohe_names + bool_features


# ---------------------------------------------------------------------------
# T37 — Feature Selection (on training data only)
# ---------------------------------------------------------------------------
def select_features_kbest(X_train: np.ndarray, y_train: np.ndarray,
                           feature_names: list[str],
                           k: int = 15) -> tuple[SelectKBest, list[str]]:
    """
    Select top-k features using f_regression on TRAINING DATA only (T37).

    Returns
    -------
    selector : SelectKBest  Fitted selector.
    selected_names : list[str]  Names of selected features.
    """
    selector = SelectKBest(score_func=f_regression, k=min(k, X_train.shape[1]))
    selector.fit(X_train, y_train)
    mask = selector.get_support()
    selected = [name for name, sel in zip(feature_names, mask) if sel]
    logger.info("Feature selection: %d → %d features.", X_train.shape[1], len(selected))
    return selector, selected


# ---------------------------------------------------------------------------
# Leakage Audit
# ---------------------------------------------------------------------------
def leakage_audit(feature_cols: list[str]) -> dict[str, Any]:
    """Verify no leakage columns appear in the feature set."""
    leaked = [c for c in feature_cols if c in LEAKAGE_COLS]
    return {
        "leakage_detected": len(leaked) > 0,
        "leaked_columns": leaked,
        "note": (
            "casual, registered, cnt (target) must never be in X. "
            "instant is a row index and should not be in X."
        ),
    }


# ---------------------------------------------------------------------------
# Full ML Data Preparation Pipeline
# ---------------------------------------------------------------------------
def prepare_ml_data(df: pd.DataFrame,
                    add_engineered: bool = True,
                    scaler_type: str = "standard") -> dict[str, Any]:
    """
    End-to-end ML data preparation returning fitted preprocessor, splits and labels.

    This function is the single entrypoint used by model training to ensure
    no leakage: all preprocessing is fit on training data only.
    """
    # Add engineered features
    if add_engineered:
        df = add_engineered_features(df)

    # Chronological split
    train_df, val_df, test_df = chronological_split(df)

    # Regression target
    y_train_reg = train_df["cnt"].reset_index(drop=True)
    y_val_reg = val_df["cnt"].reset_index(drop=True)
    y_test_reg = test_df["cnt"].reset_index(drop=True)

    # Classification target — threshold from training only
    y_train_cls, threshold, le = encode_target(train_df)
    y_val_cls = apply_target_label(val_df, threshold)
    y_test_cls = apply_target_label(test_df, threshold)

    # Determine feature columns
    engineered_numeric = []
    engineered_bool = []
    if add_engineered:
        engineered_numeric = ["hr_sin", "hr_cos", "mnth_sin", "mnth_cos",
                              "temp_hum_interaction"]
        engineered_bool = ["is_rush_hour", "is_night", "is_afternoon", "is_weekend"]

    num_feats = NUMERIC_FEATURES + engineered_numeric
    cat_feats = CATEGORICAL_FEATURES
    bool_feats = BOOL_FEATURES + engineered_bool

    # Verify leakage
    all_feats = num_feats + cat_feats + bool_feats
    audit = leakage_audit(all_feats)
    if audit["leakage_detected"]:
        raise ValueError(f"LEAKAGE DETECTED: {audit['leaked_columns']}")

    # Build preprocessor — fit on TRAINING only
    preprocessor = build_preprocessor(num_feats, cat_feats, bool_feats, scaler_type)

    X_train_raw = train_df[all_feats]
    X_val_raw = val_df[all_feats]
    X_test_raw = test_df[all_feats]

    X_train = preprocessor.fit_transform(X_train_raw, y_train_reg)
    X_val = preprocessor.transform(X_val_raw)
    X_test = preprocessor.transform(X_test_raw)

    feature_names = get_feature_names_after_transform(
        preprocessor, num_feats, cat_feats, bool_feats
    )

    return {
        "preprocessor": preprocessor,
        "feature_names": feature_names,
        "X_train": X_train, "y_train_reg": y_train_reg.values,
        "X_val": X_val,   "y_val_reg": y_val_reg.values,
        "X_test": X_test,  "y_test_reg": y_test_reg.values,
        "y_train_cls": y_train_cls.values,
        "y_val_cls": y_val_cls.values,
        "y_test_cls": y_test_cls.values,
        "high_demand_threshold": threshold,
        "label_encoder": le,
        "train_df": train_df,
        "val_df": val_df,
        "test_df": test_df,
        "num_feats": num_feats,
        "cat_feats": cat_feats,
        "bool_feats": bool_feats,
        "all_feats": all_feats,
        "split_info": {
            "train_n": len(train_df),
            "val_n": len(val_df),
            "test_n": len(test_df),
            "train_start": str(train_df["datetime_hour"].min()) if "datetime_hour" in train_df.columns else "N/A",
            "train_end": str(train_df["datetime_hour"].max()) if "datetime_hour" in train_df.columns else "N/A",
            "val_start": str(val_df["datetime_hour"].min()) if "datetime_hour" in val_df.columns else "N/A",
            "val_end": str(val_df["datetime_hour"].max()) if "datetime_hour" in val_df.columns else "N/A",
            "test_start": str(test_df["datetime_hour"].min()) if "datetime_hour" in test_df.columns else "N/A",
            "test_end": str(test_df["datetime_hour"].max()) if "datetime_hour" in test_df.columns else "N/A",
        },
    }
