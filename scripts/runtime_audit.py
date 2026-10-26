"""Phase 3 — Complete runtime audit of all data/logic operations across all pages."""
import sys, numpy as np, pandas as pd, traceback
sys.path.insert(0, '.')

from pathlib import Path

results = {}
errors = []

def test(name, fn):
    try:
        fn()
        results[name] = 'PASS'
        print(f'PASS  {name}')
    except Exception as e:
        results[name] = f'FAIL: {e}'
        errors.append((name, str(e)))
        print(f'FAIL  {name}: {e}')
        traceback.print_exc()

# ── Load data ─────────────────────────────────────────────────────────────────
from src.data_collection import load_hour_csv
from src.preprocessing import clean_dataframe

raw_path = Path('data/raw/hour.csv')
df_raw = load_hour_csv(raw_path)
df_clean = clean_dataframe(df_raw)
print(f'Data: {len(df_clean)} rows x {len(df_clean.columns)} cols\n')

# ── T01-T03 Data Collection ───────────────────────────────────────────────────
def test_data_collection():
    from src.data_collection import scrape_uci_metadata, get_data_provenance
    meta = scrape_uci_metadata(use_cache=True)
    assert 'title' in meta and 'variables' in meta
    prov = get_data_provenance(raw_path)
    assert 'sha256' in prov  # provenance dict has sha256 key
    assert Path('data/raw/hour.csv').exists()

test('T01-T03 data_collection', test_data_collection)

# ── T04-T05 Preprocessing ─────────────────────────────────────────────────────
def test_preprocessing():
    from src.preprocessing import run_missing_duplicate_audit, inject_synthetic_issues
    audit = run_missing_duplicate_audit(df_clean)
    assert audit['cnt_mismatch_rows'] == 0
    corrupted = inject_synthetic_issues(df_clean[:500])
    audit2 = run_missing_duplicate_audit(corrupted)
    assert audit2['missing_counts'].get('temp', 0) >= 5

test('T04-T05 preprocessing', test_preprocessing)

# ── T07 Descriptive Statistics ────────────────────────────────────────────────
def test_descriptive_stats():
    from src.descriptive_stats import compute_descriptive_stats, compute_grouped_stats, summarise_dataframe
    stats = compute_descriptive_stats(df_clean['cnt'])
    assert 'mean' in stats and 'iqr' in stats
    grp = compute_grouped_stats(df_clean, 'season', 'cnt')
    assert len(grp) == 4
    summary = summarise_dataframe(df_clean, cols=['cnt', 'temp'])
    assert not summary.empty

test('T07 descriptive_stats', test_descriptive_stats)

# ── T09 Probability ───────────────────────────────────────────────────────────
def test_probability():
    from src.probability import fit_normal, fit_poisson, fit_binomial, simulate_uniform
    n = fit_normal(df_clean['cnt'])
    assert n['sigma'] > 0
    p = fit_poisson(df_clean['cnt'])
    assert p['lambda_hat'] > 0
    b = fit_binomial(df_clean['cnt'])
    assert 0 <= b['p_hat'] <= 1
    u = simulate_uniform()
    assert 'SYNTHETIC' in u['note'].upper()

test('T09 probability', test_probability)

# ── T10-T13 Sampling ──────────────────────────────────────────────────────────
def test_sampling():
    from src.sampling import (get_all_samples, population_vs_sample_stats,
                               sampling_distribution, central_limit_theorem)
    samples = get_all_samples(df_clean, seed=42)
    assert len(samples) == 4
    comparison = population_vs_sample_stats(df_clean, samples['simple_random'], 'cnt')
    assert 'population' in comparison
    sd = sampling_distribution(df_clean, 'cnt', n_samples=100, sample_size=50, seed=42)
    assert len(sd['sampling_means']) == 100
    clt = central_limit_theorem(df_clean, n_iterations=100, sample_sizes=[30, 50])
    assert 30 in clt['results']

