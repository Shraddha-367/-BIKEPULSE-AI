"""
Page 9 — Demand Prediction (T55, T56)
User-input-based predictions using saved best models.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.prediction import validate_user_input, predict_demand
from src.reporting import planning_recommendations

st.set_page_config(page_title="Demand Prediction — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS, apply_chart_theme
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="predictor")
render_sidebar_drawer(active_page="predictor")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T55 – T56 · Operational Intelligence</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Demand Prediction Workspace</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Real-time inference using saved winning models with calibrated meteorological transformations.</p>
</div>
""", unsafe_allow_html=True)

MODELS_DIR = Path(__file__).parent.parent / "models"
SEASON_LABELS = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
WEATHER_LABELS = {
    1: "Clear / Partly Cloudy",
    2: "Mist / Overcast",
    3: "Light Rain / Snow",
    4: "Heavy Rain / Severe Weather",
}

# Check model availability
models_exist = list(MODELS_DIR.glob("best_*.joblib")) if MODELS_DIR.exists() else []
if not models_exist:
    st.error(
        "No trained models found. Please go to **Model Training** and train the models first."
    )
    st.info("Navigate to: **Model Training** → Click **Train All 11 Models**")
    st.stop()

st.success(f"Production models verified: {[m.stem for m in models_exist]}")

# ── Input Form ────────────────────────────────────────────────────────────────
st.header("Input Conditions")

