"""
T54 — Model Saving and Loading using Joblib
===========================================
Save and reload full preprocessing+model pipelines with metadata.
Verifies prediction parity after reload to confirm correct serialization.
"""

import json
import logging
import hashlib
from pathlib import Path
from typing import Any
import numpy as np
import joblib
import pandas as pd

logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).parent.parent / "models"


def save_model(pipeline, model_name: str,
               metadata: dict | None = None,
               verify_X: np.ndarray | None = None,
               verify_y: np.ndarray | None = None) -> Path:
    """
    Save a pipeline with joblib and a companion metadata JSON (T54).

    Parameters
    ----------
    pipeline  : sklearn Pipeline to save.
    model_name : Clean name string for filename (e.g. "best_regressor").
    metadata   : Dict with threshold, feature schema, training date, metrics, etc.
    verify_X   : If provided, check reload prediction parity.
    verify_y   : Reference predictions for parity check.

    Returns
    -------
    Path  Path to saved .joblib file.
    """
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = model_name.replace(" ", "_").replace("/", "_")
    model_path = MODELS_DIR / f"{safe_name}.joblib"
    meta_path = MODELS_DIR / f"{safe_name}_metadata.json"

    # Save pipeline
    joblib.dump(pipeline, model_path, compress=3)
    logger.info("Saved model to %s", model_path)

    # Compute file checksum for integrity
    sha = _file_sha256(model_path)

    full_meta = {
        "model_name": model_name,
        "model_file": str(model_path),
        "sha256": sha,
        "saved_at": pd.Timestamp.now().isoformat(),
    }
    if metadata:
        full_meta.update(metadata)

    with open(meta_path, "w") as f:
        json.dump(full_meta, f, indent=2, default=str)
    logger.info("Saved metadata to %s", meta_path)

    # Parity verification
    if verify_X is not None:
        parity = verify_reload(model_path, verify_X,
                               reference_predictions=verify_y)
        full_meta["parity_check"] = parity
        logger.info("Parity check: %s", parity)

    return model_path


def load_model(model_name: str) -> tuple[Any, dict]:
    """
    Load a saved pipeline and its metadata (T54).

    Verifies file checksum against stored SHA-256.

    Returns
    -------
    (pipeline, metadata) tuple.
    """
    safe_name = model_name.replace(" ", "_").replace("/", "_")
    model_path = MODELS_DIR / f"{safe_name}.joblib"
    meta_path = MODELS_DIR / f"{safe_name}_metadata.json"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Model '{model_name}' not found at {model_path}. "
            "Run model training first (scripts/train_models.py)."
        )

    pipeline = joblib.load(model_path)
    logger.info("Loaded model from %s", model_path)

    metadata = {}
    if meta_path.exists():
        with open(meta_path) as f:
            metadata = json.load(f)

        # Integrity check
        current_sha = _file_sha256(model_path)
        stored_sha = metadata.get("sha256", "")
        if stored_sha and current_sha != stored_sha:
            logger.error(
                "CHECKSUM MISMATCH for %s! "
                "Stored: %s  Current: %s. "
                "Model file may have been corrupted or tampered.",
                model_name, stored_sha, current_sha,
            )
            metadata["integrity_ok"] = False
        else:
            metadata["integrity_ok"] = True

    return pipeline, metadata


def verify_reload(model_path: Path, X: np.ndarray,
                   reference_predictions: np.ndarray | None = None,
                   tol: float = 1e-4) -> dict:
    """
    Reload pipeline from disk and verify prediction parity (T54).

    Parameters
    ----------
    X : Feature array (a small validation slice is sufficient).
    reference_predictions : Optional original predictions to compare against.
    tol : Maximum allowed absolute difference per prediction.
    """
    reloaded = joblib.load(model_path)
    new_preds = reloaded.predict(X)

    result = {
        "parity_ok": True,
        "max_diff": 0.0,
        "n_checked": len(new_preds),
    }

    if reference_predictions is not None:
        ref = np.asarray(reference_predictions)
        diffs = np.abs(new_preds - ref[:len(new_preds)])
        max_diff = float(diffs.max()) if len(diffs) > 0 else 0.0
        result["max_diff"] = max_diff
        result["parity_ok"] = bool(max_diff < tol)
        if not result["parity_ok"]:
            logger.error(
                "Reload parity FAILED: max diff=%.6f exceeds tol=%.6f",
                max_diff, tol,
            )

    return result


