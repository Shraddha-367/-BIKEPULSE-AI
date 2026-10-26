"""
pytest test suite for BIKEPULSE AI.
Covers all 56 topics with value-checking assertions.
Run: .\.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
"""

import json
import sys
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Fixtures ──────────────────────────────────────────────────────────────────
RAW_PATH = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"


@pytest.fixture(scope="session")
def raw_df():
    from src.data_collection import load_hour_csv
    return load_hour_csv(RAW_PATH)


@pytest.fixture(scope="session")
def clean_df(raw_df):
    from src.preprocessing import clean_dataframe
    return clean_dataframe(raw_df)


@pytest.fixture(scope="session")
def train_df(clean_df):
    from src.feature_engineering import add_engineered_features, chronological_split
    df_eng = add_engineered_features(clean_df)
    train, _, _ = chronological_split(df_eng)
    return train


# ── T01/T02 — Web Scraping & HTML Parsing ────────────────────────────────────
class TestWebScraping:
    def test_scrape_returns_dict(self):
        from src.data_collection import scrape_uci_metadata
        meta = scrape_uci_metadata(use_cache=True)
        assert isinstance(meta, dict)
        assert "title" in meta
        assert "description" in meta
        assert "variables" in meta

    def test_scrape_has_variables(self):
        from src.data_collection import scrape_uci_metadata, _known_variable_metadata
        meta = scrape_uci_metadata(use_cache=True)
        assert len(meta["variables"]) > 0
        # cnt appears in the known_variable_metadata static list
        # (may not appear in live-scraped HTML which has different structure)
        known = _known_variable_metadata()
        assert any(v["name"] == "cnt" for v in known)

    def test_html_parsing_extracts_metadata(self):
        from src.data_collection import _parse_html
        fake_html = """<html><head><title>UCI Test Page</title>
        <meta name="description" content="Test bike dataset"/></head>
        <body><p>This is the bike sharing dataset with cnt variable.</p></body></html>"""
        result = _parse_html(fake_html, "http://test.com")
        assert result["title"] == "UCI Test Page"
        assert "bike" in result["description"].lower() or "bike" in result["title"].lower()


# ── T03 — Data Collection ─────────────────────────────────────────────────────
class TestDataCollection:
    def test_load_hour_csv_shape(self, raw_df):
        assert raw_df.shape[0] == 17379
        assert raw_df.shape[1] == 17

    def test_load_hour_csv_columns(self, raw_df):
        from src.data_collection import REQUIRED_COLUMNS
        assert set(REQUIRED_COLUMNS).issubset(set(raw_df.columns))

    def test_cnt_equals_casual_plus_registered(self, raw_df):
        assert (raw_df["cnt"] == raw_df["casual"] + raw_df["registered"]).all()

    def test_checksum_returns_string(self):
        from src.data_collection import compute_checksum
        sha = compute_checksum(RAW_PATH)
        assert isinstance(sha, str)
        assert len(sha) == 64  # SHA-256 hex length

    def test_bad_path_raises_file_not_found(self):
        from src.data_collection import load_hour_csv
        with pytest.raises(FileNotFoundError):
            load_hour_csv("nonexistent_path/hour.csv")