test('T10-T13 sampling', test_sampling)

# ── T14-T19 Statistical Inference ─────────────────────────────────────────────
def test_inference():
    from src.statistical_inference import (point_estimates, standard_error,
        bootstrap_estimate, confidence_interval_mean,
        coverage_probability_simulation, mean_vs_median_comparison)
    pe = point_estimates(df_clean['cnt'])
    assert 0 <= pe['proportion_high_demand'] <= 1
    se = standard_error(df_clean['cnt'])
    assert se['se_iid'] > 0
    boot = bootstrap_estimate(df_clean['cnt'], n_bootstrap=200, seed=42)
    assert boot['ci_lower'] <= boot['observed_value'] <= boot['ci_upper']
    cis = confidence_interval_mean(df_clean['cnt'])
    assert len(cis) == 3
    widths = [c['ci_upper'] - c['ci_lower'] for c in cis]
    assert widths[2] > widths[0]  # 99% wider than 90%
    cov = coverage_probability_simulation(n_simulations=200, confidence=0.95, seed=42)
    assert abs(cov['empirical_coverage'] - 0.95) < 0.06
    comp = mean_vs_median_comparison(df_clean['cnt'])
    assert 'SIMULATION_TYPE' in comp['synthetic_outlier_simulation']

test('T14-T19 inference', test_inference)

# ── T20-T27 Hypothesis Tests ──────────────────────────────────────────────────
def test_hypothesis():
    from src.hypothesis_tests import (one_sample_ttest, two_sample_ttest,
        paired_ttest, one_way_anova, chi_square_independence)
    df2 = df_clean.copy()
    df2['high_demand'] = (df2['cnt'] >= np.percentile(df2['cnt'], 75)).astype(int)

    r1 = one_sample_ttest(df_clean, popmean=189.5)
    assert 'decision' in r1 and 0 <= r1['p_value'] <= 1

    r2 = two_sample_ttest(df_clean)
    assert 'statistic' in r2

    r3 = paired_ttest(df_clean, morning_hr=8, evening_hr=17)
    assert 'n_pairs' in r3 and r3['n_pairs'] > 0

    r4 = one_way_anova(df_clean)
    assert 'groups' in r4 and len(r4['groups']) == 4

    r5 = chi_square_independence(df2)
    assert 'p_value' in r5 and 0 <= r5['p_value'] <= 1

test('T20-T27 hypothesis_tests', test_hypothesis)

# ── T28-T32 Correlation ───────────────────────────────────────────────────────
def test_correlation():
    from src.correlation import (covariance_analysis, pearson_correlation,
        spearman_correlation, correlation_hypothesis_tests, correlation_matrix)
    cov = covariance_analysis(df_clean)
    assert 'covariance_matrix' in cov
    pear = pearson_correlation(df_clean, 'temp', 'cnt')
    assert -1 <= pear['r'] <= 1
    spear = spearman_correlation(df_clean, 'temp', 'cnt')
    assert -1 <= spear['rho'] <= 1
    corr = correlation_matrix(df_clean, cols=['temp', 'hum', 'cnt'])
    assert corr.shape == (3, 3)
    pairs = correlation_hypothesis_tests(df_clean)
    assert len(pairs) > 0

test('T28-T32 correlation', test_correlation)

# ── T33-T38 Feature Engineering ───────────────────────────────────────────────
def test_feature_engineering():
    from src.feature_engineering import (add_engineered_features, chronological_split,
        encode_target, build_preprocessor, leakage_audit,
        ALL_MODEL_FEATURES, LEAKAGE_COLS, NUMERIC_FEATURES, CATEGORICAL_FEATURES, BOOL_FEATURES)
    audit = leakage_audit(ALL_MODEL_FEATURES)
    assert not audit['leakage_detected']
    df_eng = add_engineered_features(df_clean)
    assert 'hr_sin' in df_eng.columns and 'is_rush_hour' in df_eng.columns
    train, val, test = chronological_split(df_eng)
    assert train['datetime_hour'].max() < val['datetime_hour'].min()
    _, threshold, _ = encode_target(train)
    assert threshold == np.percentile(train['cnt'], 75)
    prep = build_preprocessor()
    X = prep.fit_transform(train[NUMERIC_FEATURES + CATEGORICAL_FEATURES + BOOL_FEATURES])
    assert X.shape[0] == len(train)

