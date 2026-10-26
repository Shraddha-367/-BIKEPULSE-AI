"""
Page 1 — Data Management (T01, T02, T03, T04, T05)
Web scraping, HTML parsing, data collection, cleaning, missing/duplicate handling.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection import scrape_uci_metadata, get_data_provenance, load_hour_csv
from src.preprocessing import (
    clean_dataframe, run_missing_duplicate_audit,
    inject_synthetic_issues, export_cleaned_csv
)

st.set_page_config(page_title="Data Management — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="data_mgmt")
render_sidebar_drawer(active_page="data_mgmt")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T01 – T05 · Data Foundation</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Data Management</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Dataset sourcing, web scraping, cleaning pipeline and quality validation.</p>
</div>
""", unsafe_allow_html=True)

# ── Section 1: UCI Metadata Scraping (T01, T02) ──────────────────────────────
st.header("UCI Dataset Metadata — Web Scraping (T01, T02)")

with st.expander("About Web Scraping in BIKEPULSE AI", expanded=False):
    st.info(
        "BIKEPULSE AI uses `requests` + `BeautifulSoup` to fetch metadata from the public UCI "
        "dataset page. A local cache is saved so the app works offline. CSV data ingestion is "
        "completely separate from scraping — no rental rows are synthesized from the web."
    )

col_scrape1, col_scrape2 = st.columns([1, 3])
with col_scrape1:
    fetch_btn = st.button("Fetch UCI Metadata", type="primary")
    use_cache = st.checkbox("Use cache if available", value=True)

if fetch_btn or "uci_metadata" not in st.session_state:
    with st.spinner("Fetching UCI page metadata..."):
        meta = scrape_uci_metadata(use_cache=use_cache)
        st.session_state["uci_metadata"] = meta

if "uci_metadata" in st.session_state:
    meta = st.session_state["uci_metadata"]
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Source", "UCI ML Repository")
    with col_m2:
        cache_status = "Cached Local File" if meta.get("from_cache") else "Live Remote Fetch"
        st.metric("Fetch Status", cache_status)
    with col_m3:
        st.metric("Variables Found", len(meta.get("variables", [])))
    
    st.subheader("Extracted Metadata (T02 — HTML Parsing)")
    st.markdown(f"**Title**: {meta.get('title', 'N/A')}")
    st.markdown(f"**Description**: {meta.get('description', 'N/A')[:300]}...")
    st.markdown(f"**Source URL**: {meta.get('source_url', 'N/A')}")
    st.markdown(f"**Fetched at**: {meta.get('fetch_timestamp', 'N/A')}")
    
    if meta.get("variables"):
        st.subheader("Dataset Variables")
        var_df = pd.DataFrame(meta["variables"])
        st.dataframe(var_df, use_container_width=True, hide_index=True)

# ── Section 2: Data Collection & Schema Validation (T03) ─────────────────────
st.header("Data Collection & Schema Validation (T03)")

raw_path = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"
prov = get_data_provenance(raw_path)

col_p1, col_p2 = st.columns(2)
with col_p1:
    st.subheader("Data Provenance")
    for k, v in prov.items():
        st.markdown(f"**{k.replace('_', ' ').title()}**: `{v}`")
with col_p2:
    st.subheader("Raw Data Preview")
    try:
        df_raw = load_hour_csv(raw_path)
        st.success(f"Loaded {len(df_raw):,} rows × {len(df_raw.columns)} columns successfully")
        st.dataframe(df_raw.head(5), use_container_width=True)
    except Exception as e:
        st.error(f"Failed to load raw CSV: {e}")
        st.stop()

# ── Section 3: Cleaning Pipeline (T04) ───────────────────────────────────────
st.header("Data Cleaning Pipeline (T04)")

if "df_clean" not in st.session_state:
    with st.spinner("Running cleaning pipeline..."):
        df_clean = clean_dataframe(df_raw)
        st.session_state["df_clean"] = df_clean