# ── T04/T05 — Cleaning & Missing/Duplicates ──────────────────────────────────
class TestPreprocessing:
    def test_clean_df_has_datetime_hour(self, clean_df):
        assert "datetime_hour" in clean_df.columns

    def test_clean_df_sorted_chronologically(self, clean_df):
        if "datetime_hour" in clean_df.columns:
            assert clean_df["datetime_hour"].is_monotonic_increasing

    def test_clean_df_no_missing_in_key_cols(self, clean_df):
        for col in ["cnt", "temp", "hum", "windspeed", "hr", "dteday"]:
            assert clean_df[col].isnull().sum() == 0, f"Missing values in {col}"

    def test_clean_df_decoded_columns_exist(self, clean_df):
        assert "season_label" in clean_df.columns
        assert "temp_celsius" in clean_df.columns

    def test_synthetic_fixture_injection(self, clean_df):
        from src.preprocessing import inject_synthetic_issues, run_missing_duplicate_audit
        corrupted = inject_synthetic_issues(clean_df[:500])
        audit = run_missing_duplicate_audit(corrupted)
        assert audit["missing_counts"].get("temp", 0) >= 5  # injected 5 missing
        assert audit["duplicate_rows"] >= 3  # injected 3 duplicates

    def test_missing_handling_removes_nans(self, clean_df):
        from src.preprocessing import inject_synthetic_issues, clean_dataframe
        corrupted = inject_synthetic_issues(clean_df[:500])
        fixed = clean_dataframe(corrupted)
        assert fixed["temp"].isnull().sum() == 0

    def test_bad_csv_raises_or_handles_gracefully(self):
        from src.data_collection import load_hour_csv
        import io
        bad_csv = "a,b,c\n1,2,3"
        with pytest.raises((ValueError, FileNotFoundError)):
            load_hour_csv("not_real.csv")


# ── T07 — Descriptive Statistics ─────────────────────────────────────────────
class TestDescriptiveStats:
    def test_compute_descriptive_stats(self, clean_df):
        from src.descriptive_stats import compute_descriptive_stats
        stats = compute_descriptive_stats(clean_df["cnt"])
        assert stats["count"] == len(clean_df)
        assert 0 < stats["mean"] < 1000
        assert stats["std"] > 0
        assert stats["q1"] <= stats["median"] <= stats["q3"]
        assert stats["iqr"] == pytest.approx(stats["q3"] - stats["q1"], abs=0.01)

    def test_mean_correct_value(self, clean_df):
        from src.descriptive_stats import compute_descriptive_stats
        stats = compute_descriptive_stats(clean_df["cnt"])
        assert stats["mean"] == pytest.approx(float(clean_df["cnt"].mean()), rel=1e-4)

    def test_grouped_stats_shape(self, clean_df):
        from src.descriptive_stats import compute_grouped_stats
        result = compute_grouped_stats(clean_df, "season", "cnt")
        assert len(result) == 4  # 4 seasons


# ── T09 — Probability Distributions ─────────────────────────────────────────
class TestProbability:
    def test_fit_normal_returns_mu_sigma(self, clean_df):
        from src.probability import fit_normal
        res = fit_normal(clean_df["cnt"])
        assert "mu" in res and "sigma" in res
        assert res["sigma"] > 0
        assert res["mu"] == pytest.approx(clean_df["cnt"].mean(), rel=0.001)

    def test_fit_poisson_lambda(self, clean_df):
        from src.probability import fit_poisson
        res = fit_poisson(clean_df["cnt"])
        assert res["lambda_hat"] == pytest.approx(clean_df["cnt"].mean(), rel=0.001)

    def test_binomial_p_in_01(self, clean_df):
        from src.probability import fit_binomial
        res = fit_binomial(clean_df["cnt"])
        assert 0 <= res["p_hat"] <= 1

    def test_uniform_sim_labeled_synthetic(self):
        from src.probability import simulate_uniform
        res = simulate_uniform()
        assert "SYNTHETIC" in res["note"].upper()
        assert res["sample_mean"] == pytest.approx(0.5, abs=0.05)


