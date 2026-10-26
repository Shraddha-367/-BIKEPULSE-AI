"""
BIKEPULSE AI — Premium Navigation Components
Design: Quiet Luxury Enterprise Analytics
- Top horizontal glass navbar (68–72px height)
  LEFT: Hamburger + SVG logo mark + wordmark
  RIGHT: Home | Modules | Predictor | About
- Off-canvas sliding drawer (300px, Deep Navy)
  Champagne Gold active indicators, Luxury Cream links
"""
import streamlit as st
import pandas as pd
from pathlib import Path


def _init_nav_state(active_page: str):
    """Ensure session state for navigation drawer is properly initialized."""
    if "nav_drawer_open" not in st.session_state:
        st.session_state["nav_drawer_open"] = False
    # Auto-close when navigating to a new page
    current = st.session_state.get("_active_page_nav")
    if current != active_page:
        st.session_state["_active_page_nav"] = active_page
        st.session_state["nav_drawer_open"] = False


def toggle_nav_drawer():
    """Toggle navigation drawer open/close."""
    st.session_state["nav_drawer_open"] = not st.session_state.get("nav_drawer_open", False)


def close_nav_drawer():
    """Explicitly close navigation drawer."""
    st.session_state["nav_drawer_open"] = False


# ── Inline SVG logo mark (no file dependency) ─────────────────────────────────
_LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 38 38" width="32" height="32" role="img" aria-label="BIKEPULSE AI logo mark">
  <circle cx="19" cy="19" r="13" fill="none" stroke="#E5C07B" stroke-width="2" stroke-dasharray="60 22" stroke-linecap="round"/>
  <polyline points="9,19 13,13 17,23 21,9 25,25 29,19" fill="none" stroke="#E5C07B" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="19" cy="19" r="2" fill="#E5C07B"/>
