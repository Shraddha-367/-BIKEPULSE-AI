"""
Page 7 — Model Training (T33–T53)
Train all 11 models, feature engineering, leakage audit.
"""

import sys
import json
import time
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_collection import load_hour_csv
from src.preprocessing import clean_dataframe
from src.feature_engineering import (
    add_engineered_features, chronological_split, encode_target,
    build_preprocessor, leakage_audit, NUMERIC_FEATURES, CATEGORICAL_FEATURES, BOOL_FEATURES
)
from src.model_training import train_all_models
from src.model_persistence import save_best_models
from src.model_evaluation import compare_regression_results, compare_classification_results

st.set_page_config(page_title="Model Training — BIKEPULSE AI", page_icon=":chart_with_upwards_trend:", layout="wide")

from ui.theme import inject_global_css, COLORS
from ui.navigation import render_top_navbar, render_sidebar_drawer
from ui.components import render_footer

inject_global_css()
render_top_navbar(active_page="training")
render_sidebar_drawer(active_page="training")

st.markdown("""
<div style="margin-bottom: 1.5rem;">
    <div style="font-family:'Inter',sans-serif;font-size:0.75rem;font-weight:600;letter-spacing:1px;color:#E5C07B;text-transform:uppercase;">T33 – T53 · Model Engineering</div>
    <h1 style="font-family:'Manrope',sans-serif;font-size:2rem;font-weight:700;color:#F3E9D2;margin:0.2rem 0 0.4rem 0;">Model Training Pipeline</h1>
    <p style="font-family:'Inter',sans-serif;font-size:0.92rem;color:#8A9BB8;margin:0;">Leakage-safe preprocessing, chronological 70/15/15 splits and 11-model orchestration.</p>
</div>
""", unsafe_allow_html=True)

MODELS_DIR = Path(__file__).parent.parent / "models"
EVAL_DIR = Path(__file__).parent.parent / "reports" / "evaluation"

@st.cache_data
def get_df():
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"
    return clean_dataframe(load_hour_csv(raw_path))

df = get_df()

