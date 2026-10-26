"""
T46 + T47 + T48 + T49 + T50 — Classification Models
=====================================================
Logistic Regression, Decision Tree, Random Forest,
KNN, and SVM classifiers for binary high-demand prediction.
All wrapped in sklearn Pipelines with train-fit preprocessing.
"""

import logging
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)

RANDOM_STATE = 42


def build_logistic_regression(preprocessor) -> Pipeline:
    """T46 — Logistic Regression (binary high-demand classification)."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", LogisticRegression(
            max_iter=1000,
            random_state=RANDOM_STATE,
            solver="lbfgs",
            C=1.0,
        )),
    ])


def build_decision_tree_classifier(preprocessor,
                                    max_depth: int = 10) -> Pipeline:
    """T47 — Decision Tree Classifier."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_leaf=10,
            random_state=RANDOM_STATE,
        )),
    ])


def build_random_forest_classifier(preprocessor,
                                    n_estimators: int = 200) -> Pipeline:
    """T48 — Random Forest Classifier."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", RandomForestClassifier(
            n_estimators=n_estimators,
            min_samples_leaf=5,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])


def build_knn_classifier(preprocessor, n_neighbors: int = 7) -> Pipeline:
    """T49 — KNN Classifier (scaled numeric predictors via preprocessor)."""
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", KNeighborsClassifier(
            n_neighbors=n_neighbors,
            n_jobs=-1,
        )),
    ])


def build_svm_classifier(preprocessor) -> Pipeline:
    """
    T50 — SVM Classifier (SVC with train-fit scaling).

    probability=True enables predict_proba() for calibration analysis.
    NOTE: SVC probability calibration adds computation time (Platt scaling).
    """
    return Pipeline([
        ("preprocessor", preprocessor),
        ("model", SVC(
            kernel="rbf",
            C=1.0,
            gamma="scale",
            probability=True,
            random_state=RANDOM_STATE,
        )),
    ])


def get_all_classification_pipelines(preprocessor) -> dict[str, Pipeline]:
    """Return all five classification pipelines ready for training (T52)."""
    return {
        "Logistic Regression": build_logistic_regression(preprocessor),
        "Decision Tree Classifier": build_decision_tree_classifier(preprocessor),
        "Random Forest Classifier": build_random_forest_classifier(preprocessor),
        "KNN Classifier": build_knn_classifier(preprocessor),
        "SVM Classifier": build_svm_classifier(preprocessor),
    }
