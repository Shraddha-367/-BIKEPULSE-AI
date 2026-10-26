"""
Page 3 — Probability Simulation (T09)
Normal, Uniform, Binomial, Poisson distributions.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats as scipy_stats
from scipy.stats import norm, poisson as sci_poisson

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection import load_hour_csv
from src.preprocessing import clean_dataframe
from src.probability import fit_normal, fit_poisson, fit_binomial, simulate_uniform

st.set_page_config(page_title="Probability Distributions — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS, apply_chart_theme
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="prob_sim")
render_sidebar_drawer(active_page="prob_sim")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T09 · Probability Intelligence</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Probability Distributions</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Empirical distribution fitting and theoretical diagnostic models on bike rental transit data.</p>
</div>
""", unsafe_allow_html=True)

DARK = "plotly_dark"
PLOT_BG = COLORS["bg_primary"]

@st.cache_data
def get_df():
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"
    return clean_dataframe(load_hour_csv(raw_path))

df = get_df()

# ── Normal Distribution (T09) ─────────────────────────────────────────────────
st.header("1. Normal Distribution")

with st.expander("Distribution Fitting Parameters", expanded=True):
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        col_choice = st.selectbox("Data Column", ["cnt", "temp_celsius", "hum_percent", "windspeed_kmh"])
    with col_p2:
        n_bins = st.slider("Histogram bins", 20, 100, 50)

s = df[col_choice].dropna()
normal_res = fit_normal(s)

col_n1, col_n2, col_n3, col_n4 = st.columns(4)
col_n1.metric("μ (Mean)", f"{normal_res['mu']:.2f}")
col_n2.metric("σ (Std Dev)", f"{normal_res['sigma']:.2f}")
col_n3.metric("Shapiro-Wilk p", f"{normal_res['shapiro_p']:.4f}")
col_n4.metric("Is Normal (p>0.05)", "Yes" if normal_res["is_normal_p05"] else "No")

st.info(normal_res["note"])

# Plot histogram + fitted normal PDF
x_range = np.linspace(s.min(), s.max(), 300)
pdf_vals = norm.pdf(x_range, normal_res["mu"], normal_res["sigma"])

fig = go.Figure()
fig.add_trace(go.Histogram(
    x=s, nbinsx=n_bins, histnorm="probability density",
    name="Observed Data", opacity=0.75,
    marker_color="rgba(122,158,201,0.55)",
    marker_line_color="rgba(122,158,201,0.3)",
    marker_line_width=0.5,
))
fig.add_trace(go.Scatter(
    x=x_range, y=pdf_vals,
    mode="lines", name="Fitted Normal PDF",
    line=dict(color=COLORS["chart_gold"], width=2.5),
))
apply_chart_theme(fig, height=420, title=f"Normal Distribution Fit — {col_choice}")
fig.update_layout(xaxis_title=col_choice, yaxis_title="Density")
st.plotly_chart(fig, use_container_width=True)

# ── Poisson Distribution (T09) ────────────────────────────────────────────────
st.header("2. Poisson Distribution")

poisson_res = fit_poisson(df["cnt"])

col_p1, col_p2, col_p3 = st.columns(3)
col_p1.metric("λ (Estimated Mean)", f"{poisson_res['lambda_hat']:.2f}")
col_p2.metric("Sample Variance", f"{poisson_res['sample_variance']:.2f}")
col_p3.metric("Dispersion Ratio (Var/Mean)", f"{poisson_res['dispersion_ratio']:.2f}")

st.warning(poisson_res["note"])

# Plot Poisson PMF vs empirical
lam = poisson_res["lambda_hat"]
k_range = np.arange(0, min(int(lam * 3), 1000))
poisson_pmf = sci_poisson.pmf(k_range, lam)

# Empirical frequencies
cnt_rounded = df["cnt"].round().astype(int)
emp_counts = cnt_rounded.value_counts().sort_index()
max_k = min(int(lam * 3), 1000, emp_counts.index.max())
emp_k = emp_counts[emp_counts.index <= max_k]
emp_pmf = emp_k / emp_k.sum()

