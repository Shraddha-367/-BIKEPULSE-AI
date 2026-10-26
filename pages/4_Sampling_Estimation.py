"""
Page 4 — Sampling & Estimation (T10-T19)
Random sampling, CLT, bootstrap, confidence intervals, coverage probability.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection import load_hour_csv
from src.preprocessing import clean_dataframe
from src.sampling import (
    get_all_samples, population_vs_sample_stats,
    sampling_distribution, central_limit_theorem,
)
from src.statistical_inference import (
    point_estimates, standard_error, bootstrap_estimate,
    confidence_interval_mean, coverage_probability_simulation,
    mean_vs_median_comparison,
)
from src.reporting import hex_to_rgba

st.set_page_config(page_title="Sampling & Estimation — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS, CHART_PALETTE_HEX, apply_chart_theme
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="sampling")
render_sidebar_drawer(active_page="sampling")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T10 – T19 · Inferential Statistics</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Sampling & Statistical Estimation</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Sampling designs, Central Limit Theorem simulations, bootstrap resampling and confidence intervals.</p>
</div>
""", unsafe_allow_html=True)

DARK = "plotly_dark"
PLOT_BG = COLORS["bg_primary"]

@st.cache_data
def get_df():
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"
    return clean_dataframe(load_hour_csv(raw_path))

df = get_df()

tab_names = [
    "Sampling Methods (T10)", "Pop vs Sample (T11)",
    "Sampling Distribution (T12)", "CLT (T13)",
    "Point Est & SE (T14/T15)", "Bootstrap (T16)",
    "Confidence Intervals (T17)", "Coverage Probability (T18)",
    "Mean vs Median (T19)",
]
tabs = st.tabs(tab_names)

# ── T10 — Four Sampling Schemes ───────────────────────────────────────────────
with tabs[0]:
    st.subheader("T10 — Four Sampling Techniques")
    
    with st.expander("Sampling Control Parameters", expanded=False):
        seed = st.number_input("Random Seed", min_value=0, max_value=9999, value=42)
    
    samples = get_all_samples(df, seed=int(seed))
    scheme = st.selectbox("Select Sampling Scheme", list(samples.keys()))
    samp = samples[scheme]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Population Size", f"{len(df):,}")
    col2.metric("Sample Size", f"{len(samp):,}")
    col3.metric("Sampling Rate", f"{len(samp)/len(df)*100:.1f}%")
    
    st.info(f"**Scheme**: {samp.attrs.get('sampling_scheme', scheme)} | "
            f"**Metadata**: {dict(samp.attrs)}")
    
    st.dataframe(samp[["dteday", "hr", "season_label", "weather_label", "cnt"]].head(10),
                 use_container_width=True)
    
    # Compare distributions
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=df["cnt"], name="Population", nbinsx=50,
                               opacity=0.5, histnorm="probability density",
                               marker_color="rgba(122,158,201,0.45)",
                               marker_line_color="rgba(122,158,201,0.2)",
                               marker_line_width=0.5))
    fig.add_trace(go.Histogram(x=samp["cnt"], name=f"{scheme} sample", nbinsx=50,
                               opacity=0.7, histnorm="probability density",
                               marker_color="rgba(229,192,123,0.75)",
                               marker_line_color="rgba(229,192,123,0.3)",
                               marker_line_width=0.5))
    apply_chart_theme(fig, height=400, title="Population vs Sample Distribution")
    fig.update_layout(barmode="overlay")
    st.plotly_chart(fig, use_container_width=True)

# ── T11 — Population vs Sample Statistics ────────────────────────────────────
with tabs[1]:
    st.subheader("T11 — Population vs Sample Statistics")
    
    scheme2 = st.selectbox("Sampling Scheme", list(samples.keys()), key="t11_scheme")
    samp2 = samples[scheme2]
    comparison = population_vs_sample_stats(df, samp2, "cnt")
    
    pop_stats = pd.DataFrame([comparison["population"]]).T
    samp_stats = pd.DataFrame([comparison["sample"]]).T
    combined = pd.concat([pop_stats, samp_stats], axis=1)
    combined.columns = ["Population", f"Sample ({scheme2})"]
    combined["Bias"] = (combined[f"Sample ({scheme2})"] - combined["Population"]).round(4)
    
    st.dataframe(combined.round(4), use_container_width=True)
    st.metric("Mean Bias", f"{comparison['mean_bias']:.4f}",
              delta="good" if abs(comparison['mean_bias']) < 5 else "high")