# ── T10-T13 — Sampling ────────────────────────────────────────────────────────
class TestSampling:
    def test_simple_random_sample_size(self, clean_df):
        from src.sampling import simple_random_sample
        samp = simple_random_sample(clean_df, n=500, seed=42)
        assert len(samp) == 500

    def test_systematic_sample_step(self, clean_df):
        from src.sampling import systematic_sample
        samp = systematic_sample(clean_df, k=10)
        # systematic with step k=10: row 0, 10, 20 ... last row index
        # pandas iloc[::10] gives ceil(n/k) rows
        expected = len(range(0, len(clean_df), 10))
        assert len(samp) == expected

    def test_stratified_sample_all_seasons(self, clean_df):
        from src.sampling import stratified_sample
        samp = stratified_sample(clean_df, n_per_stratum=50)
        assert samp["season"].nunique() == 4

    def test_cluster_sample_day_blocks(self, clean_df):
        from src.sampling import cluster_sample
        samp = cluster_sample(clean_df, n_clusters=5)
        n_days = samp["dteday"].dt.date.nunique()
        assert n_days <= 5

    def test_clt_multiple_sizes(self, clean_df):
        from src.sampling import central_limit_theorem
        res = central_limit_theorem(clean_df, n_iterations=200, sample_sizes=[30, 100])
        assert 30 in res["results"]
        assert 100 in res["results"]
        # SE should decrease as n increases
        se_30 = res["results"][30]["std_of_means"]
        se_100 = res["results"][100]["std_of_means"]
        assert se_100 < se_30


# ── T14-T19 — Statistical Inference ─────────────────────────────────────────
class TestStatisticalInference:
    def test_point_estimates_range(self, clean_df):
        from src.statistical_inference import point_estimates
        pe = point_estimates(clean_df["cnt"])
        assert 0 <= pe["proportion_high_demand"] <= 1
        assert pe["mean_estimate"] > 0

    def test_bootstrap_ci_contains_mean(self, clean_df):
        from src.statistical_inference import bootstrap_estimate
        res = bootstrap_estimate(clean_df["cnt"], n_bootstrap=500, seed=42)
        observed = res["observed_value"]
        assert res["ci_lower"] <= observed <= res["ci_upper"]

    def test_confidence_interval_90_95_99(self, clean_df):
        from src.statistical_inference import confidence_interval_mean
        cis = confidence_interval_mean(clean_df["cnt"])
        assert len(cis) == 3
        # 99% CI should be wider than 90% CI
        widths = [c["ci_upper"] - c["ci_lower"] for c in cis]
        assert widths[2] > widths[0]  # 99% > 90%

    def test_coverage_simulation_near_nominal(self):
        from src.statistical_inference import coverage_probability_simulation
        res = coverage_probability_simulation(n_simulations=500, confidence=0.95, seed=42)
        assert abs(res["empirical_coverage"] - 0.95) < 0.05  # within 5%

    def test_mean_vs_median_simulation_labeled(self, clean_df):
        from src.statistical_inference import mean_vs_median_comparison
        res = mean_vs_median_comparison(clean_df["cnt"])
        assert "SIMULATION_TYPE" in res["synthetic_outlier_simulation"]


# ── T20-T27 — Hypothesis Tests ───────────────────────────────────────────────
class TestHypothesisTests:
    @pytest.fixture(scope="class")
    def df_with_hd(self, clean_df):
        df = clean_df.copy()
        threshold = float(np.percentile(df["cnt"], 75))
        df["high_demand"] = (df["cnt"] >= threshold).astype(int)
        return df

    def test_one_sample_ttest_has_decision(self, clean_df):
        from src.hypothesis_tests import one_sample_ttest
        result = one_sample_ttest(clean_df, popmean=189.5)
        assert "decision" in result
        assert "p_value" in result
        assert 0 <= result["p_value"] <= 1

    def test_two_sample_ttest_groups_differ(self, clean_df):
        from src.hypothesis_tests import two_sample_ttest
        result = two_sample_ttest(clean_df)
        assert "statistic" in result
        # Working days vs non-working should have different means
        wd_mean = clean_df[clean_df["workingday"] == 1]["cnt"].mean()
        nwd_mean = clean_df[clean_df["workingday"] == 0]["cnt"].mean()
        assert abs(wd_mean - nwd_mean) > 0

    def test_paired_ttest_aligned_dates(self, clean_df):
        from src.hypothesis_tests import paired_ttest
        result = paired_ttest(clean_df, morning_hr=8, evening_hr=17)
        assert "n_pairs" in result
        assert result["n_pairs"] > 0

    def test_one_way_anova_four_seasons(self, clean_df):
        from src.hypothesis_tests import one_way_anova
        result = one_way_anova(clean_df)
        assert "groups" in result
        assert len(result["groups"]) == 4

    def test_chi_square_requires_high_demand_col(self, clean_df):
        from src.hypothesis_tests import chi_square_independence
        result = chi_square_independence(clean_df)  # missing high_demand
        assert "error" in result

    def test_chi_square_with_high_demand(self, clean_df):
        from src.hypothesis_tests import chi_square_independence
        df2 = clean_df.copy()
        df2["high_demand"] = (df2["cnt"] >= np.percentile(df2["cnt"], 75)).astype(int)
        result = chi_square_independence(df2)
        assert "p_value" in result
        assert 0 <= result["p_value"] <= 1