fig = go.Figure()
fig.add_trace(go.Bar(
    x=emp_pmf.index[:100], y=emp_pmf.values[:100],
    name="Empirical PMF", opacity=0.75,
    marker_color="rgba(122,158,201,0.6)",
    marker_line_color="rgba(122,158,201,0.3)",
    marker_line_width=0.5,
))
fig.add_trace(go.Scatter(
    x=k_range[:100], y=poisson_pmf[:100],
    mode="lines+markers", name="Fitted Poisson PMF",
    line=dict(color=COLORS["chart_gold"], width=2),
    marker=dict(size=3, color=COLORS["chart_gold"]),
))
apply_chart_theme(fig, height=420, title=f"Poisson Distribution vs Empirical (λ={lam:.1f})")
fig.update_layout(xaxis_title="Rental Count", yaxis_title="Probability", xaxis_range=[0, 100])
st.plotly_chart(fig, use_container_width=True)

# ── Binomial Distribution (T09) ───────────────────────────────────────────────
st.header("3. Binomial Distribution — High Demand Event Model")

threshold_pct = st.slider("High-demand threshold (percentile)", 50, 95, 75)
threshold = float(np.percentile(df["cnt"], threshold_pct))
binom_res = fit_binomial(df["cnt"], threshold=threshold)

col_b1, col_b2, col_b3 = st.columns(3)
col_b1.metric("P(High Demand)", f"{binom_res['p_hat']:.3f}")
col_b2.metric("Threshold Count", f"{binom_res['threshold_cnt']:.0f}")
col_b3.metric("Expected High-Demand Hours/Day", f"{binom_res['expected_high_demand_hours']:.1f}")

st.info(binom_res["note"])

n = binom_res["n"]
pmf = binom_res["pmf_values"]
fig = go.Figure(go.Bar(
    x=list(range(n + 1)), y=pmf,
    marker_color="rgba(229,192,123,0.75)",
    marker_line_color="rgba(229,192,123,0.4)",
    marker_line_width=0.5,
    name="Binomial PMF",
))
apply_chart_theme(fig, height=400, title=f"Binomial PMF: P(high demand) = {binom_res['p_hat']:.3f}, n=24 hours")
fig.update_layout(
    xaxis_title="Number of High-Demand Hours in a Day",
    yaxis_title="Probability",
)
st.plotly_chart(fig, use_container_width=True)

# ── Uniform Distribution Simulation (T09) ────────────────────────────────────
st.header("4. Uniform Distribution [Simulation]")
st.warning(
    "SYNTHETIC SIMULATION — This Uniform distribution does not model real bike rental data. "
    "It is an illustrative demonstration of the Uniform distribution concept."
)

sim_res = simulate_uniform(n_samples=10000, low=0.0, high=1.0, seed=42)

col_u1, col_u2, col_u3 = st.columns(3)
col_u1.metric("Theoretical Mean", f"{sim_res['theoretical_mean']:.4f}")
col_u2.metric("Sample Mean", f"{sim_res['sample_mean']:.4f}")
col_u3.metric("Theoretical Std", f"{sim_res['theoretical_std']:.4f}")

fig = px.histogram(
    x=sim_res["samples"], nbins=50, histnorm="probability density",
    labels={"x": "Value", "y": "Density"},
    color_discrete_sequence=["rgba(122,158,201,0.65)"],
)
fig.update_traces(marker_line_color="rgba(122,158,201,0.3)", marker_line_width=0.5)
fig.add_hline(
    y=1.0, line_dash="dash", line_color=COLORS["chart_gold"],
    annotation_text="Theoretical density = 1.0",
    annotation_font_color=COLORS["chart_gold"],
)
apply_chart_theme(fig, height=380, title="Uniform(0,1) Simulation — 10,000 samples")
st.plotly_chart(fig, use_container_width=True)

st.markdown("**Distribution Comparison Summary**")
st.dataframe(pd.DataFrame([
    {"Distribution": "Normal", "Fitted to": "Real rental counts", "Key finding": f"μ={normal_res['mu']:.1f}, σ={normal_res['sigma']:.1f} — right-skewed data"},
    {"Distribution": "Poisson", "Fitted to": "Real rental counts", "Key finding": f"λ={poisson_res['lambda_hat']:.1f}, overdispersed (ratio={poisson_res['dispersion_ratio']:.1f})"},
    {"Distribution": "Binomial", "Fitted to": "High-demand event probability", "Key finding": f"p={binom_res['p_hat']:.3f} per hour"},
    {"Distribution": "Uniform", "Fitted to": "SYNTHETIC SIMULATION ONLY", "Key finding": "Illustrative — not fitted to real data"},
]), use_container_width=True, hide_index=True)

render_footer()
