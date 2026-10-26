"""
Page 2 — Exploratory Analysis (T06, T07, T08)
EDA, descriptive statistics and all chart types.
Night Gradient Glassmorphism redesign.
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
from src.descriptive_stats import compute_descriptive_stats, compute_grouped_stats, summarise_dataframe

st.set_page_config(page_title="Exploratory Analysis — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS, CHART_PALETTE_HEX, apply_chart_theme
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="eda")
render_sidebar_drawer(active_page="eda")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T06 – T08 · Exploratory Intelligence</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Exploratory Data Analysis</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Interactive distribution analysis, statistical summaries and multi-dimensional visualizations.</p>
</div>
""", unsafe_allow_html=True)

DARK = "plotly_dark"
PLOT_BG = COLORS["bg_primary"]

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_clean_df():
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"
    return clean_dataframe(load_hour_csv(raw_path))

df = get_clean_df()
SEASON_MAP = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
WEATHER_MAP = {1: "Clear", 2: "Mist", 3: "Light Rain", 4: "Heavy Rain"}

# ── Interactive Filter Panel ───────────────────────────────────────────────────
with st.expander("Interactive Filters & Data Slices", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        season_filter = st.multiselect("Season", [1, 2, 3, 4], default=[1, 2, 3, 4],
                                        format_func=lambda x: SEASON_MAP[x])
    with col2:
        year_filter = st.multiselect("Year", [0, 1], default=[0, 1],
                                      format_func=lambda x: "2011" if x == 0 else "2012")
    with col3:
        weather_filter = st.multiselect("Weather", [1, 2, 3, 4], default=[1, 2, 3, 4],
                                         format_func=lambda x: WEATHER_MAP[x])
    with col4:
        workday_filter = st.radio("Day Type", ["All", "Working Days", "Non-Working Days"])

df_filtered = df[
    df["season"].isin(season_filter) &
    df["yr"].isin(year_filter) &
    df["weathersit"].isin(weather_filter)
].copy()

if workday_filter == "Working Days":
    df_filtered = df_filtered[df_filtered["workingday"] == 1]
elif workday_filter == "Non-Working Days":
    df_filtered = df_filtered[df_filtered["workingday"] == 0]

st.info(f"Showing **{len(df_filtered):,}** records after filters (of {len(df):,} total)")

# ── T07 — Descriptive Statistics ─────────────────────────────────────────────
st.header("Descriptive Statistics (T07)")

numeric_cols = ["cnt", "temp_celsius", "atemp_celsius", "hum_percent", "windspeed_kmh"]
available_cols = [c for c in numeric_cols if c in df_filtered.columns]
desc_table = summarise_dataframe(df_filtered, cols=available_cols)

if not desc_table.empty:
    st.dataframe(desc_table.round(3), use_container_width=True)

col_sel = st.selectbox("Select column for detailed stats", available_cols, index=0)
stats = compute_descriptive_stats(df_filtered[col_sel])

if stats:
    s_cols = st.columns(8)
    labels = ["Count", "Mean", "Median", "Mode", "Std Dev", "Variance", "Min", "Max"]
    values = [
        f"{stats['count']:,}",
        f"{stats['mean']:.2f}",
        f"{stats['median']:.2f}",
        f"{stats['mode']:.2f}",
        f"{stats['std']:.2f}",
        f"{stats['variance']:.2f}",
        f"{stats['min']:.2f}",
        f"{stats['max']:.2f}",
    ]
    for col, lbl, val in zip(s_cols, labels, values):
        with col:
            st.metric(lbl, val)

    q_cols = st.columns(3)
    with q_cols[0]:
        st.metric("Q1 (25th pct)", f"{stats['q1']:.2f}")
    with q_cols[1]:
        st.metric("Q3 (75th pct)", f"{stats['q3']:.2f}")
    with q_cols[2]:
        st.metric("IQR", f"{stats['iqr']:.2f}")

# ── T08 — Visualizations ─────────────────────────────────────────────────────
st.header("Data Visualizations (T08)")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    ["Histogram", "Box Plot", "Bar Chart", "Pie Chart", "Scatter Plot", "Line Plot"]
)

