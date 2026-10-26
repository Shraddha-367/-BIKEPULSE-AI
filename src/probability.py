"""
T09 — Probability Distributions: Normal, Uniform, Binomial, Poisson
====================================================================
Fit distributions to REAL bike rental data where applicable.
Simulations are clearly labelled; no synthetic data overwrites real history.
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats as scipy_stats
from scipy.stats import norm, poisson, binom, uniform

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Normal Distribution
# ---------------------------------------------------------------------------
def fit_normal(series: pd.Series) -> dict:
    """
    Fit Normal distribution to a numeric series (T09).

    Returns MLE mean and std plus Shapiro-Wilk and K-S goodness-of-fit.
    """
    s = series.dropna().values
    mu, sigma = norm.fit(s)

    # Shapiro-Wilk (limited to 5000 samples for speed)
    sw_stat, sw_p = scipy_stats.shapiro(s[:5000] if len(s) > 5000 else s)

    # K-S test against fitted normal
    ks_stat, ks_p = scipy_stats.kstest(s, "norm", args=(mu, sigma))

    return {
        "distribution": "Normal",
        "mu": float(mu),
        "sigma": float(sigma),
        "shapiro_stat": float(sw_stat),
        "shapiro_p": float(sw_p),
        "ks_stat": float(ks_stat),
        "ks_p": float(ks_p),
        "is_normal_p05": bool(sw_p > 0.05),
        "note": (
            "Demand data is typically right-skewed; Normal is an approximation. "
            "Shapiro-Wilk p<0.05 indicates non-normality."
        ),
    }


# ---------------------------------------------------------------------------
# Poisson Distribution
# ---------------------------------------------------------------------------
def fit_poisson(series: pd.Series) -> dict:
    """
    Fit Poisson distribution to integer count data (T09).

    Reports mean/variance ratio to check Poisson assumption (equidispersion).
    """
    s = series.dropna().values.astype(int)
    mu_hat = float(np.mean(s))
    var_hat = float(np.var(s, ddof=1))
    dispersion_ratio = var_hat / mu_hat if mu_hat > 0 else float("nan")

    return {
        "distribution": "Poisson",
        "lambda_hat": mu_hat,
        "sample_variance": var_hat,
        "dispersion_ratio": dispersion_ratio,
        "is_equidispersed": bool(0.5 < dispersion_ratio < 2.0),
        "note": (
            f"Dispersion ratio = Var/Mean = {dispersion_ratio:.2f}. "
            "Ratio >> 1 indicates overdispersion; Poisson may underfit. "
            "Negative Binomial would be a safer model for count regression."
        ),
    }


# ---------------------------------------------------------------------------
# Binomial Distribution — High-Demand Event Model
# ---------------------------------------------------------------------------
def fit_binomial(series: pd.Series, threshold: float | None = None,
                 n_trials: int | None = None) -> dict:
    """
    Model the probability of a 'high-demand' event (T09).

    Parameters
    ----------
    series : pd.Series
        Hourly count series.
    threshold : float | None
        High-demand threshold. If None, uses 75th percentile.
    n_trials : int | None
        Number of Bernoulli trials per experiment. Default = 24 (hours/day).
    """
    s = series.dropna()
    if threshold is None:
        threshold = float(np.percentile(s, 75))
    if n_trials is None:
        n_trials = 24  # one observation per hour per day

    p_hat = float((s >= threshold).mean())
    n = n_trials

    return {
        "distribution": "Binomial",
        "n": n,
        "p_hat": p_hat,
        "threshold_cnt": threshold,
        "expected_high_demand_hours": round(n * p_hat, 2),
        "pmf_values": [float(binom.pmf(k, n, p_hat)) for k in range(n + 1)],
        "note": (
            f"Threshold = {threshold:.0f} rentals/hr (75th percentile). "
            f"P(high demand) = {p_hat:.3f}. "
            "Each hourly observation treated as independent Bernoulli trial — "
            "temporal dependence means strict independence does not hold; "
            "treat as an illustrative model."
        ),
    }


# ---------------------------------------------------------------------------
# Uniform Distribution — Clearly Labeled Simulation
# ---------------------------------------------------------------------------
def simulate_uniform(n_samples: int = 10000, low: float = 0.0,
                     high: float = 1.0, seed: int = 42) -> dict:
    """
    Generate a labeled Uniform simulation (T09).

    NOTE: This is a synthetic simulation for illustrative purposes only.
    Uniform is NOT fitted to bike-demand data; it serves as a probability
    distribution demonstration for the statistics curriculum.
    """
    rng = np.random.default_rng(seed)
    samples = rng.uniform(low=low, high=high, size=n_samples)
    return {
        "distribution": "Uniform [Simulation]",
        "low": low,
        "high": high,
        "n_samples": n_samples,
        "theoretical_mean": (low + high) / 2,
        "sample_mean": float(samples.mean()),
        "theoretical_std": (high - low) / (12 ** 0.5),
        "sample_std": float(samples.std()),
        "samples": samples,
        "note": (
            "SYNTHETIC SIMULATION — not fitted to real demand data. "
            "Used to illustrate the Uniform distribution concept."
        ),
    }


# ---------------------------------------------------------------------------
# Combined Distribution Summary
# ---------------------------------------------------------------------------
def distribution_summary(df: pd.DataFrame, target: str = "cnt",
                         high_demand_threshold: float | None = None) -> dict:
    """Return all four distribution fits/simulations for the target column."""
    s = df[target]
    return {
        "normal": fit_normal(s),
        "poisson": fit_poisson(s),
        "binomial": fit_binomial(s, threshold=high_demand_threshold),
        "uniform": simulate_uniform(),
    }