def save_best_models(training_results: dict,
                     ml_data: dict) -> dict[str, Path]:
    """
    Save the best regression and classification models with full metadata (T54).

    Parameters
    ----------
    training_results : Output from train_all_models().
    ml_data : Output from prepare_ml_data().

    Returns
    -------
    dict mapping "best_regressor" and "best_classifier" to saved paths.
    """
    saved = {}

    # ── Best Regressor ────────────────────────────────────────────────────
    best_reg_name = training_results["regression"]["best_model_name"]
    best_reg_pipeline = training_results["reg_trained"].get(best_reg_name)

    if best_reg_pipeline is None:
        logger.warning("Best regressor pipeline not found; skipping save.")
    else:
        reg_meta = {
            "task": "regression",
            "target": "cnt (hourly rental count)",
            "best_val_metric": "R²",
            "test_metrics": training_results["regression"]["best_model_test_metrics"],
            "feature_schema": ml_data["all_feats"],
            "num_feats": ml_data["num_feats"],
            "cat_feats": ml_data["cat_feats"],
            "bool_feats": ml_data["bool_feats"],
            "split_info": ml_data["split_info"],
            "leakage_excluded": ["casual", "registered", "cnt"],
        }
        # Use a small val slice for parity check
        X_val_slice = ml_data["val_df"][ml_data["all_feats"]].iloc[:50]
        ref_preds = best_reg_pipeline.predict(X_val_slice)
        saved["best_regressor"] = save_model(
            best_reg_pipeline, "best_regressor",
            metadata=reg_meta,
            verify_X=X_val_slice,
            verify_y=ref_preds,
        )

    # ── Best Classifier ───────────────────────────────────────────────────
    best_cls_name = training_results["classification"]["best_model_name"]
    best_cls_pipeline = training_results["cls_trained"].get(best_cls_name)

    if best_cls_pipeline is None:
        logger.warning("Best classifier pipeline not found; skipping save.")
    else:
        cls_meta = {
            "task": "classification",
            "target": "high_demand (binary 0/1)",
            "best_val_metric": "F1",
            "high_demand_threshold": ml_data["high_demand_threshold"],
            "test_metrics": {
                k: v for k, v in
                training_results["classification"]["best_model_test_metrics"].items()
                if k not in {"classification_report", "Confusion_Matrix"}
            },
            "feature_schema": ml_data["all_feats"],
            "num_feats": ml_data["num_feats"],
            "cat_feats": ml_data["cat_feats"],
            "bool_feats": ml_data["bool_feats"],
            "split_info": ml_data["split_info"],
            "leakage_excluded": ["casual", "registered", "cnt"],
        }
        X_val_slice = ml_data["val_df"][ml_data["all_feats"]].iloc[:50]
        ref_preds = best_cls_pipeline.predict(X_val_slice)
        saved["best_classifier"] = save_model(
            best_cls_pipeline, "best_classifier",
            metadata=cls_meta,
            verify_X=X_val_slice,
            verify_y=ref_preds,
        )

    # Save threshold separately for inference
    threshold_path = MODELS_DIR / "high_demand_threshold.json"
    with open(threshold_path, "w") as f:
        json.dump({
            "high_demand_threshold": ml_data["high_demand_threshold"],
            "description": "75th percentile of training cnt. Derived from training data only.",
            "feature_schema": ml_data["all_feats"],
        }, f, indent=2)
    saved["threshold_file"] = threshold_path

    logger.info("Best models saved: %s", list(saved.keys()))
    return saved


def _file_sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def load_threshold() -> float:
    """Load saved high-demand threshold."""
    path = MODELS_DIR / "high_demand_threshold.json"
    if not path.exists():
        raise FileNotFoundError(
            "Threshold file not found. Run model training first."
        )
    with open(path) as f:
        data = json.load(f)
    return float(data["high_demand_threshold"])


def list_saved_models() -> list[str]:
    """List all .joblib model files in the models directory."""
    if not MODELS_DIR.exists():
        return []
    return [p.stem for p in MODELS_DIR.glob("*.joblib")]
