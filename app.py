"""
BIKEPULSE AI — Premium Analytics Landing Page
==============================================
Design System: Quiet Luxury + Modern Enterprise Analytics + Restrained Glassmorphism
Color Palette: Deep Navy (#0D1B2A) · Royal Navy (#1B263B) · Champagne Gold (#E5C07B) · Luxury Cream (#F3E9D2)

Layout:
  1. Premium top navbar (SVG logo + wordmark, clean navigation links)
  2. Centered hero with Manrope display type and selective Gold accent
  3. Two CTA buttons (Gold primary, Royal Navy secondary)
  4. Technology metadata row (no giant pill badges)
  5. Wide analytics preview (Navy glass, Gold time-series chart)
  6. 4 KPI stat cards (Royal Navy surface, strong value hierarchy)
  7. Platform capabilities (clean feature cards)
  8. 10-module explorer grid (consistent card design)
  9. How It Works workflow (numbered steps, minimal)
 10. About + Footer (SVG brand mark, no emoji)
 11. Off-canvas sliding navigation drawer
"""

import sys
import json
import logging
from pathlib import Path
import streamlit as st
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.data_collection import load_hour_csv, get_data_provenance
from src.preprocessing import clean_dataframe, export_cleaned_csv

from ui.theme import inject_global_css
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import (
    render_hero_section,
    render_wide_dashboard_preview,
    render_four_stat_cards,
    render_capabilities_section,
    render_modules_grid,
    render_how_it_works,
    render_about_section,
    render_footer,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Page Configuration ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="BIKEPULSE AI — Smart Bike Rental Intelligence",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Inject Global Design System ──────────────────────────────────────────────
inject_global_css()

# ── Data Loading (cached) ────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading BIKEPULSE AI Dataset...")
def load_data() -> pd.DataFrame:
    """Load and cache the cleaned dataset."""
    raw_path = Path(__file__).parent / "data" / "raw" / "hour.csv"
    df_raw = load_hour_csv(raw_path)
    df_clean = clean_dataframe(df_raw)
    cleaned_path = Path(__file__).parent / "data" / "processed" / "hour_clean.csv"
    if not cleaned_path.exists():
        export_cleaned_csv(df_clean, cleaned_path)
    return df_clean

# Initialize or retrieve dataset in session state
if "df" not in st.session_state:
    st.session_state["df"] = load_data()

df = st.session_state["df"]

# Count evaluated models if evaluation reports exist
eval_dir = Path(__file__).parent / "reports" / "evaluation"
model_count = 11
if (eval_dir / "regression_results.json").exists() and (eval_dir / "classification_results.json").exists():
    try:
        with open(eval_dir / "regression_results.json") as f:
            reg_d = json.load(f)
        with open(eval_dir / "classification_results.json") as f:
            cls_d = json.load(f)
        model_count = len(reg_d.get("all_val_results", [])) + len(cls_d.get("all_val_results", []))
    except Exception:
        model_count = 11

# ── 1. Top Horizontal Navigation Bar ─────────────────────────────────────────
render_top_navbar(active_page="home")

# ── Sidebar Drawer ───────────────────────────────────────────────────────────
render_sidebar_drawer(active_page="home")

# ── 2. Centered Hero Section (matching reference wireframe) ──────────────────
render_hero_section()

# ── 3. Wide Dashboard Preview Section ────────────────────────────────────────
render_wide_dashboard_preview(df)

# ── 4. Four Statistics Cards Below Preview ───────────────────────────────────
render_four_stat_cards(df, model_count=model_count)

# ── 5. Platform Capabilities (3 Cards) ───────────────────────────────────────
render_capabilities_section()

# ── 6. Explore All 10 Modules Grid ───────────────────────────────────────────
render_modules_grid()

# ── 7. How BIKEPULSE AI Works (Workflow Pipeline) ────────────────────────────
render_how_it_works()

# ── 8. About BIKEPULSE AI ────────────────────────────────────────────────────
render_about_section()

# ── 9. Professional Footer ───────────────────────────────────────────────────
render_footer()