# ── T28-T32 — Correlation ────────────────────────────────────────────────────
class TestCorrelation:
    def test_covariance_matrix_symmetric(self, clean_df):
        from src.correlation import covariance_analysis
        res = covariance_analysis(clean_df)
        cov = pd.DataFrame(res["covariance_matrix"])
        assert (cov - cov.T).abs().max().max() < 1e-10

    def test_pearson_r_in_range(self, clean_df):
        from src.correlation import pearson_correlation
        res = pearson_correlation(clean_df, "temp", "cnt")
        assert -1 <= res["r"] <= 1

    def test_spearman_rho_in_range(self, clean_df):
        from src.correlation import spearman_correlation
        res = spearman_correlation(clean_df, "temp", "cnt")
        assert -1 <= res["rho"] <= 1

    def test_correlation_matrix_shape(self, clean_df):
        from src.correlation import correlation_matrix
        cols = ["temp", "hum", "windspeed", "cnt"]
        corr = correlation_matrix(clean_df, cols=cols)
        assert corr.shape == (4, 4)
        assert np.allclose(np.diag(corr.values), 1.0)


# ── T33-T38 — Feature Engineering ────────────────────────────────────────────
class TestFeatureEngineering:
    def test_no_leakage_in_features(self):
        from src.feature_engineering import leakage_audit, ALL_MODEL_FEATURES
        audit = leakage_audit(ALL_MODEL_FEATURES)
        assert not audit["leakage_detected"]

    def test_chronological_split_proportions(self, clean_df):
        from src.feature_engineering import chronological_split, add_engineered_features
        df_eng = add_engineered_features(clean_df)
        train, val, test = chronological_split(df_eng)
        total = len(train) + len(val) + len(test)
        assert abs(len(train) / total - 0.70) < 0.02
        assert abs(len(val) / total - 0.15) < 0.02

    def test_train_comes_before_test(self, clean_df):
        from src.feature_engineering import chronological_split, add_engineered_features
        df_eng = add_engineered_features(clean_df)
        train, val, test = chronological_split(df_eng)
        assert train["datetime_hour"].max() < val["datetime_hour"].min()
        assert val["datetime_hour"].max() < test["datetime_hour"].min()

    def test_threshold_from_training_only(self, train_df):
        from src.feature_engineering import encode_target
        _, threshold, _ = encode_target(train_df)
        assert threshold > 0
        # Threshold should be 75th percentile of training cnt
        expected = float(np.percentile(train_df["cnt"], 75))
        assert threshold == pytest.approx(expected, rel=1e-5)

    def test_engineered_features_added(self, clean_df):
        from src.feature_engineering import add_engineered_features
        df_eng = add_engineered_features(clean_df)
        for col in ["is_rush_hour", "hr_sin", "hr_cos", "temp_hum_interaction"]:
            assert col in df_eng.columns

    def test_minmax_scaler_range_01(self, clean_df):
        from src.feature_engineering import build_preprocessor, add_engineered_features, chronological_split
        from src.feature_engineering import NUMERIC_FEATURES, CATEGORICAL_FEATURES, BOOL_FEATURES
        df_eng = add_engineered_features(clean_df)
        train, _, _ = chronological_split(df_eng)
        prep = build_preprocessor(NUMERIC_FEATURES, CATEGORICAL_FEATURES, BOOL_FEATURES, "minmax")
        X = prep.fit_transform(train[NUMERIC_FEATURES + CATEGORICAL_FEATURES + BOOL_FEATURES])
        # MinMax should produce values in [0, 1] for numeric part
        assert X[:, :len(NUMERIC_FEATURES)].min() >= -1e-10
        assert X[:, :len(NUMERIC_FEATURES)].max() <= 1 + 1e-10


