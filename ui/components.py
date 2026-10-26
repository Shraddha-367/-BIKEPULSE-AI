"""
BIKEPULSE AI — Premium UI Components
Design System: Quiet Luxury + Modern Enterprise Analytics

Implements:
  - Hero section (Manrope typography, Gold accent, understated eyebrow)
  - Wide analytics preview (Navy glass, Gold line charts)
  - KPI stat cards (Royal Navy surface, strong value hierarchy)
  - Platform capabilities (clean feature cards)
  - Module explorer grid (consistent cards, no giant emoji)
  - How it works workflow steps (numbered, minimal)
  - About section (clean informational panels)
  - Footer (brand mark SVG, no emoji logo)
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from ui.theme import DARK_THEME, PLOT_BG, COLORS, CHART_PALETTE_HEX, apply_chart_theme


# ── Hero Section ───────────────────────────────────────────────────────────────
def render_hero_section():
    """Render premium hero section — Quiet Luxury design."""
    st.markdown("""
    <div class="hero-wrapper">
        <div class="hero-eyebrow-label">
            <span class="eyebrow-dot"></span>
            Urban Mobility Intelligence
        </div>
        <h1 class="hero-main-title">
            Understand Demand.<br><span class="gold-accent-text">Predict What Moves.</span>
        </h1>
        <p class="hero-subheading">
            Statistical intelligence and machine learning for smarter
            bike rental demand planning.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # CTA Buttons
    col_sl, col_primary, col_secondary, col_sr = st.columns([2.0, 2.2, 2.2, 2.0])
    with col_primary:
        if st.button("Launch Predictor", key="hero_cta_primary", type="primary",
                     use_container_width=True):
            st.switch_page("pages/9_Demand_Prediction.py")
    with col_secondary:
        if st.button("Explore Modules", key="hero_cta_secondary", type="secondary",
                     use_container_width=True):
            st.switch_page("pages/2_Exploratory_Analysis.py")

    # Technology metadata — understated, not noisy badges
    st.markdown("""
    <div class="tech-metadata-row">
        <div class="tech-meta-item">UCI Bike Sharing Dataset</div>
        <div class="tech-meta-item">Statistical Analysis</div>
        <div class="tech-meta-item">11 Machine Learning Models</div>
        <div class="tech-meta-item">17,379 Observations</div>
    </div>
    """, unsafe_allow_html=True)


