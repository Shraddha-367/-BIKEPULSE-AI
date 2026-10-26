"""
Page 8 — Model Comparison (T45, T51, T52, T53)
Full leaderboard with all regression and classification metrics.
"""

import sys
import json
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reporting import hex_to_rgba

st.set_page_config(page_title="Model Comparison — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS, CHART_PALETTE_HEX, apply_chart_theme
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="comparison")
render_sidebar_drawer(active_page="comparison")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T45, T51–T53 · Model Benchmarking</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Model Comparison & Leaderboard</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Comparative evaluation metrics across 6 regressors and 5 classifiers on validation and held-out test splits.</p>
</div>
""", unsafe_allow_html=True)

DARK = "plotly_dark"
PLOT_BG = COLORS["bg_primary"]
EVAL_DIR = Path(__file__).parent.parent / "reports" / "evaluation"
MODELS_DIR = Path(__file__).parent.parent / "models"

reg_json = EVAL_DIR / "regression_results.json"
cls_json = EVAL_DIR / "classification_results.json"

if not reg_json.exists() or not cls_json.exists():
    st.warning("No training results found. Please run **Model Training** first.")
    st.stop()

with open(reg_json) as f:
    reg_data = json.load(f)
with open(cls_json) as f:
    cls_data = json.load(f)

# ── Regression Leaderboard ────────────────────────────────────────────────────
st.header("Regression Model Leaderboard (T45, T52)")

tab_rv, tab_rt = st.tabs(["Validation Metrics", "Test Metrics"])

with tab_rv:
    reg_val = pd.DataFrame(reg_data.get("all_val_results", []))
    if not reg_val.empty:
        reg_val = reg_val.sort_values("R2", ascending=False).reset_index(drop=True)
        reg_val.index += 1
        st.markdown(f"**Best on Validation R²**: `{reg_data['best_model']}` (Winning Regressor)")
        st.dataframe(reg_val, use_container_width=True)

with tab_rt:
    reg_test = pd.DataFrame(reg_data.get("all_test_results", []))
    if not reg_test.empty:
        reg_test = reg_test.sort_values("R2", ascending=False).reset_index(drop=True)
        reg_test.index += 1
        st.dataframe(reg_test, use_container_width=True)
        st.success(
            f"**Best Regressor Final Test Score**: {reg_data['best_model']} — "
            f"R² = {reg_data['best_test_metrics'].get('R2', 'N/A')}, "
            f"RMSE = {reg_data['best_test_metrics'].get('RMSE', 'N/A')}"
        )

# Regression comparison chart
if not reg_val.empty:
    fig = go.Figure()
    models = reg_val["model"].tolist()
    
    fig.add_trace(go.Bar(
        name="R²", x=models, y=reg_val["R2"].tolist(),
        marker_color="rgba(229,192,123,0.85)",
        marker_line_color="rgba(229,192,123,0.4)",
        marker_line_width=0.5,
        yaxis="y1",
    ))
    fig.add_trace(go.Scatter(
        name="RMSE", x=models, y=reg_val["RMSE"].tolist(),
        mode="lines+markers",
        marker=dict(color=COLORS["chart_steel"], size=8),
        line=dict(color=COLORS["chart_steel"], width=2.5),
        yaxis="y2",
    ))
    
    apply_chart_theme(fig, height=420, title="Regression Model Comparison (Validation)")
    fig.update_layout(
        yaxis=dict(title="R²", range=[0, 1],
                   gridcolor="rgba(138,155,184,0.12)",
                   tickfont=dict(color=COLORS["text_muted"])),
        yaxis2=dict(title="RMSE", overlaying="y", side="right",
                    tickfont=dict(color=COLORS["chart_steel"])),
        barmode="group",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Classification Leaderboard ────────────────────────────────────────────────
st.header("Classification Model Leaderboard (T51, T52)")

tab_cv, tab_ct = st.tabs(["Validation Metrics", "Test Metrics"])

with tab_cv:
    cls_val = pd.DataFrame(cls_data.get("all_val_results", []))
    if not cls_val.empty:
        cls_val = cls_val.sort_values("F1", ascending=False).reset_index(drop=True)
        cls_val.index += 1
        st.markdown(f"**Best on Validation F1**: `{cls_data['best_model']}` (Winning Classifier)")
        st.dataframe(cls_val, use_container_width=True)

with tab_ct:
    cls_test = pd.DataFrame(cls_data.get("all_test_results", []))
    if not cls_test.empty:
        cls_test = cls_test.sort_values("F1", ascending=False).reset_index(drop=True)
        cls_test.index += 1
        st.dataframe(cls_test, use_container_width=True)
        
        best_cls = cls_data.get("best_test_metrics", {})
        st.success(
            f"**Best Classifier Final Test Score**: {cls_data['best_model']} — "
            f"Accuracy = {best_cls.get('Accuracy', 'N/A')}, "
            f"F1 = {best_cls.get('F1', 'N/A')}, "
            f"Recall = {best_cls.get('Recall', 'N/A')}"
        )

# Classification comparison chart
if not cls_val.empty:
    metrics_to_plot = ["Accuracy", "Precision", "Recall", "F1"]
    colors = [
        "rgba(229,192,123,0.85)",  # Champagne Gold
        "rgba(122,158,201,0.85)",  # Steel Blue
        "rgba(106,173,142,0.85)",  # Sage Green
        "rgba(192,122,90,0.85)",   # Terracotta Rust
    ]
    
    fig2 = go.Figure()
    for metric, color in zip(metrics_to_plot, colors):
        if metric in cls_val.columns:
            fig2.add_trace(go.Bar(
                name=metric,
                x=cls_val["model"].tolist(),
                y=cls_val[metric].tolist(),
                marker_color=color,
                marker_line_color=color.replace("0.85", "0.4"),
                marker_line_width=0.5,
            ))
    
    apply_chart_theme(fig2, height=420, title="Classification Model Comparison (Validation)")
    fig2.update_layout(yaxis_title="Score", yaxis_range=[0, 1], barmode="group")
    st.plotly_chart(fig2, use_container_width=True)

# ── Model Selection Rationale (T53) ──────────────────────────────────────────
st.header("Best Model Selection Rationale (T53)")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Regression — Best Model**")
    st.success(f"Best: **{reg_data.get('best_model', 'N/A')}**")
    st.markdown("""
    **Selection metric**: Validation R² (higher = better fit)  
    **Final evaluation**: Held-out test set (used ONCE, after selection)  
    **Why not test for selection**: Prevents optimistic bias from test-set peeking
    """)
    
    best_reg = reg_data.get("best_test_metrics", {})
    if best_reg:
        st.markdown("**Final Test Performance**")
        for k, v in best_reg.items():
            if k in ["MAE", "MSE", "RMSE", "R2", "n"]:
                st.markdown(f"- **{k}**: {v}")

with col2:
    st.markdown("**Classification — Best Model**")
    st.success(f"Best: **{cls_data.get('best_model', 'N/A')}**")
    st.markdown("""
    **Selection metric**: Validation F1 (balances precision and recall)  
    **Final evaluation**: Held-out test set (used ONCE, after selection)  
    **Positive class**: 1 = High Demand (≥ 75th percentile of training cnt)
    """)
    
    best_cls = cls_data.get("best_test_metrics", {})
    if best_cls:
        st.markdown("**Final Test Performance**")
        for k, v in best_cls.items():
            if k in ["Accuracy", "Precision", "Recall", "F1", "n"]:
                st.markdown(f"- **{k}**: {v}")

# ── Saved Model Artifacts ─────────────────────────────────────────────────────
st.header("Saved Model Artifacts (T54)")

model_files = list(MODELS_DIR.glob("*.joblib")) if MODELS_DIR.exists() else []
meta_files = list(MODELS_DIR.glob("*_metadata.json")) if MODELS_DIR.exists() else []

if model_files:
    art_col1, art_col2 = st.columns(2)
    with art_col1:
        st.markdown("**Model Files**")
        for f in model_files:
            size_kb = f.stat().st_size / 1024
            st.markdown(f"- `{f.name}` ({size_kb:.1f} KB)")
    
    with art_col2:
        st.markdown("**Metadata Files**")
        for f in meta_files:
            with open(f) as mf:
                meta = json.load(mf)
            st.markdown(f"- `{f.name}` — saved {meta.get('saved_at', 'N/A')[:10]}")
            if meta.get("integrity_ok") is not False:
                st.markdown(f"  SHA-256 integrity: `{meta.get('sha256', 'N/A')[:12]}...`")
else:
    st.info("No model files found. Run Model Training first.")

# ── Download Evaluation Summary ───────────────────────────────────────────────
summary_path = EVAL_DIR / "model_summary.csv"
if summary_path.exists():
    with open(summary_path, "rb") as f:
        st.download_button("Download Model Summary CSV", f,
                           "model_summary.csv", "text/csv")

render_footer()