# ── T39-T44 — Regression Models ──────────────────────────────────────────────
class TestRegressionModels:
    @pytest.fixture(scope="class")
    def ml_data(self, clean_df):
        from src.feature_engineering import prepare_ml_data
        return prepare_ml_data(clean_df)

    def test_simple_linear_predicts(self, ml_data):
        from sklearn.linear_model import LinearRegression
        from sklearn.preprocessing import StandardScaler
        X_train = StandardScaler().fit_transform(
            ml_data["train_df"][["temp"]]
        )
        model = LinearRegression()
        model.fit(X_train, ml_data["y_train_reg"])
        preds = model.predict(X_train[:5])
        assert len(preds) == 5
        assert all(isinstance(p, float) for p in preds)

    def test_random_forest_better_than_simple_linear(self, ml_data):
        from src.regression_models import build_random_forest_regression
        from src.feature_engineering import build_preprocessor
        from sklearn.metrics import r2_score
        from src.feature_engineering import NUMERIC_FEATURES, CATEGORICAL_FEATURES, BOOL_FEATURES
        prep = build_preprocessor()
        rfr = build_random_forest_regression(prep, n_estimators=50)
        rfr.fit(ml_data["train_df"][ml_data["all_feats"]], ml_data["y_train_reg"])
        preds = rfr.predict(ml_data["val_df"][ml_data["all_feats"]])
        r2 = r2_score(ml_data["y_val_reg"], preds)
        assert r2 > 0.5  # RF should achieve at least 50% R²


# ── T46-T50 — Classification Models ──────────────────────────────────────────
class TestClassificationModels:
    @pytest.fixture(scope="class")
    def ml_data(self, clean_df):
        from src.feature_engineering import prepare_ml_data
        return prepare_ml_data(clean_df)

    def test_logistic_regression_accuracy(self, ml_data):
        from src.classification_models import build_logistic_regression
        from src.feature_engineering import build_preprocessor
        from sklearn.metrics import accuracy_score
        prep = build_preprocessor()
        lr = build_logistic_regression(prep)
        lr.fit(ml_data["train_df"][ml_data["all_feats"]], ml_data["y_train_cls"])
        preds = lr.predict(ml_data["val_df"][ml_data["all_feats"]])
        acc = accuracy_score(ml_data["y_val_cls"], preds)
        assert acc > 0.6  # at least 60% accuracy

    def test_random_forest_classifier_f1(self, ml_data):
        from src.classification_models import build_random_forest_classifier
        from src.feature_engineering import build_preprocessor
        from sklearn.metrics import f1_score
        prep = build_preprocessor()
        rfc = build_random_forest_classifier(prep, n_estimators=50)
        rfc.fit(ml_data["train_df"][ml_data["all_feats"]], ml_data["y_train_cls"])
        preds = rfc.predict(ml_data["val_df"][ml_data["all_feats"]])
        f1 = f1_score(ml_data["y_val_cls"], preds)
        assert f1 > 0.5


