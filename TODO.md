# BIKEPULSE AI — TODO / Acceptance Checklist

> All entries are initially unchecked. **Do not tick an item before implementation + verification.**
> Project: Local Windows Python + Streamlit. **No Google Colab.**

## Progress summary
- Phases completed: **9 / 9**
- Coverage topics verified: **56 / 56** (70/70 pytest tests PASS, 26/26 visualization audits PASS, 13/13 runtime audits PASS, 7/7 navigation Playwright tests PASS)
- Models completed: **11 / 11** (6 regressors + 5 classifiers trained & evaluated, best saved to models/)
- Last update: Selected feature tags/chips contrast enhanced to Dark Charcoal #1F2937 (WCAG AAA compliant: 8.53:1 contrast ratio) with golden background preserved; subtle 3D layered background depth and refined glassmorphic cards implemented; verified across all 11 screens with 70/70 pytest tests passing.

## Execution phases

### Phase 0 — Audit, setup, and persistence ✅
- [x] Inspect the provided ZIP, practicals, assignments and report source
- [x] Create .venv using local Windows Python; requirements and reproducible install
- [x] Create source layout, local run instructions, .gitignore, README, configuration
- [x] Create TODO.md, BIKEPULSE_COVERAGE_MATRIX.csv, PROGRESS_LOG.md and PROJECT_STATE.md
- [x] Create first offline smoke test for app import and run command

### Phase 1 — Dataset/source/cleaning ✅
- [x] Read UCI hour.csv with checksum and schema validation (src/data_collection.py)
- [x] Implement requests+BeautifulSoup public-page metadata parser and local cached fallback
- [x] Parse HTML and display data source provenance; document robots/network limitations
- [x] Export cleaned CSV; show missing and duplicate audit (src/preprocessing.py)
- [x] Validate weather/date units, schema and edge-case handling

### Phase 2 — EDA/visualization ✅
- [x] Implement mean, median, mode, range, variance, std, quartiles and IQR
- [x] Build hourly/weekday/season/weather EDA filters and grouped KPI aggregations
- [x] Build histogram, box, bar, pie, scatter and line plots using real computed data
- [x] Implement reproducible chart export and data download

### Phase 3 — Probability & statistical sampling ✅
- [x] Implement Normal/Poisson diagnostic fits plus Binomial event model and labeled Uniform simulation
- [x] Implement four sampling schemes: simple random, systematic, season-stratified, day-cluster
- [x] Population vs sample statistics and sampling-distribution visualizations
- [x] CLT experiments for multiple sample sizes with seeded controls and dependence caveats
- [x] Point estimates, standard error, bootstrap and mean/median comparisons
- [x] Confidence intervals 90/95/99 percent and known-population coverage simulation

### Phase 4 — Statistical testing and relationships ✅
- [x] Create hypothesis controls for null/alternative, alpha and p-value conclusions
- [x] Compute one-sample t, Welch two-sample t, paired t, seasonal ANOVA, chi-square tests
- [x] Validate paired-date alignment, contingency expected counts, missingness and sample sufficiency
- [x] Compute covariance, Pearson, Spearman, their tests and correlation heatmap

### Phase 5 — Leakage-safe ML preparation ✅
- [x] Create valid input schema, data dictionary and true unit conversions
- [x] Define high-demand label threshold using training data only
- [x] Fit LabelEncoder, OneHotEncoder, MinMaxScaler and StandardScaler only on training subsets
- [x] Prepare engineered time/weather/calendar features; exclude leakage columns
- [x] Implement strictly chronological 70/15/15 train/validation/test split
- [x] Create feature selection/ablation on training data only

### Phase 6 — All ML models and evidence ✅
- [x] Build simple linear, multiple linear, ridge, lasso, decision-tree and random-forest regressors
- [x] Build logistic, decision-tree, random-forest, KNN and SVM classifiers
- [x] Train and compare 6+5 models on matched splits under fixed seed
- [x] Evaluate regression MAE, MSE, RMSE, R2 and classification Accuracy, Precision, Recall, F1, confusion matrix
- [x] Select best regression and classification models using validation-only rule
- [x] Save best complete pipelines using Joblib; verify reload parity

### Phase 7 — Connected Streamlit product ✅
- [x] Landing analytics overview with real KPIs and demand trend (app.py)
- [x] Create connected pages for Data, EDA, Probability, Sampling, Inference, Tests, Correlation
- [x] Create Model Training, Model Comparison, Prediction, Reports/Planning screens
- [x] Prediction form with weather, hour, calendar and measurement-unit checks
- [x] Only load saved models for inference; never retrain automatically
- [x] CSV import and model mismatch handling; graceful empty/failure states

