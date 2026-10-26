"""
Page 10 — Reports & Planning (T55)
Consolidated model summary, statistical results, and actionable planning insights.
"""

import sys
import json
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection import load_hour_csv
from src.preprocessing import clean_dataframe
from src.descriptive_stats import compute_descriptive_stats

st.set_page_config(page_title="Reports & Planning — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS, apply_chart_theme
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="about")
render_sidebar_drawer(active_page="about")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T55 · Decision Support & Planning</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Reports & Resource Planning</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Executive demand overview, model benchmark summaries, fleet resource guidance and reporting exports.</p>
</div>
""", unsafe_allow_html=True)

EVAL_DIR = Path(__file__).parent.parent / "reports" / "evaluation"
MODELS_DIR = Path(__file__).parent.parent / "models"

@st.cache_data
def get_df():
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"
    return clean_dataframe(load_hour_csv(raw_path))

df = get_df()

# ── Executive Summary ─────────────────────────────────────────────────────────
st.header("Executive Summary")

threshold = float(np.percentile(df["cnt"], 75))
stats = compute_descriptive_stats(df["cnt"])
rush_hours = df[df["hr"].isin([7, 8, 9, 17, 18, 19])]
night_hours = df[df["hr"].isin(range(0, 6))]
best_season = df.groupby("season")["cnt"].mean().idxmax()
season_map = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Records", f"{len(df):,}", "2011–2012")
col2.metric("Avg Demand", f"{stats['mean']:.0f}", "rentals/hr")
col3.metric("Peak Season", season_map.get(best_season, "N/A"))
col4.metric("High-Demand Threshold", f"{threshold:.0f}", "75th percentile")

# ── Model Performance Summary ─────────────────────────────────────────────────
st.header("Machine Learning Performance Summary")

reg_json = EVAL_DIR / "regression_results.json"
cls_json = EVAL_DIR / "classification_results.json"

if reg_json.exists() and cls_json.exists():
    with open(reg_json) as f:
        reg = json.load(f)
    with open(cls_json) as f:
        cls = json.load(f)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Best Regression Model**")
        st.success(f"Best: **{reg.get('best_model', 'N/A')}**")
        bm = reg.get("best_test_metrics", {})
        st.markdown(f"- R² = **{bm.get('R2', 'N/A')}**")
        st.markdown(f"- RMSE = **{bm.get('RMSE', 'N/A')}** rentals/hr")
        st.markdown(f"- MAE = **{bm.get('MAE', 'N/A')}** rentals/hr")
    
    with col2:
        st.markdown("**Best Classification Model**")
        st.success(f"Best: **{cls.get('best_model', 'N/A')}**")
        bc = cls.get("best_test_metrics", {})
        st.markdown(f"- F1 = **{bc.get('F1', 'N/A')}**")
        st.markdown(f"- Accuracy = **{bc.get('Accuracy', 'N/A')}**")
        st.markdown(f"- Recall = **{bc.get('Recall', 'N/A')}**")
    
    # Full comparison table
    all_val = pd.DataFrame(reg.get("all_val_results", []))
    if not all_val.empty:
        st.markdown("**All Regression Models — Validation**")
        st.dataframe(all_val.sort_values("R2", ascending=False), 
                     use_container_width=True, hide_index=True)
    
    all_cls = pd.DataFrame(cls.get("all_val_results", []))
    if not all_cls.empty:
        st.markdown("**All Classification Models — Validation**")
        st.dataframe(all_cls.sort_values("F1", ascending=False), 
                     use_container_width=True, hide_index=True)
else:
    st.warning("No model results found. Run Model Training first.")

# ── Statistical Findings ──────────────────────────────────────────────────────
st.header("Key Statistical Findings")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Descriptive Statistics (cnt)**")
    stats_df = pd.DataFrame([{
        "Metric": k.replace("_", " ").title(),
        "Value": round(v, 2) if isinstance(v, float) else v
    } for k, v in stats.items() if k not in {"mode_count"}])
    st.dataframe(stats_df, use_container_width=True, hide_index=True)

with col2:
    # Demand by hour bar chart
    hourly = df.groupby("hr")["cnt"].mean().reset_index()
    hourly.columns = ["Hour", "Avg Rentals"]
    fig = px.bar(hourly, x="Hour", y="Avg Rentals",
                 color="Avg Rentals",
                 color_continuous_scale=[[0, "#0D1B2A"], [0.5, "#415A77"], [1.0, "#E5C07B"]])
    fig.update_traces(marker_line_width=0)
    apply_chart_theme(fig, height=350, title="Avg Demand by Hour")
    st.plotly_chart(fig, use_container_width=True)

# ── Operational Planning Guide ────────────────────────────────────────────────
st.header("Operational Planning Guide")

planning_data = {
    "Time of Day": {
        "Morning Rush (7-9am)": f"{df[df['hr'].isin([7,8,9])]['cnt'].mean():.0f} avg",
        "Afternoon (12-4pm)": f"{df[df['hr'].isin(range(12,17))]['cnt'].mean():.0f} avg",
        "Evening Rush (5-7pm)": f"{df[df['hr'].isin([17,18,19])]['cnt'].mean():.0f} avg",
        "Night (12-5am)": f"{df[df['hr'].isin(range(0,6))]['cnt'].mean():.0f} avg",
    },
    "Season": {s: f"{df[df['season']==i]['cnt'].mean():.0f} avg" 
               for i, s in season_map.items()},
    "Day Type": {
        "Working Day": f"{df[df['workingday']==1]['cnt'].mean():.0f} avg",
        "Non-Working Day": f"{df[df['workingday']==0]['cnt'].mean():.0f} avg",
    },
}

for section, items in planning_data.items():
    st.subheader(section)
    plan_df = pd.DataFrame(
        [{"Category": k, "Avg Demand (rentals/hr)": v} for k, v in items.items()]
    )
    st.dataframe(plan_df, use_container_width=True, hide_index=True)

# ── Download Report ───────────────────────────────────────────────────────────
st.header("Reports & Export")

# Build a summary CSV
summary_rows = []
for section, items in planning_data.items():
    for k, v in items.items():
        summary_rows.append({"Category": section, "Subcategory": k, "Avg_Demand": v})

summary_df = pd.DataFrame(summary_rows)
csv_bytes = summary_df.to_csv(index=False).encode("utf-8")
st.download_button("Download Planning Summary CSV", csv_bytes,
                   "bikepulse_planning_summary.csv", "text/csv")

# ── Data Limitations ─────────────────────────────────────────────────────────
st.markdown("---")
st.warning("""
**Important Limitations**:
- All predictions are based on 2011–2012 Capital Bikeshare data from Washington D.C.
- This is an analytical decision-support workspace.
- No station-level data is available; recommendations are system-level only.
- Seasonal/weather patterns from 2011-2012 may not perfectly reflect current conditions.
- Temporal autocorrelation in hourly data means standard independence assumptions in 
  statistical tests should be interpreted cautiously.
""")

st.caption(
    "BIKEPULSE AI — Built with Python 3.11, Streamlit, scikit-learn, pandas, SciPy. "
    "Data: UCI Machine Learning Repository — Bike Sharing Dataset. "
    "Cite: Fanaee-T & Gama (2013), Progress in Artificial Intelligence."
)

render_footer()