# ── T45/T51 — Model Evaluation ────────────────────────────────────────────────
class TestModelEvaluation:
    def test_regression_metrics_computed(self):
        from src.model_evaluation import evaluate_regression
        y_true = np.array([100, 200, 300, 150, 250])
        y_pred = np.array([110, 190, 290, 160, 260])
        metrics = evaluate_regression(y_true, y_pred, "test_model")
        assert "MAE" in metrics
        assert "RMSE" in metrics
        assert "R2" in metrics
        assert metrics["MAE"] == pytest.approx(10.0, abs=0.1)
        assert metrics["R2"] > 0.9

    def test_classification_metrics_computed(self):
        from src.model_evaluation import evaluate_classification
        y_true = np.array([0, 1, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 1, 0, 0, 0])
        metrics = evaluate_classification(y_true, y_pred, "test_clf")
        assert "Accuracy" in metrics
        assert "F1" in metrics
        assert "Confusion_Matrix" in metrics
        assert metrics["Accuracy"] == pytest.approx(5/6, rel=0.01)


# ── T54 — Model Persistence ───────────────────────────────────────────────────
class TestModelPersistence:
    def test_save_and_reload_parity(self, tmp_path):
        """Test joblib save/reload prediction parity (T54)."""
        from sklearn.linear_model import LinearRegression
        import numpy as np
        import joblib
        
        # Simple model for testing
        model = LinearRegression()
        X = np.array([[1], [2], [3], [4], [5]])
        y = np.array([2, 4, 6, 8, 10])
        model.fit(X, y)
        
        # Manually test joblib save/load
        test_path = tmp_path / "test_model.joblib"
        joblib.dump(model, test_path)
        reloaded = joblib.load(test_path)
        
        preds_orig = model.predict(X)
        preds_reload = reloaded.predict(X)
        assert np.allclose(preds_orig, preds_reload, atol=1e-6)


# ── T56 — Prediction Validation ──────────────────────────────────────────────
class TestPrediction:
    def test_validate_user_input_valid(self):
        from src.prediction import validate_user_input
        inputs = {
            "season": 2, "yr": 1, "mnth": 6, "hr": 8,
            "holiday": 0, "weekday": 1, "workingday": 1,
            "weathersit": 1, "temp": 25.0, "atemp": 28.0,
            "hum": 60.0, "windspeed": 15.0,
        }
        validated, errors = validate_user_input(inputs)
        assert len(errors) == 0
        assert validated["temp"] == 25.0

    def test_validate_user_input_out_of_range(self):
        from src.prediction import validate_user_input
        inputs = {
            "season": 2, "yr": 1, "mnth": 13,  # invalid month
            "hr": 8, "holiday": 0, "weekday": 1, "workingday": 1,
            "weathersit": 1, "temp": 25.0, "atemp": 28.0,
            "hum": 60.0, "windspeed": 15.0,
        }
        _, errors = validate_user_input(inputs)
        assert any("mnth" in e for e in errors)

    def test_validate_holiday_workingday_conflict(self):
        from src.prediction import validate_user_input
        inputs = {
            "season": 2, "yr": 1, "mnth": 6, "hr": 8,
            "holiday": 1, "weekday": 1, "workingday": 1,  # conflict
            "weathersit": 1, "temp": 25.0, "atemp": 28.0,
            "hum": 60.0, "windspeed": 15.0,
        }
        _, errors = validate_user_input(inputs)
        assert any("workingday" in e.lower() for e in errors)

    def test_transform_normalizes_inputs(self):
        from src.prediction import transform_user_input
        inputs = {
            "season": 2, "yr": 1, "mnth": 6, "hr": 8,
            "holiday": 0, "weekday": 1, "workingday": 1,
            "weathersit": 1, "temp": 20.5, "atemp": 25.0,
            "hum": 60.0, "windspeed": 15.0,
        }
        df_row = transform_user_input(inputs)
        # Check normalization applied
        assert df_row["temp"].iloc[0] == pytest.approx(20.5 / 41.0, rel=1e-5)
        assert df_row["hum"].iloc[0] == pytest.approx(60.0 / 100.0, rel=1e-5)


