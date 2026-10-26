"""
Page 6 — Correlation Analysis (T28–T32)
Covariance, Pearson, Spearman, hypothesis testing, correlation heatmap.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection import load_hour_csv
from src.preprocessing import clean_dataframe
from src.correlation import (
    covariance_analysis, pearson_correlation, spearman_correlation,
    correlation_hypothesis_tests, correlation_matrix,
)

st.set_page_config(page_title="Correlation Analysis — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS, apply_chart_theme, DIVERGING_COLORSCALE
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="correlation")
render_sidebar_drawer(active_page="correlation")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T28 – T32 · Association & Dependency</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Correlation Analysis</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Bivariate linear and monotonic relationships, covariance structures, and hypothesis testing.</p>
</div>
""", unsafe_allow_html=True)

DARK = "plotly_dark"
PLOT_BG = COLORS["bg_primary"]

@st.cache_data
def get_df():
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"
    return clean_dataframe(load_hour_csv(raw_path))

df = get_df()

# ── T32 — Correlation Heatmap ─────────────────────────────────────────────────
st.header("T32 — Correlation Matrix & Heatmap")

method = st.selectbox("Correlation Method", ["pearson", "spearman"])
corr_cols = st.multiselect(
    "Select columns",
    ["temp", "atemp", "hum", "windspeed", "cnt", "hr", "mnth", "season", "weathersit",
     "workingday", "holiday"],
    default=["temp", "atemp", "hum", "windspeed", "cnt", "hr", "mnth"],
)

if len(corr_cols) >= 2:
    corr_df = correlation_matrix(df, cols=corr_cols, method=method)
    
    fig = px.imshow(
        corr_df.round(3), text_auto=".2f",
        color_continuous_scale=DIVERGING_COLORSCALE,
        color_continuous_midpoint=0, zmin=-1, zmax=1,
        aspect="auto",
    )
    apply_chart_theme(fig, height=550, title=f"{method.capitalize()} Correlation Heatmap")
    st.plotly_chart(fig, use_container_width=True)
    
    # Download correlation matrix
    csv = corr_df.round(4).to_csv()
    st.download_button("Download Correlation Matrix", csv, "correlation_matrix.csv", "text/csv")
else:
    st.warning("Select at least 2 columns.")

# ── T28 — Covariance ─────────────────────────────────────────────────────────
st.header("T28 — Covariance Analysis")

cov_cols = st.multiselect(
    "Select columns for covariance",
    ["temp", "atemp", "hum", "windspeed", "cnt"],
    default=["temp", "atemp", "hum", "windspeed", "cnt"],
    key="cov_cols",
)

if len(cov_cols) >= 2:
    cov_res = covariance_analysis(df, cols=cov_cols)
    
    cov_matrix_df = pd.DataFrame(cov_res["covariance_matrix"])
    fig = px.imshow(
        cov_matrix_df, text_auto=".4f",
        color_continuous_scale=DIVERGING_COLORSCALE,
        color_continuous_midpoint=0,
        aspect="auto",
    )
    apply_chart_theme(fig, height=400, title="Covariance Matrix")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("**Pairwise Covariances**")
    pairwise_df = pd.DataFrame([
        {"Pair": k, "Covariance": v["covariance"], "Interpretation": v["interpretation"]}
        for k, v in cov_res["pairwise"].items()
    ])
    st.dataframe(pairwise_df, use_container_width=True, hide_index=True)
    st.caption(cov_res["note"])

# ── T29 + T30 + T31 — Pearson & Spearman ────────────────────────────────────
st.header("T29/T30/T31 — Pearson & Spearman Correlations with Hypothesis Testing")

col1, col2 = st.columns(2)
with col1:
    num_cols = ["temp", "atemp", "hum", "windspeed", "hr", "mnth", "cnt"]
    x_col = st.selectbox("X variable", num_cols, index=0)
with col2:
    y_col = st.selectbox("Y variable", num_cols, index=4)

if x_col != y_col:
    pear = pearson_correlation(df, x_col, y_col)
    spear = spearman_correlation(df, x_col, y_col)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Pearson Correlation (T29)")
        st.metric("r", f"{pear['r']:.4f}")
        st.metric("p-value", f"{pear['p_value']:.6f}")
        st.metric("Significant (α=0.05)", "Yes" if pear["significant"] else "No")
        st.markdown(f"**H₀**: {pear['H0']}")
        st.markdown(f"**H₁**: {pear['H1']}")
        st.info(f"**Interpretation**: {pear['interpretation']}")
        st.caption(pear["assumptions"])
    
    with col2:
        st.subheader("Spearman Rank Correlation (T30)")
        st.metric("ρ (rho)", f"{spear['rho']:.4f}")
        st.metric("p-value", f"{spear['p_value']:.6f}")
        st.metric("Significant (α=0.05)", "Yes" if spear["significant"] else "No")
        st.markdown(f"**H₀**: {spear['H0']}")
        st.markdown(f"**H₁**: {spear['H1']}")
        st.info(f"**Interpretation**: {spear['interpretation']}")
        st.caption(spear["assumptions"])
    
    # Scatter plot
    sample = df.sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(sample, x=x_col, y=y_col,
                     trendline="ols",
                     color_discrete_sequence=["rgba(122,158,201,0.6)"],
                     trendline_color_override=COLORS["chart_gold"],
                     opacity=0.6)
    fig.update_traces(marker=dict(size=4))
    apply_chart_theme(fig, height=420, title=f"{x_col} vs {y_col} | r={pear['r']:.3f}, ρ={spear['rho']:.3f}")
    st.plotly_chart(fig, use_container_width=True)

# ── Full Correlation Test Table (T31) ─────────────────────────────────────────
st.header("T31 — Correlation Hypothesis Testing — All Key Pairs")

cht = correlation_hypothesis_tests(df)
cht_df = pd.DataFrame(cht)
cht_df.columns = ["Pair", "Pearson r", "Pearson p", "Pearson Sig",
                   "Spearman ρ", "Spearman p", "Spearman Sig", "Interpretation"]

def color_sig(val):
    if val is True:
        return f"color: {COLORS['success']}"
    elif val is False:
        return f"color: {COLORS['error']}"
    return ""

st.dataframe(cht_df.round(4), use_container_width=True, hide_index=True)

render_footer()