with st.form("prediction_form"):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Time Parameters**")
        season = st.selectbox("Season", [1, 2, 3, 4],
                               format_func=lambda x: SEASON_LABELS[x])
        yr = st.selectbox("Year", [0, 1],
                           format_func=lambda x: "2011" if x == 0 else "2012",
                           index=1)
        mnth = st.slider("Month", 1, 12, 6)
        hr = st.slider("Hour of Day", 0, 23, 8)
    
    with col2:
        st.markdown("**Weather Conditions**")
        weathersit = st.selectbox("Weather Situation", [1, 2, 3, 4],
                                   format_func=lambda x: WEATHER_LABELS[x])
        temp_c = st.slider("Temperature (°C)", 0.0, 41.0, 20.0, step=0.5,
                            help="Real temperature in Celsius (normalized to 0-1 internally)")
        atemp_c = st.slider("Feeling Temperature (°C)", 0.0, 50.0, 22.0, step=0.5)
        hum_pct = st.slider("Humidity (%)", 0.0, 100.0, 60.0, step=1.0)
        windspeed_kmh = st.slider("Wind Speed (km/h)", 0.0, 67.0, 15.0, step=0.5)
    
    with col3:
        st.markdown("**Calendar & Day Type**")
        weekday = st.selectbox("Day of Week", list(range(7)),
                                format_func=lambda x: ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"][x])
        holiday = st.radio("Holiday?", [0, 1], format_func=lambda x: "Yes" if x else "No",
                            horizontal=True)
        
        # Auto-derive workingday
        if holiday == 1 or weekday in [0, 6]:
            workingday = 0
            st.info("Auto-derived: Non-working day (weekend or holiday)")
        else:
            workingday = 1
            st.info("Auto-derived: Working day")
    
    submit = st.form_submit_button("Generate Demand Prediction", type="primary", use_container_width=True)

# ── Prediction Output ─────────────────────────────────────────────────────────
if submit:
    raw_inputs = {
        "season": season, "yr": yr, "mnth": mnth, "hr": hr,
        "holiday": holiday, "weekday": weekday, "workingday": workingday,
        "weathersit": weathersit,
        "temp": temp_c, "atemp": atemp_c,
        "hum": hum_pct, "windspeed": windspeed_kmh,
    }
    
    # Validate inputs
    validated, errors = validate_user_input(raw_inputs)
    
    if errors:
        for err in errors:
            st.error(f"Validation Error: {err}")
    else:
        with st.spinner("Running prediction with saved models..."):
            result = predict_demand(validated)
        
        if "error" in result:
            st.error(f"Prediction failed: {result['error']}")
            if "suggestion" in result:
                st.info(result["suggestion"])
        else:
            st.markdown("---")
            st.header("Prediction Results")
            
            # Main metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(
                "Predicted Rental Count",
                f"{result['predicted_count']:.0f} bikes/hr",
                help="Regression model output",
            )
            col2.metric("Demand Category", result["demand_category"])
            
            if result["high_demand_probability"] != "N/A":
                col3.metric("P(High Demand)", f"{result['high_demand_probability']:.1%}")
            col4.metric("High-Demand Threshold", f"{result['high_demand_threshold']:.0f} bikes/hr")
            
            # Context
            st.markdown("---")
            context_col1, context_col2 = st.columns(2)
            with context_col1:
                st.markdown("**Prediction Context**")
                st.markdown(f"- **Season**: {result['season']}")
                st.markdown(f"- **Weather**: {result['weather']}")
                st.markdown(f"- **Hour**: {result['hour']}:00")
                st.markdown(f"- **Working Day**: {'Yes' if result['is_working_day'] else 'No'}")
            
            with context_col2:
                st.markdown("**Model Provenance**")
                st.markdown(f"- **Regressor**: {result['regressor_used']}")
                st.markdown(f"- **Classifier**: {result['classifier_used']}")
                st.markdown(f"- **Regressor Test R²**: {result['regressor_test_r2']}")
                st.markdown(f"- **Classifier Test F1**: {result['classifier_test_f1']}")
                st.markdown(f"- **Trained on data from**: {result.get('model_trained_on', 'N/A')[:10]}")
            
            # Planning recommendations
            st.markdown("---")
            st.header("Planning Recommendations")
            season_map_rev = {v: k for k, v in 
                              {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}.items()}
            recs = planning_recommendations(
                result["predicted_count"],
                result["high_demand_threshold"],
                result["hour"],
                result["season"],
            )
            for rec in recs:
                st.markdown(rec)
            
            # Gauge chart
            is_high = result["demand_category"] == "High Demand"
            gauge_color = COLORS["chart_gold"] if is_high else COLORS["chart_steel"]
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=result["predicted_count"],
                delta={"reference": result["high_demand_threshold"],
                       "font": {"color": COLORS["text_secondary"]}},
                gauge={
                    "axis": {"range": [0, 1000], "tickcolor": COLORS["text_muted"],
                             "tickfont": {"color": COLORS["text_muted"]}},
                    "bar": {"color": gauge_color},
                    "bgcolor": "rgba(27,38,59,0.6)",
                    "borderwidth": 1,
                    "bordercolor": COLORS["glass_border"],
                    "steps": [
                        {"range": [0, result["high_demand_threshold"]], "color": "rgba(27,38,59,0.7)"},
                        {"range": [result["high_demand_threshold"], 1000], "color": "rgba(229,192,123,0.15)"},
                    ],
                    "threshold": {
                        "line": {"color": COLORS["chart_gold"], "width": 3},
                        "thickness": 0.75,
                        "value": result["high_demand_threshold"],
                    },
                },
                title={"text": "Predicted Rentals/Hour",
                       "font": {"color": COLORS["text_primary"], "family": "Manrope, Inter, sans-serif"}},
                number={"font": {"color": gauge_color, "size": 48}},
            ))
            apply_chart_theme(fig, height=320)
            fig.update_layout(margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            st.caption(result.get("note", ""))

# ── Input Guide ───────────────────────────────────────────────────────────────
with st.expander("Input Guide & Variable Measurement Units", expanded=False):
    st.markdown("""
    | Field | Unit in Form | Internal Representation | Range |
    |-------|-------------|------------------------|-------|
    | Temperature | °C | Normalized ÷ 41 | 0–41°C |
    | Feeling Temp | °C | Normalized ÷ 50 | 0–50°C |
    | Humidity | % | Normalized ÷ 100 | 0–100% |
    | Wind Speed | km/h | Normalized ÷ 67 | 0–67 km/h |
    | Season | 1-4 | Categorical (OHE) | 1=Spring, 2=Summer, 3=Fall, 4=Winter |
    | Weather | 1-4 | Categorical (OHE) | 1=Clear, 2=Mist, 3=Rain, 4=Heavy |
    
    **Important notes:**
    - Predictions are based on 2011–2012 Capital Bikeshare historical patterns.
    - This is an analytical decision-support workspace.
    - `workingday` is derived automatically from holiday and weekday inputs.
    """)

render_footer()
