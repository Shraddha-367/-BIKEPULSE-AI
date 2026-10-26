# BIKEPULSE AI — README

## BIKEPULSE AI — Smart Bike Rental Demand Prediction

**Statistical Intelligence & Resource Planning System**  
Data: UCI Bike Sharing Dataset (2011–2012, Capital Bikeshare, Washington D.C.)

---

## Quick Start (Windows PowerShell)

```powershell
# 1. Create virtual environment
py -3 -m venv .venv

# 2. Install dependencies
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Train all 11 ML models (required before prediction page)
.\.venv\Scripts\python.exe scripts\train_models.py

# 4. Run tests
.\.venv\Scripts\python.exe -m pytest tests\ -v

# 5. Launch Streamlit app
.\.venv\Scripts\python.exe -m streamlit run app.py
```

---

## Project Structure

```
BIKEPULSE_AI/
  app.py                    # Main Streamlit app (T55 entry point)
  requirements.txt          # Pinned dependencies
  scripts/
    train_models.py         # Run once to train & save all 11 models
  src/
    data_collection.py      # T01, T02, T03 — web scraping, CSV loading
    preprocessing.py        # T04, T05 — cleaning, missing values
    descriptive_stats.py    # T07 — descriptive statistics
    probability.py          # T09 — distributions
    sampling.py             # T10-T13 — sampling, CLT
    statistical_inference.py # T14-T19 — bootstrap, CI, coverage
    hypothesis_tests.py     # T20-T27 — all hypothesis tests
    correlation.py          # T28-T32 — correlation analysis
    feature_engineering.py  # T33-T38 — encoding, scaling, splits
    regression_models.py    # T39-T44 — 6 regression models
    classification_models.py # T46-T50 — 5 classification models
    model_training.py       # T52-T53 — train all, select best
    model_evaluation.py     # T45, T51 — evaluation metrics
    model_persistence.py    # T54 — joblib save/load with parity check
    prediction.py           # T56 — user-input prediction
    reporting.py            # Export and planning utilities
  pages/
    1_Data_Management.py    # T01-T05
    2_Exploratory_Analysis.py # T06-T08
    3_Probability_Simulation.py # T09
    4_Sampling_Estimation.py   # T10-T19
    5_Hypothesis_Testing.py    # T20-T27
    6_Correlation_Analysis.py  # T28-T32
    7_Model_Training.py        # T33-T53
    8_Model_Comparison.py      # T45, T51-T53
    9_Demand_Prediction.py     # T55, T56
    10_Reports_Planning.py     # T55 planning
  tests/
    test_bikepulse.py      # Full pytest suite
  data/
    raw/hour.csv           # UCI original (read-only)
    processed/hour_clean.csv # Generated after first run
  models/                  # Saved .joblib artifacts
  reports/evaluation/      # JSON metrics output
```

---

## Coverage: 56 Topics + 11 ML Models

- **6 Regressors**: Simple Linear, Multiple Linear, Ridge, Lasso, Decision Tree, Random Forest  
- **5 Classifiers**: Logistic Regression, Decision Tree, Random Forest, KNN, SVM  
- **Statistical**: Descriptive stats, CLT, bootstrap, t-tests, ANOVA, chi-square, correlations  
- **Data**: Web scraping, cleaning, EDA, feature engineering with leakage prevention

---

## Data Provenance

Source: UCI Machine Learning Repository  
Citation: Fanaee-T, H. & Gama, J. (2013). *Event labeling combining ensemble detectors and background knowledge*. Progress in Artificial Intelligence. DOI: 10.1007/s13748-013-0040-3

---

## Local Development Notes

- Python 3.11 (Windows)  
- NO Google Colab, no `google.colab` imports  
- All preprocessing fit on training data only (no leakage)  
- Chronological train/val/test split (70/15/15), no shuffle  
- High-demand threshold derived from training target (75th pct) only  
- Models never retrained on Streamlit page reload