# ── T12 — Sampling Distribution ──────────────────────────────────────────────
with tabs[2]:
    st.subheader("T12 — Sampling Distribution of the Mean")
    
    n_samp = st.slider("Sample size", 30, 500, 100, key="t12_n")
    n_iter = st.slider("Number of iterations", 100, 2000, 1000, key="t12_iter")
    
    sd_res = sampling_distribution(df, "cnt", n_samples=n_iter, sample_size=n_samp, seed=42)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Population Mean", f"{df['cnt'].mean():.2f}")
    col2.metric("Mean of Sample Means", f"{sd_res['mean_of_means']:.2f}")
    col3.metric("Std of Sample Means (SE)", f"{sd_res['std_of_means']:.2f}")
    
    st.caption(sd_res["caveat"])
    
    fig = px.histogram(x=sd_res["sampling_means"], nbins=40,
                       labels={"x": "Sample Mean", "y": "Frequency"},
                       color_discrete_sequence=["rgba(122,158,201,0.7)"])
    fig.update_traces(marker_line_color="rgba(122,158,201,0.3)", marker_line_width=0.5)
    # Add vertical lines for mean
    fig.add_vline(x=df["cnt"].mean(), line_dash="dash", line_color=COLORS["chart_gold"],
                  annotation_text=f"Pop. Mean={df['cnt'].mean():.1f}",
                  annotation_font_color=COLORS["chart_gold"])
    apply_chart_theme(fig, height=400, title=f"Distribution of {n_iter} Sample Means (n={n_samp})")
    st.plotly_chart(fig, use_container_width=True)

# ── T13 — Central Limit Theorem ──────────────────────────────────────────────
with tabs[3]:
    st.subheader("T13 — Central Limit Theorem")
    
    clt_res = central_limit_theorem(df, "cnt", sample_sizes=[30, 50, 100, 200],
                                     n_iterations=1000, seed=42)
    st.info(clt_res["clt_caveat"])
    
    fig = go.Figure()
    colors = ["#E5C07B", "#7A9EC9", "#6AAD8E", "#C07A5A"]
    for i, (n, color) in enumerate(zip([30, 50, 100, 200], colors)):
        means = clt_res["results"][n]["sample_means"]
        fig.add_trace(go.Histogram(
            x=means, nbinsx=40, name=f"n={n}",
            opacity=0.65, histnorm="probability density",
            marker_color=hex_to_rgba(color, 0.65) if color.startswith("#") else color,
            marker_line_color=hex_to_rgba(color, 0.3) if color.startswith("#") else color,
            marker_line_width=0.5,
        ))
    
    apply_chart_theme(fig, height=420, title="CLT: Sample Mean Distributions for n = 30, 50, 100, 200")
    fig.update_layout(
        xaxis_title="Sample Mean", yaxis_title="Density",
        barmode="overlay",
    )
    st.plotly_chart(fig, use_container_width=True)
    
    clt_table = pd.DataFrame([
        {
            "n": n,
            "Mean of Means": round(clt_res["results"][n]["mean_of_means"], 2),
            "SE (Empirical)": round(clt_res["results"][n]["std_of_means"], 2),
            "SE (Theoretical)": round(clt_res["results"][n]["theoretical_se"], 2),
            "Shapiro-Wilk p": round(clt_res["results"][n]["shapiro_p"], 4),
            "Approx. Normal?": "Yes" if clt_res["results"][n]["is_normal_p05"] else "No",
        }
        for n in [30, 50, 100, 200]
    ])
    st.dataframe(clt_table, use_container_width=True, hide_index=True)

# ── T14 + T15 — Point Estimates & SE ─────────────────────────────────────────
with tabs[4]:
    st.subheader("T14 — Point Estimates")
    pe = point_estimates(df["cnt"])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Mean Estimate", f"{pe['mean_estimate']:.2f}")
    col2.metric("Median Estimate", f"{pe['median_estimate']:.2f}")
    col3.metric("P(High Demand)", f"{pe['proportion_high_demand']:.3f}")
    st.caption(f"Threshold: {pe['high_demand_threshold']:.0f} rentals/hr (75th pct) | n={pe['n']:,}")
    
    st.subheader("T15 — Standard Error")
    se_res = standard_error(df["cnt"])
    col1, col2 = st.columns(2)
    col1.metric("IID Standard Error", f"{se_res['se_iid']:.4f}")
    col1.caption(f"n={se_res['n']:,}, std={se_res['std']:.2f}")
    col2.info(se_res["iid_caveat"])

