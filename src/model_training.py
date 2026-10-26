"""
T52 + T53 — Model Training and Best Model Selection
=====================================================
Trains all 6 regressors and 5 classifiers on matched chronological splits.
Best model selected on VALIDATION metrics only; test used once at the end.
"""

import json
import logging
from pathlib import Path
from typing import Any
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from src.feature_engineering import prepare_ml_data, build_preprocessor
from src.regression_models import get_all_regression_pipelines, build_simple_linear_regression
from src.classification_models import get_all_classification_pipelines
from src.model_evaluation import (
    evaluate_regression, evaluate_classification,
    compare_regression_results, compare_classification_results,
)

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"
EVAL_DIR = Path(__file__).parent.parent / "reports" / "evaluation"


def train_all_models(df: pd.DataFrame) -> dict[str, Any]:
    """
    Train all 11 models on chronological splits and return full results (T52, T53).

    Parameters
    ----------
    df : pd.DataFrame  Cleaned dataframe from preprocessing.

    Returns
    -------
    dict with regression/classification results, best models, data splits.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    EVAL_DIR.mkdir(parents=True, exist_ok=True)

    # ── Prepare ML data (fit preprocessing on train only) ─────────────────
    logger.info("Preparing ML data...")
    ml_data = prepare_ml_data(df)

    # ── Simple Linear Regression: temp-only ───────────────────────────────
    # Needs its own single-feature preprocessor (MinMaxScaler on temp only)
    from sklearn.preprocessing import StandardScaler as SS
    from sklearn.pipeline import Pipeline as P
    from sklearn.linear_model import LinearRegression

    temp_scaler = SS()
    X_train_temp = temp_scaler.fit_transform(
        ml_data["train_df"][["temp"]]
    )
    X_val_temp = temp_scaler.transform(ml_data["val_df"][["temp"]])
    X_test_temp = temp_scaler.transform(ml_data["test_df"][["temp"]])

    slr_model = LinearRegression()
    slr_model.fit(X_train_temp, ml_data["y_train_reg"])

    # ── Preprocessor for multi-feature models ─────────────────────────────
    preprocessor = ml_data["preprocessor"]

    # ── Regression Models ─────────────────────────────────────────────────
    logger.info("Training regression models...")
    reg_pipelines = get_all_regression_pipelines(preprocessor)

    reg_val_results = []
    reg_test_results = []
    reg_trained = {}

    for name, pipeline in reg_pipelines.items():
        logger.info("  Fitting %s ...", name)
        if "Simple Linear" in name:
            # Use the pre-fitted slr_model
            y_val_pred = slr_model.predict(X_val_temp)
            y_test_pred = slr_model.predict(X_test_temp)
            reg_trained[name] = slr_model
            reg_trained[f"{name}__scaler"] = temp_scaler
        else:
            pipeline.fit(
                ml_data["train_df"][ml_data["all_feats"]],
                ml_data["y_train_reg"],
            )
            y_val_pred = pipeline.predict(ml_data["val_df"][ml_data["all_feats"]])
            y_test_pred = pipeline.predict(ml_data["test_df"][ml_data["all_feats"]])
            reg_trained[name] = pipeline

        val_metrics = evaluate_regression(ml_data["y_val_reg"], y_val_pred, name)
        test_metrics = evaluate_regression(ml_data["y_test_reg"], y_test_pred, name)
        val_metrics["split"] = "validation"
        test_metrics["split"] = "test"
        reg_val_results.append(val_metrics)
        reg_test_results.append(test_metrics)

    # ── Select best regressor on VALIDATION R² (T53) ─────────────────────
    reg_val_df = compare_regression_results(reg_val_results)
    best_reg_name = reg_val_df.iloc[0]["model"]
    logger.info("Best regressor (by val R²): %s", best_reg_name)

    # Final test score for the best model
    best_reg_test = next(r for r in reg_test_results if r["model"] == best_reg_name)

    # ── Classification Models ─────────────────────────────────────────────
    logger.info("Training classification models...")
    # Rebuild preprocessor for classifiers (must refit fresh — do not share fitted state)
    cls_preprocessor = build_preprocessor(
        ml_data["num_feats"], ml_data["cat_feats"], ml_data["bool_feats"]
    )
    cls_pipelines = get_all_classification_pipelines(cls_preprocessor)

    cls_val_results = []
    cls_test_results = []
    cls_trained = {}

    for name, pipeline in cls_pipelines.items():
        logger.info("  Fitting %s ...", name)
        pipeline.fit(
            ml_data["train_df"][ml_data["all_feats"]],
            ml_data["y_train_cls"],
        )
        y_val_pred = pipeline.predict(ml_data["val_df"][ml_data["all_feats"]])
        y_test_pred = pipeline.predict(ml_data["test_df"][ml_data["all_feats"]])
        cls_trained[name] = pipeline

        val_metrics = evaluate_classification(ml_data["y_val_cls"], y_val_pred, name)
        test_metrics = evaluate_classification(ml_data["y_test_cls"], y_test_pred, name)
        val_metrics["split"] = "validation"
        test_metrics["split"] = "test"
        cls_val_results.append(val_metrics)
        cls_test_results.append(test_metrics)

    # ── Select best classifier on VALIDATION F1 (T53) ────────────────────
    cls_val_df = compare_classification_results(cls_val_results)
    best_cls_name = cls_val_df.iloc[0]["model"]
    logger.info("Best classifier (by val F1): %s", best_cls_name)

    best_cls_test = next(r for r in cls_test_results if r["model"] == best_cls_name)

    # ── Save evaluation results ───────────────────────────────────────────
    results = {
        "regression": {
            "val_results": reg_val_results,
            "test_results": reg_test_results,
            "best_model_name": best_reg_name,
            "best_model_test_metrics": best_reg_test,
        },
        "classification": {
            "val_results": cls_val_results,
            "test_results": cls_test_results,
            "best_model_name": best_cls_name,
            "best_model_test_metrics": best_cls_test,
        },
        "ml_data": ml_data,
        "reg_trained": reg_trained,
        "cls_trained": cls_trained,
    }

    # Save JSON summaries (serialisable subset)
    _save_eval_summaries(results)

    return results


def _save_eval_summaries(results: dict) -> None:
    """Save serialisable evaluation summaries to JSON."""
    reg_summary = {
        "best_model": results["regression"]["best_model_name"],
        "best_test_metrics": results["regression"]["best_model_test_metrics"],
        "all_val_results": [
            {k: v for k, v in r.items()
             if k in {"model", "MAE", "MSE", "RMSE", "R2", "n", "split"}}
            for r in results["regression"]["val_results"]
        ],
        "all_test_results": [
            {k: v for k, v in r.items()
             if k in {"model", "MAE", "MSE", "RMSE", "R2", "n", "split"}}
            for r in results["regression"]["test_results"]
        ],
    }
    cls_summary = {
        "best_model": results["classification"]["best_model_name"],
        "best_test_metrics": {
            k: v for k, v in results["classification"]["best_model_test_metrics"].items()
            if k not in {"classification_report", "Confusion_Matrix"}
        },
        "all_val_results": [
            {k: v for k, v in r.items()
             if k in {"model", "Accuracy", "Precision", "Recall", "F1", "n", "split"}}
            for r in results["classification"]["val_results"]
        ],
        "all_test_results": [
            {k: v for k, v in r.items()
             if k in {"model", "Accuracy", "Precision", "Recall", "F1", "n", "split"}}
            for r in results["classification"]["test_results"]
        ],
    }
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    with open(EVAL_DIR / "regression_results.json", "w") as f:
        json.dump(reg_summary, f, indent=2)
    with open(EVAL_DIR / "classification_results.json", "w") as f:
        json.dump(cls_summary, f, indent=2)
    logger.info("Evaluation summaries saved to %s", EVAL_DIR)