# ── Wide Analytics Dashboard Preview ──────────────────────────────────────────
def render_wide_dashboard_preview(df: pd.DataFrame):
    """Render premium analytics preview with Navy glass container and Gold chart."""
    st.markdown("""
    <div class="preview-shell">
        <div class="preview-topbar">
            <div>
                <div class="preview-title-text">Historical Demand Overview — 2-Year Time Series</div>
                <div class="preview-subtitle-text">Capital Bikeshare · Washington D.C. · 2011–2012 Daily Total Rentals</div>
            </div>
            <div class="preview-status-pill">
                <span>●</span> 17,379 Records Verified
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Aggregated daily time-series
    daily = df.groupby("dteday")["cnt"].sum().reset_index()
    daily.columns = ["Date", "Total Rentals"]

    fig = go.Figure()

    # Primary series — Champagne Gold
    fig.add_trace(go.Scatter(
        x=daily["Date"],
        y=daily["Total Rentals"],
        mode="lines",
        name="Daily Total Rentals",
        line=dict(color=COLORS["chart_gold"], width=1.8),
        fill="tozeroy",
        fillcolor="rgba(229,192,123,0.08)",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Rentals: <b>%{y:,}</b><extra></extra>",
    ))

    # 14-day moving average — subtle cream/steel
    if len(daily) > 7:
        smooth = daily["Total Rentals"].rolling(14, center=True, min_periods=1).mean()
        fig.add_trace(go.Scatter(
            x=daily["Date"],
            y=smooth,
            mode="lines",
            name="14-day Moving Avg",
            line=dict(color=COLORS["chart_cream"], width=1.2, dash="dot"),
            hoverinfo="skip",
        ))

    apply_chart_theme(fig, height=300)
    fig.update_layout(
        hovermode="x unified",
        xaxis=dict(showgrid=False, tickformat="%b %Y"),
        yaxis=dict(showgrid=True, gridcolor="rgba(138,155,184,0.07)", title="Daily Rentals"),
        showlegend=True,
        margin=dict(l=12, r=12, t=8, b=8),
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Four KPI Stat Cards ────────────────────────────────────────────────────────
def render_four_stat_cards(df: pd.DataFrame, model_count: int = 11):
    """Render 4 horizontally aligned KPI cards — Royal Navy surface."""
    total_rentals = int(df["cnt"].sum())
    avg_hourly    = round(df["cnt"].mean(), 1)
    total_records = len(df)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card-box">
            <div class="stat-lbl-text">Total Historical Rentals</div>
            <div class="stat-val-text">{total_rentals:,}</div>
            <div class="stat-sub-text">2011–2012 · Capital Bikeshare</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card-box">
            <div class="stat-lbl-text">Average Hourly Demand</div>
            <div class="stat-val-text">{avg_hourly}</div>
            <div class="stat-sub-text">Bikes per hour, system-wide</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card-box">
            <div class="stat-lbl-text">Hourly Observations</div>
            <div class="stat-val-text">{total_records:,}</div>
            <div class="stat-sub-text">Complete 2-year dataset</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card-box">
            <div class="stat-lbl-text">ML Models Evaluated</div>
            <div class="stat-val-text stat-val-gold">{model_count}</div>
            <div class="stat-sub-text">6 Regressors · 5 Classifiers</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="margin-bottom:2.5rem;"></div>', unsafe_allow_html=True)


# ── Platform Capabilities ──────────────────────────────────────────────────────
def render_capabilities_section():
    """Render Platform Capabilities — three clean feature cards."""
    st.markdown("""
    <div class="section-heading-center">
        <div class="section-eyebrow">What It Does</div>
        <h2 class="section-title-large">Platform Capabilities</h2>
        <p class="section-subtitle-muted">
            End-to-end analytical framework from raw transit logs to production-grade ML inference.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    icon_chart = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 3v18h18"/><path d="M18 9l-5 5-4-4-3 3"/></svg>"""
    icon_math = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 19c3-1 5-13 10-13s7 12 10 13"/><line x1="2" y1="19" x2="22" y2="19"/></svg>"""
    icon_ai = """<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><circle cx="19" cy="5" r="2"/><circle cx="5" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/></svg>"""

    with col1:
        st.markdown(f"""
        <div class="capability-box">
            <div class="capability-icon-mark">{icon_chart}</div>
            <div class="capability-title">Analyze Historical Demand</div>
            <p class="capability-desc">
                Inspect 17,379 hourly observations across seasons, holidays and weather regimes.
                Calculate 14 descriptive parameters with multi-dimensional filtering.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="capability-box">
            <div class="capability-icon-mark">{icon_math}</div>
            <div class="capability-title">Understand Statistical Patterns</div>
            <p class="capability-desc">
                Fit probability models (Normal, Poisson, Binomial), test sampling schemes,
                simulate CLT convergence and execute hypothesis tests.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="capability-box">
            <div class="capability-icon-mark">{icon_ai}</div>
            <div class="capability-title">Predict Rental Demand</div>
            <p class="capability-desc">
                Evaluate 11 machine learning algorithms on strict chronological splits.
                Predict hourly rental counts and high-demand probability with automatic unit conversions.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="margin-bottom:2rem;"></div>', unsafe_allow_html=True)


# ── Module Explorer Grid ───────────────────────────────────────────────────────
def render_modules_grid():
    """Render all 10 modules in a clean two-column grid."""
    st.markdown("""
    <div class="section-heading-center" id="modules">
        <div class="section-eyebrow">Complete Coverage</div>
        <h2 class="section-title-large">Explore All 10 Modules</h2>
        <p class="section-subtitle-muted">
            Every statistical and machine learning topic implemented and verified.
        </p>
    </div>
    """, unsafe_allow_html=True)

    icon_data = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>"""
    icon_eda  = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>"""
    icon_prob = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 19c3-1 5-13 10-13s7 12 10 13"/><line x1="2" y1="19" x2="22" y2="19"/></svg>"""
    icon_samp = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>"""
    icon_test = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2v6a2 2 0 0 0 .5 1.5L20 15a4 4 0 0 1-3.5 6h-9A4 4 0 0 1 4 15l5.5-5.5A2 2 0 0 0 10 8V2"/><line x1="9" y1="2" x2="15" y2="2"/></svg>"""
    icon_corr = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>"""
    icon_trn  = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>"""
    icon_comp = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9H3a2 2 0 0 0-2 2v2a2 2 0 0 0 2 2h3"/><path d="M18 9h3a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2h-3"/><path d="M6 5h12v10a6 6 0 0 1-12 0V5z"/><line x1="12" y1="15" x2="12" y2="20"/><line x1="8" y1="20" x2="16" y2="20"/></svg>"""
    icon_pred = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/><circle cx="12" cy="12" r="4"/></svg>"""
    icon_plan = """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E5C07B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>"""

    modules = [
        {"icon": icon_data, "title": "Data Management",        "page": "pages/1_Data_Management.py",       "tag": "T01–T05", "desc": "Web scraping, HTML parsing, dataset schema validation, missing and duplicate auditing."},
        {"icon": icon_eda,  "title": "Exploratory Analysis",   "page": "pages/2_Exploratory_Analysis.py",  "tag": "T06–T08", "desc": "Interactive filters, 14 summary statistics, and 6 full visualization chart tabs."},
        {"icon": icon_prob, "title": "Probability Simulation",  "page": "pages/3_Probability_Simulation.py","tag": "T09",     "desc": "Normal, Poisson and Binomial distribution fitting against empirical transit data."},
        {"icon": icon_samp, "title": "Sampling & Estimation",   "page": "pages/4_Sampling_Estimation.py",   "tag": "T10–T19", "desc": "4 sampling schemes, CLT simulation, bootstrap confidence intervals and estimation."},
        {"icon": icon_test, "title": "Hypothesis Testing",      "page": "pages/5_Hypothesis_Testing.py",    "tag": "T20–T27", "desc": "One-sample, two-sample, paired t-tests, one-way ANOVA and chi-square significance testing."},
        {"icon": icon_corr, "title": "Correlation Analysis",    "page": "pages/6_Correlation_Analysis.py",  "tag": "T28–T32", "desc": "Pearson and Spearman heatmaps, covariance matrices and pairwise correlation tests."},
        {"icon": icon_trn,  "title": "Model Training",          "page": "pages/7_Model_Training.py",        "tag": "T33–T53", "desc": "Leakage-safe preprocessing, chronological 70/15/15 splits and 11-model orchestration."},
        {"icon": icon_comp, "title": "Model Comparison",        "page": "pages/8_Model_Comparison.py",      "tag": "T45, T51–T53", "desc": "Full leaderboard, dual-axis regression curves and classification metric comparisons."},
        {"icon": icon_pred, "title": "Demand Prediction",       "page": "pages/9_Demand_Prediction.py",     "tag": "T55–T56", "desc": "Real-time prediction form with weather, time and calendar inputs. Gauge and planning output."},
        {"icon": icon_plan, "title": "Reports & Planning",      "page": "pages/10_Reports_Planning.py",     "tag": "T55",     "desc": "Executive summary, model exports, operational planning guidance and CSV downloads."},
    ]

    for i in range(0, len(modules), 2):
        col1, col2 = st.columns(2)
        mod1 = modules[i]
        with col1:
            st.markdown(f"""
            <div class="module-item-card">
                <div class="module-icon-mark">{mod1['icon']}</div>
                <div class="module-tag-badge">{mod1['tag']}</div>
                <div class="module-title-text">{mod1['title']}</div>
                <div class="module-desc-text">{mod1['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link(mod1['page'], label=f"Open {mod1['title']}", use_container_width=True)

        if i + 1 < len(modules):
            mod2 = modules[i + 1]
            with col2:
                st.markdown(f"""
                <div class="module-item-card">
                    <div class="module-icon-mark">{mod2['icon']}</div>
                    <div class="module-tag-badge">{mod2['tag']}</div>
                    <div class="module-title-text">{mod2['title']}</div>
                    <div class="module-desc-text">{mod2['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.page_link(mod2['page'], label=f"Open {mod2['title']}", use_container_width=True)

    st.markdown('<div style="margin-bottom:2rem;"></div>', unsafe_allow_html=True)


# ── How It Works ───────────────────────────────────────────────────────────────
def render_how_it_works():
    """Render platform workflow steps — numbered, minimal."""
    st.markdown("""
    <div class="section-heading-center">
        <div class="section-eyebrow">The Process</div>
        <h2 class="section-title-large">How It Works</h2>
        <p class="section-subtitle-muted">
            A leakage-safe pipeline from raw transit logs to operational demand intelligence.
        </p>
    </div>
    """, unsafe_allow_html=True)

    steps = [
        ("01", "Data Ingestion",      "Raw UCI hour.csv validated with SHA-256 integrity and schema auditing."),
        ("02", "Cleaning Pipeline",   "Date parsing, chronological sort, range bounds and decoded unit columns."),
        ("03", "Statistical Analysis","Distribution fitting, sampling variance and hypothesis validation."),
        ("04", "Model Training",      "Chronological 70/15/15 splits; 6 regressors and 5 classifiers evaluated."),
        ("05", "Model Selection",     "Validation-only selection rule locks winning models to Joblib artifacts."),
        ("06", "Live Prediction",     "Operational form applies fitted transformations for real-time demand scoring."),
    ]

    for row_start in (0, 3):
        cols = st.columns(3)
        for idx, (num, title, desc) in enumerate(steps[row_start:row_start + 3]):
            with cols[idx]:
                st.markdown(f"""
                <div class="workflow-step-pill">
                    <div class="workflow-step-num">Step {num}</div>
                    <div class="workflow-step-title">{title}</div>
                    <div class="workflow-step-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('<div style="margin-bottom:0.8rem;"></div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-bottom:2.5rem;"></div>', unsafe_allow_html=True)


# ── About Section ──────────────────────────────────────────────────────────────
def render_about_section():
    """Render About section — clean informational panels."""
    st.markdown("""
    <div class="section-heading-center" id="about">
        <div class="section-eyebrow">Background</div>
        <h2 class="section-title-large">About BIKEPULSE AI</h2>
        <p class="section-subtitle-muted">
            Project context, data provenance, limitations and technology foundation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="capability-box">
            <div class="capability-title">Project & Dataset</div>
            <p class="capability-desc">
                BIKEPULSE AI is built on the <strong style="color:#D4C9B0;">UCI Machine Learning Repository
                Bike Sharing Dataset</strong> collected from Capital Bikeshare in Washington D.C.
                between January 2011 and December 2012. The system encompasses 17,379 hourly
                observations with weather and calendar events.
            </p>
            <p class="capability-desc" style="margin-top:0.7rem;">
                <strong style="color:#D4C9B0;">Citation:</strong> Fanaee-T, H., &amp; Gama, J. (2013).
                Event labeling combining ensemble detectors and background knowledge.
                <em>Progress in Artificial Intelligence.</em>
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="capability-box">
            <div class="capability-title">Scope &amp; Disclaimer</div>
            <p class="capability-desc">
                Predictions reflect historical 2011–2012 commuter behaviors and meteorological
                correlations. BIKEPULSE AI is designed as an analytical decision-support and
                educational system — not a live real-time sensor feed.
            </p>
            <p class="capability-desc" style="margin-top:0.7rem;">
                <strong style="color:#D4C9B0;">Technology:</strong> Python 3.11 &middot; Streamlit 1.39
                &middot; Plotly 5.24 &middot; Scikit-learn 1.5 &middot; SciPy 1.13 &middot; Pandas 2.2
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="margin-bottom:2rem;"></div>', unsafe_allow_html=True)


# ── Footer ─────────────────────────────────────────────────────────────────────
def render_footer():
    """Render premium footer — SVG brand mark, no emoji."""
    _LOGO_SVG_SMALL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 38 38" width="22" height="22">
      <circle cx="19" cy="19" r="13" fill="none" stroke="#E5C07B" stroke-width="2" stroke-dasharray="60 22" stroke-linecap="round"/>
      <polyline points="9,19 13,13 17,23 21,9 25,25 29,19" fill="none" stroke="#E5C07B" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="19" cy="19" r="2" fill="#E5C07B"/>
    </svg>"""

    st.markdown(f"""
    <div class="footer-glass">
        <div class="footer-brand-mark">
            {_LOGO_SVG_SMALL}
            <span class="footer-wordmark">BIKEPULSE</span>
            <span class="footer-ai-badge">AI</span>
        </div>
        <div class="footer-tagline">
            Smart Bike Rental Demand Prediction · Statistical Intelligence · Urban Resource Planning
        </div>
        <div class="footer-links-row">
            <span class="footer-link-item">Data: UCI Machine Learning Repository</span>
            <span class="footer-separator">·</span>
            <span class="footer-link-item">Washington D.C. Capital Bikeshare</span>
            <span class="footer-separator">·</span>
            <span class="footer-link-item">Python 3.11 &amp; Streamlit 1.39</span>
        </div>
        <div class="footer-copyright">
            Academic Data Science &amp; Machine Learning Implementation &middot; All 56 Topics Verified
        </div>
    </div>
    """, unsafe_allow_html=True)