# ── T16 — Bootstrap ───────────────────────────────────────────────────────────
with tabs[5]:
    st.subheader("T16 — Bootstrap Sampling & Estimation")
    
    col1, col2 = st.columns(2)
    with col1:
        boot_stat = st.selectbox("Statistic", ["mean", "median"])
        n_boot = st.slider("Bootstrap iterations", 500, 5000, 2000)
        conf_boot = st.slider("Confidence level", 0.80, 0.99, 0.95)
        use_block = st.checkbox("Use block bootstrap (more appropriate for temporal data)")
        block_sz = st.slider("Block size (days of 24hr)", 1, 7, 3) * 24 if use_block else None
    
    boot_res = bootstrap_estimate(df["cnt"], stat=boot_stat, n_bootstrap=n_boot,
                                   confidence=conf_boot, seed=42,
                                   block_size=block_sz)
    
    with col2:
        st.metric(f"Observed {boot_stat}", f"{boot_res['observed_value']:.2f}")
        st.metric(f"{conf_boot*100:.0f}% CI Lower", f"{boot_res['ci_lower']:.2f}")
        st.metric(f"{conf_boot*100:.0f}% CI Upper", f"{boot_res['ci_upper']:.2f}")
        st.caption(f"Method: {boot_res['method']}")
    
    fig = px.histogram(x=boot_res["boot_values"], nbins=50,
                       labels={"x": f"Bootstrap {boot_stat}", "y": "Count"},
                       color_discrete_sequence=["rgba(122,158,201,0.7)"])
    fig.update_traces(marker_line_color="rgba(122,158,201,0.3)", marker_line_width=0.5)
    fig.add_vline(x=boot_res["ci_lower"], line_dash="dash", line_color=COLORS["chart_gold"],
                  annotation_text="CI lower", annotation_font_color=COLORS["chart_gold"])
    fig.add_vline(x=boot_res["ci_upper"], line_dash="dash", line_color=COLORS["chart_gold"],
                  annotation_text="CI upper", annotation_font_color=COLORS["chart_gold"])
    fig.add_vline(x=boot_res["observed_value"], line_dash="solid", line_color="#F3E9D2",
                  annotation_text="Observed", annotation_font_color="#F3E9D2")
    apply_chart_theme(fig, height=400, title=f"Bootstrap Distribution of {boot_stat} ({n_boot} resamples)")
    st.plotly_chart(fig, use_container_width=True)

# ── T17 — Confidence Intervals ────────────────────────────────────────────────
with tabs[6]:
    st.subheader("T17 — Confidence Intervals for Mean Demand")
    
    ci_results = confidence_interval_mean(df["cnt"])
    ci_df = pd.DataFrame(ci_results)[
        ["confidence_pct", "mean", "se", "t_critical", "margin_of_error", "ci_lower", "ci_upper", "n"]
    ]
    ci_df.columns = ["Confidence", "Mean", "SE", "t-Critical", "Margin", "CI Lower", "CI Upper", "n"]
    st.dataframe(ci_df.round(4), use_container_width=True, hide_index=True)
    
    fig = go.Figure()
    ci_colors = ["#7A9EC9", "#6AAD8E", "#E5C07B"]
    for ci, col in zip(ci_results, ci_colors):
        fig.add_trace(go.Scatter(
            x=[ci["ci_lower"], ci["ci_upper"]],
            y=[ci["confidence_pct"], ci["confidence_pct"]],
            mode="lines+markers",
            name=ci["confidence_pct"],
            line=dict(width=7, color=col),
            marker=dict(size=11, color=col),
        ))
    fig.add_vline(x=df["cnt"].mean(), line_dash="dash", line_color=COLORS["chart_gold"],
                  annotation_text="Sample Mean", annotation_font_color=COLORS["chart_gold"])
    apply_chart_theme(fig, height=340, title="Confidence Intervals at 90%, 95%, 99%")
    fig.update_layout(xaxis_title="Hourly Rentals")
    st.plotly_chart(fig, use_container_width=True)

# ── T18 — Coverage Probability ────────────────────────────────────────────────
with tabs[7]:
    st.subheader("T18 — Coverage Probability Simulation")
    st.warning(
        "SYNTHETIC SIMULATION — This uses a synthetic known-population Normal distribution, "
        "NOT real bike rental data. Purpose: verify empirical CI coverage."
    )
    
    n_sim = st.slider("Number of simulations", 200, 5000, 2000)
    conf_cov = st.slider("Nominal confidence", 0.80, 0.99, 0.95, key="cov_conf")
    
    cov_res = coverage_probability_simulation(
        true_mean=200.0, true_std=80.0,
        n_per_sample=100, n_simulations=n_sim,
        confidence=conf_cov, seed=42,
    )
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Nominal Coverage", f"{conf_cov*100:.0f}%")
    col2.metric("Empirical Coverage", f"{cov_res['empirical_coverage']*100:.2f}%")
    col3.metric("Intervals Capturing μ", f"{cov_res['captured_count']}/{n_sim}")
    st.caption(cov_res["note"])

# ── T19 — Mean vs Median ──────────────────────────────────────────────────────
with tabs[8]:
    st.subheader("T19 — Mean vs Median as Estimators")
    
    comp = mean_vs_median_comparison(df["cnt"])
    
    st.markdown("**Real Data**")
    rd = comp["real_data"]
    col1, col2, col3 = st.columns(3)
    col1.metric("Mean", f"{rd['mean']:.2f}")
    col2.metric("Median", f"{rd['median']:.2f}")
    col3.metric("Skewness", f"{rd['skewness']:.3f}")
    st.info(f"**Preferred estimator**: {rd['preferred']} (skewness={rd['skewness']:.3f})")
    
    st.markdown("**Outlier Simulation** (SYNTHETIC)")
    st.warning(comp["synthetic_outlier_simulation"]["SIMULATION_TYPE"])
    out = comp["synthetic_outlier_simulation"]
    col1, col2 = st.columns(2)
    col1.metric("Mean shift from outliers", f"+{out['outlier_impact_on_mean']:.2f}")
    col2.metric("Median shift from outliers", f"+{out['outlier_impact_on_median']:.2f}")
    st.success(comp["interpretation"])

render_footer()
