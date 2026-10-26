"""
Page 5 — Hypothesis Testing (T20–T27)
All hypothesis tests with H0/H1, alpha selector, p-values and decisions.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection import load_hour_csv
from src.preprocessing import clean_dataframe
from src.hypothesis_tests import (
    one_sample_ttest, two_sample_ttest, paired_ttest,
    one_way_anova, chi_square_independence,
)

st.set_page_config(page_title="Hypothesis Testing — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="hypothesis")
render_sidebar_drawer(active_page="hypothesis")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T20 – T27 · Statistical Inference</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Hypothesis Testing</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Formal parametric and non-parametric hypothesis tests with strict α threshold evaluation.</p>
</div>
""", unsafe_allow_html=True)

@st.cache_data
def get_df():
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"
    df = clean_dataframe(load_hour_csv(raw_path))
    # Add high_demand for chi-square
    threshold = float(np.percentile(df["cnt"], 75))
    df["high_demand"] = (df["cnt"] >= threshold).astype(int)
    return df

df = get_df()

with st.expander("Significance Threshold (α) Parameters", expanded=True):
    col_a1, col_a2 = st.columns([1, 2])
    with col_a1:
        alpha = st.select_slider("Significance Level (α)", options=[0.01, 0.05, 0.10], value=0.05)
        st.markdown(f"**Selected Significance Threshold: α = {alpha}**")
    with col_a2:
        st.info(
            "H0 is rejected when p-value < α. "
            "A small p-value provides evidence against H0 — "
            "it does NOT prove H1 is true."
        )

def display_test_result(result: dict):
    """Render a formatted hypothesis test result."""
    if "error" in result:
        st.error(f"Test error: {result['error']}")
        return
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"**H₀**: {result.get('H0', 'N/A')}")
        st.markdown(f"**H₁**: {result.get('H1', 'N/A')}")
    with col2:
        sig = result.get("significant", False)
        if sig:
            st.success(f"Significant: {result.get('decision', 'N/A')}")
        else:
            st.info(f"Not Significant: {result.get('decision', 'N/A')}")
    
    metric_cols = st.columns(3)
    metric_cols[0].metric("Test Statistic", f"{result.get('statistic', 'N/A'):.4f}")
    metric_cols[1].metric("p-value", f"{result.get('p_value', 1):.6f}")
    metric_cols[2].metric("α", f"{result.get('alpha', alpha)}")
    
    if result.get("caveats"):
        st.caption(f"Caveat: {result['caveats']}")

tab_names = [
    "One-Sample T (T23)", "Two-Sample T (T24)", "Paired T (T25)",
    "ANOVA (T26)", "Chi-Square (T27)"
]
tabs = st.tabs(tab_names)

# ── T23 — One-Sample T-Test ───────────────────────────────────────────────────
with tabs[0]:
    st.subheader("T23 — One-Sample T-Test")
    st.markdown("Compare a historical demand subset to a user-specified planning benchmark.")
    
    col1, col2 = st.columns(2)
    with col1:
        filter_hour = st.selectbox("Hour to Test (None = all hours)", [None] + list(range(24)),
                                    format_func=lambda x: "All hours" if x is None else f"{x}:00")
        benchmark = st.number_input("Planning Benchmark (rentals/hr)", min_value=1.0,
                                     max_value=1000.0, value=189.5, step=0.5)
    
    result = one_sample_ttest(df, col="cnt", filter_hour=filter_hour,
                               popmean=benchmark, alpha=alpha)
    
    st.divider()
    display_test_result(result)
    
    if "sample_mean" in result:
        col1, col2 = st.columns(2)
        col1.metric("Sample Mean", f"{result['sample_mean']:.2f}")
        col2.metric("Sample n", f"{result['sample_n']:,}")