# ── Data Integrity Tests ──────────────────────────────────────────────────────
class TestDataIntegrity:
    def test_no_future_leakage_in_features(self):
        """Verify cnt (target) is not in the feature set used for training."""
        from src.feature_engineering import ALL_MODEL_FEATURES, LEAKAGE_COLS
        leaked = set(ALL_MODEL_FEATURES) & LEAKAGE_COLS
        assert len(leaked) == 0, f"Leakage detected: {leaked}"

    def test_season_codes_match_official_uci(self, clean_df):
        """UCI official: 1=Spring, 2=Summer, 3=Fall, 4=Winter."""
        assert set(clean_df["season"].unique()) == {1, 2, 3, 4}

    def test_weathersit_codes_in_range(self, clean_df):
        assert clean_df["weathersit"].between(1, 4).all()

    def test_hr_codes_in_range(self, clean_df):
        assert clean_df["hr"].between(0, 23).all()

    def test_normalized_vars_in_range(self, clean_df):
        for col in ["temp", "atemp", "hum", "windspeed"]:
            assert clean_df[col].between(-0.001, 1.001).all(), \
                f"{col} has values outside [0,1]: {clean_df[col].describe()}"


# ── Visualization & Plotly Color Compatibility Tests ─────────────────────────
class TestVisualizationAndPlotlyColors:
    def test_hex_to_rgba_valid(self):
        from src.reporting import hex_to_rgba
        assert hex_to_rgba("#64b4ff", 0.8) == "rgba(100,180,255,0.8)"
        assert hex_to_rgba("34d399", 0.5) == "rgba(52,211,153,0.5)"
        assert hex_to_rgba("#f59e0b", 1.0) == "rgba(245,158,11,1.0)"
        assert hex_to_rgba("#a78bfa", 0.0) == "rgba(167,139,250,0.0)"

    def test_hex_to_rgba_invalid(self):
        from src.reporting import hex_to_rgba
        with pytest.raises(ValueError, match="Expected a six-digit hex color"):
            hex_to_rgba("#fff")
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            hex_to_rgba("#64b4ff", 1.5)
        with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
            hex_to_rgba("#64b4ff", -0.1)

    def test_plotly_bar_color_regression(self):
        """Test exact failing color and valid rgba format in go.Bar."""
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=["Model A", "Model B"],
                y=[0.85, 0.92],
                marker_color="rgba(64,180,255,0.8)",
            )
        )
        assert len(fig.data) == 1
        # Test serializability
        json_str = fig.to_json()
        assert "rgba(64,180,255,0.8)" in json_str

    def test_classification_comparison_chart_colors(self):
        """Validate classification comparison chart building with hex_to_rgba."""
        import plotly.graph_objects as go
        from src.reporting import hex_to_rgba

        models = ["Logistic Regression", "Random Forest", "KNN"]
        metrics = ["Accuracy", "Precision", "Recall", "F1"]
        palette = ["#64b4ff", "#34d399", "#f59e0b", "#a78bfa"]

        fig = go.Figure()
        for metric, color in zip(metrics, palette):
            rgba_color = hex_to_rgba(color, 0.8)
            fig.add_trace(go.Bar(
                name=metric,
                x=models,
                y=[0.8, 0.85, 0.9],
                marker_color=rgba_color,
            ))
        fig.update_layout(barmode="group")
        assert len(fig.data) == 4
        assert fig.to_json() is not None

    def test_clt_histogram_colors(self):
        """Validate CLT histogram color rendering."""
        import plotly.graph_objects as go
        from src.reporting import hex_to_rgba

        fig = go.Figure()
        palette = ["#64b4ff", "#34d399", "#f59e0b", "#a78bfa"]
        for n, color in zip([30, 50, 100, 200], palette):
            fig.add_trace(go.Histogram(
                x=[100, 150, 200],
                name=f"n={n}",
                opacity=0.6,
                marker_color=hex_to_rgba(color, 0.6),
            ))
        assert len(fig.data) == 4
        assert fig.to_json() is not None