### Phase 8 — Tests, reports, handoff ✅
- [x] Write pytest coverage for all 56 topics; link each checklist item to test
- [x] Run unit/integration/smoke checks (64/64 pytest PASS, 13/13 runtime PASS)
- [x] Generate actual model comparison exports and figures
- [x] Create Windows setup/start scripts (run_app.bat, run_tests.bat, train_models.bat)

## Mandatory coverage — 56 individual topics
- [x] **T01. Web Scraping** — `src/data_collection.py` — scrape_uci_metadata()
- [x] **T02. HTML Parsing** — `src/data_collection.py` — _parse_html()
- [x] **T03. Data Collection** — `src/data_collection.py` — load_hour_csv()
- [x] **T04. Data Cleaning** — `src/preprocessing.py` — clean_dataframe()
- [x] **T05. Missing/Duplicate Handling** — `src/preprocessing.py` — run_missing_duplicate_audit()
- [x] **T06. EDA** — `pages/2_Exploratory_Analysis.py`
- [x] **T07. Descriptive Statistics** — `src/descriptive_stats.py` — compute_descriptive_stats()
- [x] **T08. Data Visualization** — `pages/2_Exploratory_Analysis.py`
- [x] **T09. Probability Distributions** — `src/probability.py`
- [x] **T10. Random Sampling** — `src/sampling.py` — get_all_samples()
- [x] **T11. Population and Sample Statistics** — `src/sampling.py`
- [x] **T12. Sampling Distribution** — `src/sampling.py` — sampling_distribution()
- [x] **T13. Central Limit Theorem** — `src/sampling.py` — central_limit_theorem()
- [x] **T14. Point Estimation** — `src/statistical_inference.py`
- [x] **T15. Standard Error** — `src/statistical_inference.py`
- [x] **T16. Bootstrap** — `src/statistical_inference.py`
- [x] **T17. Confidence Intervals** — `src/statistical_inference.py`
- [x] **T18. Coverage Probability** — `src/statistical_inference.py`
- [x] **T19. Mean vs Median** — `src/statistical_inference.py`
- [x] **T20. Hypothesis Testing** — `src/hypothesis_tests.py`
- [x] **T21. Null/Alternative Hypothesis** — `src/hypothesis_tests.py`
- [x] **T22. P-Value** — `src/hypothesis_tests.py`
- [x] **T23. One-Sample T-Test** — `src/hypothesis_tests.py`
- [x] **T24. Two-Sample T-Test** — `src/hypothesis_tests.py`
- [x] **T25. Paired T-Test** — `src/hypothesis_tests.py`
- [x] **T26. One-Way ANOVA** — `src/hypothesis_tests.py`
- [x] **T27. Chi-Square** — `src/hypothesis_tests.py`
- [x] **T28. Covariance** — `src/correlation.py`
- [x] **T29. Pearson Correlation** — `src/correlation.py`
- [x] **T30. Spearman Correlation** — `src/correlation.py`
- [x] **T31. Correlation Hypothesis Testing** — `src/correlation.py`
- [x] **T32. Correlation Heatmap** — `pages/6_Correlation_Analysis.py`
- [x] **T33. Min-Max Normalization** — `src/feature_engineering.py`
- [x] **T34. Z-Score Standardization** — `src/feature_engineering.py`
- [x] **T35. Label Encoding** — `src/feature_engineering.py`
- [x] **T36. One-Hot Encoding** — `src/feature_engineering.py`
- [x] **T37. Feature Selection** — `src/feature_engineering.py`
- [x] **T38. Train-Test Split** — `src/feature_engineering.py`
- [x] **T39. Simple Linear Regression** — `src/regression_models.py`
- [x] **T40. Multiple Linear Regression** — `src/regression_models.py`
- [x] **T41. Ridge Regression** — `src/regression_models.py`
- [x] **T42. Lasso Regression** — `src/regression_models.py`
- [x] **T43. Decision Tree Regression** — `src/regression_models.py`
- [x] **T44. Random Forest Regression** — `src/regression_models.py`
- [x] **T45. Regression Evaluation** — `src/model_evaluation.py`
- [x] **T46. Logistic Regression** — `src/classification_models.py`
- [x] **T47. Decision Tree Classification** — `src/classification_models.py`
- [x] **T48. Random Forest Classification** — `src/classification_models.py`
- [x] **T49. KNN Classification** — `src/classification_models.py`
- [x] **T50. SVM Classification** — `src/classification_models.py`
- [x] **T51. Classification Evaluation** — `src/model_evaluation.py`
- [x] **T52. Multiple Model Comparison** — `src/model_training.py`
- [x] **T53. Best Model Selection** — `src/model_training.py`
- [x] **T54. Model Saving/Loading** — `src/model_persistence.py`
- [x] **T55. Streamlit GUI** — `app.py + pages/`
- [x] **T56. User Input Prediction** — `pages/9_Demand_Prediction.py`