# ── T24 — Two-Sample T-Test ───────────────────────────────────────────────────
with tabs[1]:
    st.subheader("T24 — Independent Two-Sample T-Test (Welch)")
    st.markdown("Compare demand between working days and non-working days.")
    
    result2 = two_sample_ttest(df, col="cnt", group_col="workingday",
                                group_a=1, group_b=0, alpha=alpha)
    
    display_test_result(result2)
    
    if "group_a_mean" in result2:
        col1, col2 = st.columns(2)
        col1.metric("Working Day Mean", f"{result2['group_a_mean']:.2f}",
                    f"n={result2['group_a_n']:,}")
        col2.metric("Non-Working Day Mean", f"{result2['group_b_mean']:.2f}",
                    f"n={result2['group_b_n']:,}")

# ── T25 — Paired T-Test ───────────────────────────────────────────────────────
with tabs[2]:
    st.subheader("T25 — Paired T-Test (Morning vs Evening)")
    st.markdown("Compare same-date morning and evening rush-hour demand (paired observations).")
    
    col1, col2 = st.columns(2)
    with col1:
        morning_hr = st.selectbox("Morning Hour", [6, 7, 8, 9], index=2)
    with col2:
        evening_hr = st.selectbox("Evening Hour", [16, 17, 18, 19], index=1)
    
    result3 = paired_ttest(df, col="cnt", morning_hr=morning_hr,
                            evening_hr=evening_hr, alpha=alpha)
    
    display_test_result(result3)
    
    if "n_pairs" in result3:
        col1, col2, col3 = st.columns(3)
        col1.metric("Paired Observations", f"{result3['n_pairs']:,}")
        col2.metric("Mean Morning Demand", f"{result3['mean_morning']:.2f}")
        col3.metric("Mean Evening Demand", f"{result3['mean_evening']:.2f}")

# ── T26 — One-Way ANOVA ───────────────────────────────────────────────────────
with tabs[3]:
    st.subheader("T26 — One-Way ANOVA (Seasonal Demand)")
    st.markdown("Test whether mean demand differs significantly across seasons.")
    
    result4 = one_way_anova(df, col="cnt", group_col="season", alpha=alpha)
    
    display_test_result(result4)
    
    if "groups" in result4:
        grp_df = pd.DataFrame(result4["groups"]).T.reset_index()
        grp_df.columns = ["Season Code", "n", "Mean", "Std Dev"]
        grp_df["Season"] = grp_df["Season Code"].astype(int).map(
            {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
        )
        st.dataframe(grp_df[["Season", "n", "Mean", "Std Dev"]], 
                     use_container_width=True, hide_index=True)
        
        st.markdown(f"**Levene Test for Equal Variances**: "
                    f"F={result4['levene_stat']:.3f}, p={result4['levene_p']:.4f}")

# ── T27 — Chi-Square ─────────────────────────────────────────────────────────
with tabs[4]:
    st.subheader("T27 — Chi-Square Test of Independence")
    st.markdown("Test association between weather situation and high-demand label.")
    
    result5 = chi_square_independence(df, cat_col="weathersit",
                                       high_demand_col="high_demand", alpha=alpha)
    
    display_test_result(result5)
    
    if "contingency_table" in result5:
        st.markdown("**Contingency Table** (weathersit × high_demand)")
        ct_df = pd.DataFrame(result5["contingency_table"])
        ct_df.index = [f"Weather {i}" for i in ct_df.index]
        ct_df.columns = [f"HD={c}" for c in ct_df.columns]
        st.dataframe(ct_df, use_container_width=True)
        
        st.markdown(f"**Degrees of Freedom**: {result5['dof']}")
        st.markdown(f"**Total observations**: {result5['n']:,}")
        
        if result5["cells_below_5"]:
            st.warning(
                f"{len(result5['cells_below_5'])} cell(s) with expected count < 5. "
                "Cochran's rule violated. Consider merging rare weather categories."
            )
        else:
            st.success("All expected cell counts ≥ 5 (Cochran's rule satisfied).")

render_footer()