with tab1:
    st.subheader("Histogram — Distribution of Hourly Rentals")
    fig = px.histogram(
        df_filtered, x="cnt", nbins=50,
        labels={"cnt": "Rentals/Hour"},
        color_discrete_sequence=[COLORS["chart_gold"]],
    )
    fig.update_traces(marker_line_color="rgba(229,192,123,0.4)", marker_line_width=0.5, opacity=0.85)
    apply_chart_theme(fig, height=400, title="Distribution of Hourly Bike Rental Count")
    fig.update_layout(bargap=0.08)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Box Plots — Demand by Group")
    box_grp = st.selectbox("Group by", ["season_label", "weather_label", "hr", "weekday"])
    fig = px.box(
        df_filtered, x=box_grp, y="cnt",
        color=box_grp,
        color_discrete_sequence=CHART_PALETTE_HEX,
    )
    apply_chart_theme(fig, height=420, title=f"Hourly Demand by {box_grp}")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Bar Chart — Average Demand by Hour")
    hourly = df_filtered.groupby("hr")["cnt"].mean().reset_index()
    hourly.columns = ["Hour", "Avg Demand"]
    fig = px.bar(
        hourly, x="Hour", y="Avg Demand",
        color="Avg Demand",
        color_continuous_scale=[[0, "#0D1B2A"], [0.5, "#415A77"], [1.0, "#E5C07B"]],
    )
    fig.update_traces(marker_line_width=0)
    apply_chart_theme(fig, height=400, title="Average Hourly Demand Profile")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Pie Chart — Rental Share by Season")
    seasonal_totals = df_filtered.groupby("season_label")["cnt"].sum().reset_index()
    fig = px.pie(
        seasonal_totals, names="season_label", values="cnt",
        color_discrete_sequence=CHART_PALETTE_HEX,
        hole=0.4,
    )
    fig.update_traces(
        textfont_size=13,
        marker=dict(line=dict(color="rgba(10,15,31,0.8)", width=2)),
    )
    apply_chart_theme(fig, height=400, title="Total Rental Share by Season")
    fig.update_layout(hovermode=False)
    st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.subheader("Scatter Plot — Temperature vs Demand")
    x_col = st.selectbox("X axis", ["temp_celsius", "atemp_celsius", "hum_percent", "windspeed_kmh"])
    sample_n = min(2000, len(df_filtered))
    df_sample = df_filtered.sample(sample_n, random_state=42)
    fig = px.scatter(
        df_sample, x=x_col, y="cnt",
        color="season_label", opacity=0.7,
        color_discrete_sequence=CHART_PALETTE_HEX,
        trendline="ols",
        trendline_color_override=COLORS["chart_gold"],
    )
    fig.update_traces(marker=dict(size=5))
    apply_chart_theme(fig, height=420, title=f"Hourly Demand vs {x_col}")
    st.plotly_chart(fig, use_container_width=True)

with tab6:
    st.subheader("Line Plot — Daily Demand Trend")
    daily = df_filtered.groupby("dteday")["cnt"].sum().reset_index()
    daily.columns = ["Date", "Total Rentals"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["Date"], y=daily["Total Rentals"],
        mode="lines", name="Daily Total",
        line=dict(color=COLORS["chart_gold"], width=1.8),
        fill="tozeroy", fillcolor="rgba(229,192,123,0.10)",
    ))
    apply_chart_theme(fig, height=400, title="Daily Total Bike Rentals")
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Total Rentals",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── T06 — EDA Drilldowns ─────────────────────────────────────────────────────
st.header("EDA Drilldowns (T06)")

col_eda1, col_eda2 = st.columns(2)

with col_eda1:
    st.subheader("Working Day vs Non-Working Day")
    wd = df_filtered.groupby("workingday")["cnt"].agg(["mean", "std", "count"]).reset_index()
    wd["workingday"] = wd["workingday"].map({0: "Non-Working", 1: "Working"})
    wd.columns = ["Day Type", "Mean Demand", "Std Dev", "Count"]
    st.dataframe(wd.round(2), use_container_width=True, hide_index=True)

with col_eda2:
    st.subheader("Hourly Demand Heatmap (Season × Hour)")
    pivot = df_filtered.pivot_table(
        values="cnt", index="season_label", columns="hr", aggfunc="mean"
    )
    fig = px.imshow(
        pivot.round(1), text_auto=True,
        color_continuous_scale=[[0, "#0D1B2A"], [0.5, "#415A77"], [1.0, "#E5C07B"]],
    )
    apply_chart_theme(fig, height=320, title="Average Demand Heatmap: Season × Hour")
    st.plotly_chart(fig, use_container_width=True)

# ── Grouped Stats Table ───────────────────────────────────────────────────────
st.subheader("Grouped Statistics")
grp_col = st.selectbox("Group column", ["season", "weathersit", "hr", "weekday", "workingday"])
grp_stats = compute_grouped_stats(df_filtered, grp_col, "cnt")
st.dataframe(grp_stats, use_container_width=True, hide_index=True)

# Download
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download Filtered Data", csv, "bikepulse_filtered.csv", "text/csv")

render_footer()
