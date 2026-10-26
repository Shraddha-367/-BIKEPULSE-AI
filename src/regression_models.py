"""
T39 + T40 + T41 + T42 + T43 + T44 — Regression Models
=======================================================
Simple Linear, Multiple Linear, Ridge, Lasso,
Decision Tree, and Random Forest regressors.
All wrapped in sklearn Pipelines for leakage safety.
"""

import logging
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

RANDOM_STATE = 42


def build_simple_linear_regression(preprocessor=None) -> Pipeline:
    """
    T39 — Simple Linear Regression (single feature: temp).
    Returns a pipeline; preprocessor may be omitted if raw single feature supplied.
    """
    steps = []
    if preprocessor is not None:
        steps.append(("preprocessor", preprocessor))
    steps.append(("model", LinearRegression()))
    return Pipeline(steps)


def build_multiple_linear_regression(preprocessor) -> Pipeline:
    """T40 — Multiple Linear Regression (all engineered features)."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", LinearRegression()),
    ])


def build_ridge_regression(preprocessor, alpha: float = 1.0) -> Pipeline:
    """T41 — Ridge Regression (L2 regularisation)."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", Ridge(alpha=alpha, random_state=RANDOM_STATE)),
    ])


def build_lasso_regression(preprocessor, alpha: float = 0.1) -> Pipeline:
    """T42 — Lasso Regression (L1 regularisation, sparse features)."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", Lasso(alpha=alpha, max_iter=5000, random_state=RANDOM_STATE)),
    ])


def build_decision_tree_regression(preprocessor,
                                    max_depth: int = 12) -> Pipeline:
    """T43 — Decision Tree Regression."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", DecisionTreeRegressor(
            max_depth=max_depth,
            min_samples_leaf=10,
            random_state=RANDOM_STATE,
        )),
    ])


def build_random_forest_regression(preprocessor,
                                    n_estimators: int = 200,
                                    max_depth: int = None) -> Pipeline:
    """T44 — Random Forest Regression."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])


def get_all_regression_pipelines(preprocessor,
                                   simple_preprocessor=None) -> dict[str, Pipeline]:
    """
    Return all six regression pipelines ready for training (T52).
    simple_preprocessor: preprocessor for single-temp feature (T39).
    """
    return {
        "Simple Linear Regression": build_simple_linear_regression(simple_preprocessor),
        "Multiple Linear Regression": build_multiple_linear_regression(preprocessor),
        "Ridge Regression": build_ridge_regression(preprocessor),
        "Lasso Regression": build_lasso_regression(preprocessor),
        "Decision Tree Regression": build_decision_tree_regression(preprocessor),
        "Random Forest Regression": build_random_forest_regression(preprocessor),
    }