# ── Feature Engineering Overview ─────────────────────────────────────────────
with st.expander("Feature Engineering Details (T33–T38)", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Numeric Features (StandardScaler — T34)**")
        st.code("\n".join(NUMERIC_FEATURES + ["hr_sin", "hr_cos", "mnth_sin", "mnth_cos", "temp_hum_interaction"]))
        
        st.markdown("**Categorical Features (OneHotEncoder — T36)**")
        st.code("\n".join(CATEGORICAL_FEATURES))
    
    with col2:
        st.markdown("**Boolean/Binary Features (passthrough)**")
        st.code("\n".join(BOOL_FEATURES + ["is_rush_hour", "is_night", "is_afternoon", "is_weekend"]))
        
        st.markdown("**Excluded (Leakage) Columns**")
        st.error("casual, registered, cnt (target), instant")
    
    # Leakage audit
    all_feats = NUMERIC_FEATURES + CATEGORICAL_FEATURES + BOOL_FEATURES
    audit = leakage_audit(all_feats)
    if not audit["leakage_detected"]:
        st.success("No leakage columns detected in feature set.")
    else:
        st.error(f"Leakage detected: {audit['leaked_columns']}")
    
    # Chronological split preview
    df_eng = add_engineered_features(df)
    train, val, test = chronological_split(df_eng)
    
    st.markdown("**Chronological Train/Val/Test Split (T38) — NO SHUFFLE**")
    split_df = pd.DataFrame([
        {"Split": "Train (70%)", "Rows": len(train),
         "Start": str(train["datetime_hour"].min())[:10],
         "End": str(train["datetime_hour"].max())[:10]},
        {"Split": "Validation (15%)", "Rows": len(val),
         "Start": str(val["datetime_hour"].min())[:10],
         "End": str(val["datetime_hour"].max())[:10]},
        {"Split": "Test (15%)", "Rows": len(test),
         "Start": str(test["datetime_hour"].min())[:10],
         "End": str(test["datetime_hour"].max())[:10]},
    ])
    st.dataframe(split_df, use_container_width=True, hide_index=True)
    
    # High-demand threshold
    _, threshold, le = encode_target(train)
    st.info(
        f"**High-Demand Threshold** (T35): **{threshold:.0f} rentals/hr** "
        f"(75th percentile of TRAINING target data only)"
    )

# ── Model Training Trigger ────────────────────────────────────────────────────
st.header("Train All 11 Models")

reg_json = EVAL_DIR / "regression_results.json"
cls_json = EVAL_DIR / "classification_results.json"
models_exist = list(MODELS_DIR.glob("best_*.joblib")) if MODELS_DIR.exists() else []

if models_exist and reg_json.exists() and cls_json.exists():
    st.success(f"Models already trained. Saved artifacts: {[m.stem for m in models_exist]}")
    retrain = st.checkbox("Force retrain (overwrite existing models)")
else:
    retrain = True
    st.warning("Models not yet trained. Click 'Train All Models' to begin.")

col_btn, col_info = st.columns([1, 2])
with col_btn:
    train_btn = st.button("Train All 11 Models", type="primary", disabled=not retrain)

with col_info:
    st.markdown("""
    **Training**: 6 regressors + 5 classifiers  
    **Selection**: Validation R² for regression, Validation F1 for classification  
    **Test**: Held-out test set used ONLY after best model selection  
    **Time**: ~2–5 minutes depending on hardware
    """)

if train_btn or (not models_exist and "training_results" not in st.session_state):
    progress_bar = st.progress(0, text="Initializing...")
    status_box = st.empty()
    
    try:
        status_box.info("Preparing ML data (feature engineering, splits)...")
        progress_bar.progress(10, "Preparing data...")
        
        start_time = time.time()
        status_box.info("Training all models (this may take 2-5 minutes)...")
        progress_bar.progress(20, "Training regression models...")
        
        results = train_all_models(df)
        progress_bar.progress(80, "Saving best models...")
        
        status_box.info("Saving best models with joblib...")
        saved_paths = save_best_models(results, results["ml_data"])
        
        progress_bar.progress(100, "Complete!")
        elapsed = time.time() - start_time
        
        st.session_state["training_results"] = results
        status_box.success(f"Training complete in {elapsed:.1f}s! "
                          f"Best regressor: **{results['regression']['best_model_name']}** | "
                          f"Best classifier: **{results['classification']['best_model_name']}**")
    
    except Exception as e:
        st.error(f"Training failed: {e}")
        import traceback
        st.code(traceback.format_exc())
        st.stop()

# ── Display Results ───────────────────────────────────────────────────────────
if reg_json.exists() and cls_json.exists():
    with open(reg_json) as f:
        reg_data = json.load(f)
    with open(cls_json) as f:
        cls_data = json.load(f)
    
    st.header("Training Results")
    
    tab1, tab2 = st.tabs(["Regression Models", "Classification Models"])
    
    with tab1:
        st.subheader("Regression — Validation Metrics")
        reg_val_df = pd.DataFrame(reg_data.get("all_val_results", []))
        if not reg_val_df.empty:
            reg_val_df = reg_val_df.sort_values("R2", ascending=False).reset_index(drop=True)
            st.dataframe(reg_val_df, use_container_width=True, hide_index=True)
        
        st.subheader("Best Regressor — Test Metrics")
        st.info(f"**Best Model**: {reg_data.get('best_model', 'N/A')}")
        best_reg_metrics = reg_data.get("best_test_metrics", {})
        if best_reg_metrics:
            m_cols = st.columns(4)
            m_cols[0].metric("MAE", f"{best_reg_metrics.get('MAE', 'N/A')}")
            m_cols[1].metric("RMSE", f"{best_reg_metrics.get('RMSE', 'N/A')}")
            m_cols[2].metric("R²", f"{best_reg_metrics.get('R2', 'N/A')}")
            m_cols[3].metric("n test", f"{best_reg_metrics.get('n', 'N/A'):,}" if isinstance(best_reg_metrics.get('n'), int) else "N/A")
    
    with tab2:
        st.subheader("Classification — Validation Metrics")
        cls_val_df = pd.DataFrame(cls_data.get("all_val_results", []))
        if not cls_val_df.empty:
            cls_val_df = cls_val_df.sort_values("F1", ascending=False).reset_index(drop=True)
            st.dataframe(cls_val_df, use_container_width=True, hide_index=True)
        
        st.subheader("Best Classifier — Test Metrics")
        st.info(f"**Best Model**: {cls_data.get('best_model', 'N/A')}")
        best_cls_metrics = cls_data.get("best_test_metrics", {})
        if best_cls_metrics:
            m_cols = st.columns(4)
            m_cols[0].metric("Accuracy", f"{best_cls_metrics.get('Accuracy', 'N/A')}")
            m_cols[1].metric("Precision", f"{best_cls_metrics.get('Precision', 'N/A')}")
            m_cols[2].metric("Recall", f"{best_cls_metrics.get('Recall', 'N/A')}")
            m_cols[3].metric("F1", f"{best_cls_metrics.get('F1', 'N/A')}")

elif not models_exist:
    st.info("Click **Train All 11 Models** above to start training.")

render_footer()