test('T33-T38 feature_engineering', test_feature_engineering)

# ── T39-T44 Regression Models ─────────────────────────────────────────────────
def test_regression():
    from src.feature_engineering import prepare_ml_data
    from src.regression_models import get_all_regression_pipelines
    from src.model_evaluation import evaluate_regression
    ml = prepare_ml_data(df_clean)
    pipes = get_all_regression_pipelines(ml['preprocessor'])
    assert len(pipes) == 6
    # Test one pipeline (Random Forest, fastest)
    rfr = pipes['Random Forest Regression']
    rfr.fit(ml['train_df'][ml['all_feats']], ml['y_train_reg'])
    preds = rfr.predict(ml['val_df'][ml['all_feats']])
    metrics = evaluate_regression(ml['y_val_reg'], preds, 'Random Forest')
    assert metrics['R2'] > 0.5

test('T39-T44 regression_models', test_regression)

# ── T46-T50 Classification Models ────────────────────────────────────────────
def test_classification():
    from src.feature_engineering import prepare_ml_data, build_preprocessor
    from src.classification_models import get_all_classification_pipelines
    from src.model_evaluation import evaluate_classification
    ml = prepare_ml_data(df_clean)
    cls_prep = build_preprocessor(ml['num_feats'], ml['cat_feats'], ml['bool_feats'])
    pipes = get_all_classification_pipelines(cls_prep)
    assert len(pipes) == 5
    lr = pipes['Logistic Regression']
    lr.fit(ml['train_df'][ml['all_feats']], ml['y_train_cls'])
    preds = lr.predict(ml['val_df'][ml['all_feats']])
    metrics = evaluate_classification(ml['y_val_cls'], preds, 'Logistic Regression')
    assert metrics['Accuracy'] > 0.6

test('T46-T50 classification_models', test_classification)

# ── T54 Model Persistence ─────────────────────────────────────────────────────
def test_model_persistence():
    from src.model_persistence import load_model, load_threshold, list_saved_models
    saved = list_saved_models()
    assert 'best_regressor' in saved and 'best_classifier' in saved
    reg_pipe, reg_meta = load_model('best_regressor')
    assert reg_meta.get('integrity_ok', True)  # True if sha matches
    cls_pipe, cls_meta = load_model('best_classifier')
    threshold = load_threshold()
    assert threshold > 0

test('T54 model_persistence', test_model_persistence)

# ── T56 Prediction ────────────────────────────────────────────────────────────
def test_prediction():
    from src.prediction import validate_user_input, predict_demand, transform_user_input
    inputs = {'season':2,'yr':1,'mnth':6,'hr':8,'holiday':0,'weekday':1,'workingday':1,
              'weathersit':1,'temp':25.0,'atemp':28.0,'hum':60.0,'windspeed':15.0}
    validated, errs = validate_user_input(inputs)
    assert len(errs) == 0
    df_row = transform_user_input(validated)
    assert abs(df_row['temp'].iloc[0] - 25.0/41.0) < 1e-6
    result = predict_demand(validated)
    assert 'error' not in result, f'Prediction error: {result.get("error")}'
    assert result['predicted_count'] >= 0

test('T56 prediction', test_prediction)

# ── Summary ───────────────────────────────────────────────────────────────────
print()
print('='*60)
print(f'PASS: {sum(1 for v in results.values() if v=="PASS")}/{len(results)}')
if errors:
    print('FAILURES:')
    for name, err in errors:
        print(f'  {name}: {err}')
else:
    print('ALL TESTS PASSED')
print('='*60)