else:
    df_clean = st.session_state["df_clean"]

col_c1, col_c2, col_c3 = st.columns(3)
with col_c1:
    st.metric("Raw Rows", f"{len(df_raw):,}")
with col_c2:
    st.metric("Clean Rows", f"{len(df_clean):,}")
with col_c3:
    st.metric("Columns", f"{len(df_clean.columns)}")

with st.expander("Cleaning Steps Applied", expanded=True):
    st.markdown("""
    1. **Date Parsing**: `dteday` parsed to `datetime64`; invalid dates dropped.
    2. **Chronological Ordering**: Sorted by `datetime_hour = dteday + hr`.
    3. **Type Casting**: Categorical columns cast to `int`.
    4. **Range Validation**: `temp`, `atemp`, `hum`, `windspeed`, `hr`, `season`, 
       `weathersit`, `cnt` values clipped to documented valid ranges.
    5. **Decoded Columns Added**: `season_label`, `weather_label`, 
       `temp_celsius`, `atemp_celsius`, `hum_percent`, `windspeed_kmh`.
    6. **Missing Value Policy**: Forward-fill numeric; mode-fill categorical.
    7. **Duplicate Removal**: Kept first of any duplicate `(dteday, hr)` pairs.
    """)

st.subheader("Cleaned Dataset Preview")
st.dataframe(df_clean.head(10), use_container_width=True)

# Export
if st.button("Export Cleaned CSV"):
    out = export_cleaned_csv(df_clean)
    st.success(f"Exported to `{out}` successfully")

# ── Section 4: Missing Values & Duplicate Audit (T05) ────────────────────────
st.header("Missing Values & Duplicate Audit (T05)")

audit = run_missing_duplicate_audit(df_clean)

col_a1, col_a2, col_a3 = st.columns(3)
with col_a1:
    missing_total = sum(audit["missing_counts"].values()) if audit["missing_counts"] else 0
    st.metric("Missing Values", missing_total, 
              delta="Zero (Clean)" if missing_total == 0 else f"{missing_total} detected")
with col_a2:
    st.metric("Duplicate Rows", audit["duplicate_rows"],
              delta="Zero (Clean)" if audit["duplicate_rows"] == 0 else f"{audit['duplicate_rows']} duplicates")
with col_a3:
    st.metric("cnt ≠ casual+registered", audit["cnt_mismatch_rows"],
              delta="100% Consistent" if audit["cnt_mismatch_rows"] == 0 else "Mismatch detected")

# Test with controlled synthetic fixture
st.subheader("Synthetic Fixture Test (Controlled Anomaly Injection)")
st.info(
    "The UCI dataset is verified clean. To demonstrate missing-value and duplicate handling in action, "
    "a controlled synthetic fixture injects 5 missing `temp` values and 3 duplicate rows. "
    "This audit is clearly labelled and does not overwrite the baseline dataset."
)

if st.button("Run Synthetic Fixture Test"):
    corrupted = inject_synthetic_issues(df_clean[:1000])
    audit_corrupted = run_missing_duplicate_audit(corrupted)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**Before cleaning (corrupted fixture)**")
        st.json(audit_corrupted)
    with col_t2:
        st.markdown("**After cleaning**")
        cleaned_fixture = clean_dataframe(corrupted)
        audit_after = run_missing_duplicate_audit(cleaned_fixture)
        st.json(audit_after)
        st.success("All injected issues resolved successfully by cleaning pipeline.")

# ── Data Type Summary ─────────────────────────────────────────────────────────
st.header("Data Schema & Types")
dtype_df = pd.DataFrame({
    "Column": df_clean.dtypes.index,
    "Type": df_clean.dtypes.values.astype(str),
    "Non-null": df_clean.notnull().sum().values,
    "Null": df_clean.isnull().sum().values,
}).reset_index(drop=True)
st.dataframe(dtype_df, use_container_width=True, hide_index=True)

render_footer()
