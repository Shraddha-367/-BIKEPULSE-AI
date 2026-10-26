"""
T45 + T51 — Model Evaluation
==============================
Regression: MAE, MSE, RMSE, R²
Classification: Accuracy, Precision, Recall, F1, Confusion Matrix
All computed on genuine held-out data; no hardcoded metrics.
"""

import logging
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# T45 — Regression Evaluation
# ---------------------------------------------------------------------------
def evaluate_regression(y_true: np.ndarray,
                         y_pred: np.ndarray,
                         model_name: str = "Model") -> dict:
    """
    Compute MAE, MSE, RMSE, R² for regression predictions (T45).

    Parameters
    ----------
    y_true : actual values (held-out split).
    y_pred : predicted values.
    model_name : display name for the model.
    """
    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))

    logger.info("%s → MAE=%.2f, RMSE=%.2f, R²=%.4f", model_name, mae, rmse, r2)
    return {
        "model": model_name,
        "MAE": round(mae, 4),
        "MSE": round(mse, 4),
        "RMSE": round(rmse, 4),
        "R2": round(r2, 4),
        "n": int(len(y_true)),
    }


def compare_regression_results(results: list[dict]) -> pd.DataFrame:
    """Sort and display regression model comparison table."""
    df = pd.DataFrame(results)
    df = df.sort_values("R2", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df


# ---------------------------------------------------------------------------
# T51 — Classification Evaluation
# ---------------------------------------------------------------------------
def evaluate_classification(y_true: np.ndarray,
                              y_pred: np.ndarray,
                              model_name: str = "Model",
                              positive_label: int = 1) -> dict:
    """
    Compute Accuracy, Precision, Recall, F1 and Confusion Matrix (T51).

    Parameters
    ----------
    y_true : actual class labels.
    y_pred : predicted class labels.
    positive_label : the positive class value.
    """
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, pos_label=positive_label,
                                  zero_division=0))
    rec = float(recall_score(y_true, y_pred, pos_label=positive_label,
                              zero_division=0))
    f1 = float(f1_score(y_true, y_pred, pos_label=positive_label,
                         zero_division=0))
    cm = confusion_matrix(y_true, y_pred).tolist()
    report = classification_report(y_true, y_pred, zero_division=0, output_dict=True)

    # Class distribution
    unique, counts = np.unique(y_true, return_counts=True)
    class_dist = {int(k): int(v) for k, v in zip(unique, counts)}

    logger.info(
        "%s → Acc=%.4f, Prec=%.4f, Rec=%.4f, F1=%.4f",
        model_name, acc, prec, rec, f1,
    )
    return {
        "model": model_name,
        "Accuracy": round(acc, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1": round(f1, 4),
        "Confusion_Matrix": cm,
        "class_distribution": class_dist,
        "positive_label": positive_label,
        "classification_report": report,
        "n": int(len(y_true)),
    }


def compare_classification_results(results: list[dict]) -> pd.DataFrame:
    """Sort and display classification model comparison table."""
    df = pd.DataFrame(
        [{k: v for k, v in r.items()
          if k in {"model", "Accuracy", "Precision", "Recall", "F1", "n"}}
         for r in results]
    )
    df = df.sort_values("F1", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1
    return df
