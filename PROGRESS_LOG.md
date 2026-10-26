# BIKEPULSE AI — Progress Log

## [2026-10-26 21:51] Phase 0 — Environment Setup
- **Action**: Created project directory `BIKEPULSE_AI/` and all subdirectories
- **Files**: src/, pages/, data/raw/, data/processed/, models/, reports/, tests/, scripts/
- **Commands**: `py -3 -m venv .venv`, `pip install -r requirements.txt`
- **Status**: venv created; requirements.txt pinned; packages installed (cache warnings only — harmless)

## [2026-10-26 21:52] Phase 0 — Package Installation
- **Packages**: pandas 2.2.3, numpy 1.26.4, scipy 1.13.1, scikit-learn 1.5.2, streamlit 1.39.0, plotly 5.24.1, requests 2.32.3, beautifulsoup4 4.12.3, joblib 1.4.2, pytest 8.3.3, statsmodels 0.14.4
- **Status**: All installed successfully. Python 3.11.9 confirmed.

## [2026-10-26 21:53] Phase 1 — Data Collection Module (T01-T03)
- **File**: `src/data_collection.py`
- **Functions**: `scrape_uci_metadata()`, `_fetch_and_parse()`, `_parse_html()`, `load_hour_csv()`, `compute_checksum()`, `get_data_provenance()`
- **T01**: Web scraping with requests + BeautifulSoup; polite 1s delay; robots compliance
- **T02**: HTML parsing extracting title, description, variable metadata
- **T03**: load_hour_csv() validates schema, audits cnt=casual+registered
- **Status**: IN_PROGRESS — tests pending

## [2026-10-26 21:54] Phase 1 — Preprocessing Module (T04-T05)
- **File**: `src/preprocessing.py`
- **Functions**: `clean_dataframe()`, `run_missing_duplicate_audit()`, `inject_synthetic_issues()`, `export_cleaned_csv()`
- **T04**: Date parsing, chronological sort, type casting, range validation, decoded columns
- **T05**: Missing value audit + synthetic fixture with 5 missing + 3 duplicates for testing
- **Status**: IN_PROGRESS

## [2026-10-26 21:55] Phase 2 — Descriptive Statistics (T07)
- **File**: `src/descriptive_stats.py`
- **Functions**: `compute_descriptive_stats()`, `compute_grouped_stats()`, `summarise_dataframe()`
- **Metrics**: count, mean, median, mode, std, variance, range, min, max, q1, q3, iqr, skewness, kurtosis
- **Status**: IN_PROGRESS

## [2026-10-26 21:55] Phase 3 — Probability Module (T09)
- **File**: `src/probability.py`
- **T09**: fit_normal (MLE + Shapiro-Wilk + K-S), fit_poisson (dispersion ratio), fit_binomial (high-demand event model), simulate_uniform (SYNTHETIC, clearly labeled)
- **Status**: IN_PROGRESS

## [2026-10-26 21:56] Phase 3 — Sampling Module (T10-T13)
- **File**: `src/sampling.py`
- **T10**: simple_random_sample, systematic_sample, stratified_sample, cluster_sample
- **T11**: population_vs_sample_stats() side-by-side comparison
- **T12**: sampling_distribution() 1000 iterations
- **T13**: central_limit_theorem() n=30/50/100/200 + Shapiro-Wilk normality
- **Status**: IN_PROGRESS

## [2026-10-26 21:57] Phase 3 — Statistical Inference (T14-T19)
- **File**: `src/statistical_inference.py`
- **T14**: point_estimates() — mean, median, proportion
- **T15**: standard_error() — IID + cluster-robust SE with caveats
- **T16**: bootstrap_estimate() — standard + block bootstrap
- **T17**: confidence_interval_mean() — 90/95/99% t-based intervals
- **T18**: coverage_probability_simulation() — SYNTHETIC labeled clearly
- **T19**: mean_vs_median_comparison() — real data + outlier simulation
- **Status**: IN_PROGRESS

## [2026-10-26 21:57] Phase 4 — Hypothesis Tests (T20-T27)
- **File**: `src/hypothesis_tests.py`
- **T20-T22**: hypothesis_test_meta() framework with H0/H1/statistic/p/decision/alpha
- **T23**: one_sample_ttest() — vs user-specified benchmark
- **T24**: two_sample_ttest() — Welch working vs non-working day
- **T25**: paired_ttest() — same-date morning vs evening (date-aligned)
- **T26**: one_way_anova() — 4 seasons + Levene test
- **T27**: chi_square_independence() — weathersit vs high_demand + expected count validation
- **Status**: IN_PROGRESS

