"""
Reporting utilities — summary statistics, export helpers.
"""
import json
import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger(__name__)


def export_summary_report(regression_results: list[dict],
                           classification_results: list[dict],
                           output_path: Path = None) -> Path:
    """Export a combined model performance summary to CSV."""
    if output_path is None:
        output_path = Path(__file__).parent.parent / "reports" / "evaluation" / "model_summary.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    reg_df = pd.DataFrame([
        {k: v for k, v in r.items()
         if k in {"model", "MAE", "MSE", "RMSE", "R2", "n", "split"}}
        for r in regression_results
    ])
    reg_df["task"] = "Regression"

    cls_df = pd.DataFrame([
        {k: v for k, v in r.items()
         if k in {"model", "Accuracy", "Precision", "Recall", "F1", "n", "split"}}
        for r in classification_results
    ])
    cls_df["task"] = "Classification"

    combined = pd.concat([reg_df, cls_df], ignore_index=True)
    combined.to_csv(output_path, index=False)
    logger.info("Model summary report saved to %s", output_path)
    return output_path


def planning_recommendations(pred_count: float, threshold: float,
                              hour: int, season: str) -> list[str]:
    """Generate practical resource planning recommendations based on predictions."""
    recs = []

    if pred_count >= threshold:
        recs.append(f"HIGH DEMAND ALERT: ~{pred_count:.0f} rentals expected.")
        recs.append("→ Ensure maximum fleet availability at this hour.")
        recs.append("→ Pre-position bikes at high-traffic stations.")
        if hour in [7, 8, 9]:
            recs.append("→ Morning rush: prioritize commuter routes.")
        elif hour in [17, 18, 19]:
            recs.append("→ Evening rush: ensure dock capacity at destination stations.")
    else:
        recs.append(f"NORMAL DEMAND: ~{pred_count:.0f} rentals expected.")
        recs.append("→ Standard fleet distribution is sufficient.")
        recs.append("→ Good time for maintenance and rebalancing operations.")

    if season == "Winter":
        recs.append("Winter conditions: expect higher weather-related cancellations.")
    elif season == "Summer":
        recs.append("Summer peak: plan for extended operational hours.")

    return recs


def hex_to_rgba(hex_color: str, alpha: float = 1.0) -> str:
    """Convert a 6-digit hex color to valid CSS/Plotly rgba(r,g,b,a) string.

    Parameters
    ----------
    hex_color : str
        Hex color string, e.g. '#64b4ff' or '64b4ff'.
    alpha : float, default 1.0
        Alpha transparency in [0, 1].

    Returns
    -------
    str
        Formatted 'rgba(r,g,b,alpha)' string compatible with Plotly and CSS.
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        raise ValueError(f"Expected a six-digit hex color, got '{hex_color}'")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    if not 0 <= alpha <= 1:
        raise ValueError(f"Alpha must be between 0 and 1, got {alpha}")
    return f"rgba({r},{g},{b},{alpha})"