</svg>"""


def render_top_navbar(active_page: str = "home"):
    """Render the premium top horizontal navbar.

    Layout:
      LEFT  → Hamburger (☰) · SVG Mark · BIKEPULSE wordmark
      RIGHT → HOME · MODULES · PREDICTOR · ABOUT
    """
    _init_nav_state(active_page)

    nav_container = st.container(key="bikepulse_navbar")
    with nav_container:
        # Columns: [Logo area (3.5), spacer (1), nav links (5.5)]
        col_logo, col_space, col_home, col_modules, col_pred, col_about = st.columns(
            [3.5, 1.0, 1.1, 1.2, 1.3, 1.1],
            gap="small"
        )

        with col_logo:
            c_ham, c_brand = st.columns([0.85, 4.0])
            with c_ham:
                is_open = st.session_state.get("nav_drawer_open", False)
                ham_icon = "✕" if is_open else "☰"
                st.button(
                    ham_icon,
                    key=f"nav_ham_{active_page}",
                    on_click=toggle_nav_drawer,
                    help="Toggle Navigation"
                )
            with c_brand:
                # SVG mark + wordmark as link to dashboard
                st.markdown(
                    f"""<a href="/" target="_self" style="text-decoration:none;display:flex;align-items:center;gap:8px;height:42px;cursor:pointer;user-select:none;">
                        {_LOGO_SVG}
                        <div style="line-height:1;">
                            <span style="font-family:'Manrope','Inter',sans-serif;font-size:0.98rem;font-weight:700;color:#F3E9D2;letter-spacing:0.3px;">BIKEPULSE</span><span style="font-family:'Inter',sans-serif;font-size:0.65rem;font-weight:600;color:#E5C07B;letter-spacing:0.5px;vertical-align:super;margin-left:2px;">AI</span>
                        </div>
                    </a>""",
                    unsafe_allow_html=True
                )

        with col_home:
            st.page_link(
                "app.py",
                label="Home",
                use_container_width=True,
                disabled=(active_page == "home"),
            )

        with col_modules:
            st.page_link(
                "pages/2_Exploratory_Analysis.py",
                label="Modules",
                use_container_width=True,
                disabled=(active_page == "modules"),
            )

        with col_pred:
            st.page_link(
                "pages/9_Demand_Prediction.py",
                label="Predictor",
                use_container_width=True,
                disabled=(active_page == "predictor"),
            )

        with col_about:
            st.page_link(
                "pages/10_Reports_Planning.py",
                label="About",
                use_container_width=True,
                disabled=(active_page == "about"),
            )

    st.markdown('<div style="margin-bottom:0.6rem;"></div>', unsafe_allow_html=True)


def render_navigation_drawer(active_page: str = "home"):
    """Render the off-canvas premium sliding navigation drawer."""
    _init_nav_state(active_page)

    if not st.session_state.get("nav_drawer_open", False):
        return

    # Backdrop button (click outside to close)
    st.button(
        "",
        key=f"backdrop_btn_{active_page}",
        on_click=close_nav_drawer,
        help="Click outside to close"
    )

    # Drawer container
    with st.container(key="bikepulse_drawer"):
        # Header: Brand (Left) + Close Button (Right)
        head_brand, head_close = st.columns([3.8, 1.2])
        with head_brand:
            st.markdown(
                f"""<div style="display:flex;align-items:center;gap:8px;margin-top:2px;">
                    {_LOGO_SVG}
                    <div>
                        <div style="font-family:'Manrope','Inter',sans-serif;font-size:0.92rem;font-weight:700;color:#F3E9D2;letter-spacing:0.3px;">BIKEPULSE<span style="font-size:0.6rem;font-weight:600;color:#E5C07B;vertical-align:super;margin-left:2px;">AI</span></div>
                        <div style="font-family:'Inter',sans-serif;font-size:0.72rem;color:#8A9BB8;margin-top:1px;">Statistical Intelligence</div>
                    </div>
                </div>""",
                unsafe_allow_html=True
            )
        with head_close:
            st.button(
                "✕",
                key=f"close_drawer_{active_page}",
                on_click=close_nav_drawer,
                help="Close Navigation"
            )

        st.markdown('<div class="drawer-divider"></div>', unsafe_allow_html=True)

        # ── GENERAL ──────────────────────────────────────────────────────────
        st.markdown('<div class="drawer-section-label">General</div>', unsafe_allow_html=True)
        st.page_link("app.py", label="Dashboard", disabled=(active_page == "home"))
        st.page_link("pages/9_Demand_Prediction.py", label="Demand Predictor",
                     disabled=(active_page == "predictor"))
        st.page_link("pages/10_Reports_Planning.py", label="Reports & Planning",
                     disabled=(active_page == "about"))

        st.markdown('<div class="drawer-divider"></div>', unsafe_allow_html=True)

        # ── DATA & STATISTICS ─────────────────────────────────────────────
        st.markdown('<div class="drawer-section-label">Data & Statistics</div>', unsafe_allow_html=True)
        st.page_link("pages/1_Data_Management.py", label="Data Management",
                     disabled=(active_page == "data_mgmt"))
        st.page_link("pages/2_Exploratory_Analysis.py", label="Exploratory Analysis",
                     disabled=(active_page == "eda"))
        st.page_link("pages/3_Probability_Simulation.py", label="Probability Simulation",
                     disabled=(active_page == "prob_sim"))
        st.page_link("pages/4_Sampling_Estimation.py", label="Sampling & Estimation",
                     disabled=(active_page == "sampling"))
        st.page_link("pages/5_Hypothesis_Testing.py", label="Hypothesis Testing",
                     disabled=(active_page == "hypothesis"))
        st.page_link("pages/6_Correlation_Analysis.py", label="Correlation Analysis",
                     disabled=(active_page == "correlation"))

        st.markdown('<div class="drawer-divider"></div>', unsafe_allow_html=True)

        # ── MACHINE LEARNING ─────────────────────────────────────────────
        st.markdown('<div class="drawer-section-label">Machine Learning</div>', unsafe_allow_html=True)
        st.page_link("pages/7_Model_Training.py", label="Model Training",
                     disabled=(active_page == "training"))
        st.page_link("pages/8_Model_Comparison.py", label="Model Comparison",
                     disabled=(active_page == "comparison"))
        st.page_link("pages/9_Demand_Prediction.py", label="Demand Prediction",
                     disabled=(active_page == "predictor"))

        st.markdown('<div class="drawer-divider"></div>', unsafe_allow_html=True)

        # ── DATASET UPLOAD ────────────────────────────────────────────────
        with st.expander("Upload Custom Dataset", expanded=False):
            st.caption("Upload a UCI Bike Sharing-compatible hour.csv")
            uploaded = st.file_uploader(
                "Choose CSV file",
                type=["csv"],
                key=f"drawer_csv_{active_page}",
                label_visibility="collapsed"
            )
            if uploaded is not None:
                try:
                    from src.preprocessing import clean_dataframe
                    df_custom = clean_dataframe(pd.read_csv(uploaded))
                    st.session_state["df"] = df_custom
                    st.success(f"Loaded {len(df_custom):,} rows.")
                except Exception as e:
                    st.error(f"Upload error: {e}")

        st.markdown('<div class="drawer-divider"></div>', unsafe_allow_html=True)

        # ── INFO ──────────────────────────────────────────────────────────
        st.markdown(
            """<div style="font-size:0.76rem;color:#4A5A70;line-height:1.6;padding:0.4rem 0.7rem;font-family:'Inter',sans-serif;">
                UCI Bike Sharing Dataset · 2011–2012<br>
                Washington D.C., USA · 17,379 observations<br>
                11 Models · 56 Topics Verified
            </div>""",
            unsafe_allow_html=True
        )


# Backward compatibility alias
render_sidebar_drawer = render_navigation_drawer