## [2026-10-26 21:58] Phase 4 — Correlation (T28-T32)
- **File**: `src/correlation.py`
- **T28**: covariance_analysis() — full matrix + pairwise
- **T29**: pearson_correlation() — r, p, H0/H1, assumptions
- **T30**: spearman_correlation() — rho, p, non-parametric
- **T31**: correlation_hypothesis_tests() — 5 pairs, both methods
- **T32**: correlation_matrix() — for heatmap in page 6
- **Status**: IN_PROGRESS

## [2026-10-26 21:59] Phase 5 — Feature Engineering (T33-T38)
- **File**: `src/feature_engineering.py`
- **T33**: MinMaxScaler via build_preprocessor(scaler_type='minmax')
- **T34**: StandardScaler via build_preprocessor() default
- **T35**: encode_target() — 75th pct threshold from TRAINING ONLY
- **T36**: OneHotEncoder(handle_unknown='ignore') for cat features
- **T37**: add_engineered_features() + select_features_kbest() on train
- **T38**: chronological_split() 70/15/15 NO shuffle
- **Status**: IN_PROGRESS

## [2026-10-26 22:00] Phase 6 — Regression Models (T39-T44)
- **File**: `src/regression_models.py`
- **T39-T44**: All 6 regression pipelines implemented in sklearn Pipeline
- **Status**: IN_PROGRESS (pending training run)

## [2026-10-26 22:00] Phase 6 — Classification Models (T46-T50)
- **File**: `src/classification_models.py`
- **T46-T50**: All 5 classification pipelines implemented
- **Status**: IN_PROGRESS (pending training run)

## [2026-10-26 22:01] Phase 6 — Model Evaluation, Training, Persistence (T45, T51-T54)
- **Files**: `src/model_evaluation.py`, `src/model_training.py`, `src/model_persistence.py`
- **T45**: evaluate_regression() — MAE/MSE/RMSE/R²
- **T51**: evaluate_classification() — Acc/Prec/Rec/F1/CM
- **T52**: train_all_models() — all 11 models on matched chronological splits
- **T53**: best selection by validation R² (regression) and F1 (classification)
- **T54**: save_model() + load_model() + verify_reload() with SHA-256 + parity check
- **Status**: IN_PROGRESS (pending training run)

## [2026-10-26 22:02] Phase 7 — Streamlit Application (T55-T56)
- **Files**: `app.py`, `pages/1_Data_Management.py` through `pages/10_Reports_Planning.py`
- **T55**: 10 connected pages, dark-mode premium design, stateful session
- **T56**: validate_user_input() + predict_demand() with UCI unit normalization
- **T55**: 10 connected pages, dark-mode premium design, stateful session
- **T56**: validate_user_input() + predict_demand() with UCI unit normalization
- **Status**: COMPLETE

## [2026-10-26 22:45] Phase 8 — PyArrow / Plotly Compatibility & Visualization Audit
- **Issue 1**: `ImportError: pyarrow requires NumPy 2.0 or newer, found 1.26.4` across DataFrame views. Fixed by pinning `pyarrow==16.1.0`.
- **Issue 2**: `ValueError: Invalid value of type 'builtins.str' received for 'color' property of bar.marker: 'rgba(64b4ff,0.8)'` on Page 8 line 131 and Page 4 line 145.
- **Root Cause**: Naive string replacement `color.replace("#", "rgba(")...` converted hex string `#64b4ff` to invalid `rgba(64b4ff,0.8)` instead of decimal RGB values.
- **Fix**: Created centralized `hex_to_rgba(hex_color, alpha)` in `src/reporting.py`, exported in `src/__init__.py`. Replaced naive string replacements in `pages/8_Model_Comparison.py` and `pages/4_Sampling_Estimation.py`.
- **Audit**: Created `scripts/visualization_audit.py` testing all 26 Plotly charts across all pages with actual project data and JSON serialization: **26/26 PASS (100%)**.
- **Pytest**: Added `TestVisualizationAndPlotlyColors` in `tests/test_bikepulse.py`: **69/69 PASS (100%)**.
- **Live Verification**: Browser subagent verified `Model_Comparison` and `Sampling_Estimation` (CLT) pages; rendered cleanly without exceptions or console errors.
