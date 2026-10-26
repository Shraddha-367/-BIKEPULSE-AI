"""
Extract genuine model evaluation results, dataset statistics, confusion matrices,
and technical specifications for the Ramdeobaba University Semester V SI Lab Report.
"""
import sys
import json
import platform
from pathlib import Path
import pandas as pd
import numpy as np
import sklearn
import scipy
import streamlit
import plotly
import joblib

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_collection import load_hour_csv
from src.preprocessing import clean_dataframe
from src.feature_engineering import prepare_ml_data
from src.classification_models import get_all_classification_pipelines
from src.model_evaluation import evaluate_classification, evaluate_regression

def run_extraction():
    report_picture_dir = PROJECT_ROOT / "report_picture"
    report_picture_dir.mkdir(exist_ok=True, parents=True)

    # 1. Load authentic dataset
    raw_path = PROJECT_ROOT / "data" / "raw" / "hour.csv"
    raw_df = load_hour_csv(raw_path)
    clean_df = clean_dataframe(raw_df)

    # Dataset Statistics
    dataset_stats = {
        "dataset_name": "UCI Bike Sharing Dataset (Hourly)",
        "source": "UCI Machine Learning Repository / Capital Bikeshare Washington D.C.",
        "collection_period": "2011-01-01 to 2012-12-31",
        "total_records": int(len(clean_df)),
        "total_columns": int(len(clean_df.columns)),
        "columns_list": list(clean_df.columns),
        "missing_values_count": int(clean_df.isnull().sum().sum()),
        "duplicate_rows_count": int(clean_df.duplicated().sum()),
        "target_variable_regression": "cnt (hourly bike rental count)",
        "target_variable_classification": "high_demand (binary 0/1, threshold at 75th percentile of train data)",
        "regression_target_summary": {
            "mean": float(round(clean_df["cnt"].mean(), 2)),
            "median": float(round(clean_df["cnt"].median(), 2)),
            "std": float(round(clean_df["cnt"].std(), 2)),
            "min": int(clean_df["cnt"].min()),
            "max": int(clean_df["cnt"].max()),
            "q25": float(round(clean_df["cnt"].quantile(0.25), 2)),
            "q75": float(round(clean_df["cnt"].quantile(0.75), 2)),
            "iqr": float(round(clean_df["cnt"].quantile(0.75) - clean_df["cnt"].quantile(0.25), 2))
        }
    }

    # 2. Chronological ML split
    ml_data = prepare_ml_data(clean_df)
    train_df = ml_data["train_df"]
    val_df = ml_data["val_df"]
    test_df = ml_data["test_df"]
    preprocessor = ml_data["preprocessor"]
    all_feats = ml_data["all_feats"]

    splits_info = {
        "split_strategy": "Chronological Sequential Split (Strictly avoids temporal data leakage)",
        "train_set": {
            "records": int(len(train_df)),
            "percentage": round(len(train_df) / len(clean_df) * 100, 2),
            "date_range": f"{train_df['dteday'].min().strftime('%Y-%m-%d')} to {train_df['dteday'].max().strftime('%Y-%m-%d')}"
        },
        "validation_set": {
            "records": int(len(val_df)),
            "percentage": round(len(val_df) / len(clean_df) * 100, 2),
            "date_range": f"{val_df['dteday'].min().strftime('%Y-%m-%d')} to {val_df['dteday'].max().strftime('%Y-%m-%d')}"
        },
        "test_set": {
            "records": int(len(test_df)),
            "percentage": round(len(test_df) / len(clean_df) * 100, 2),
            "date_range": f"{test_df['dteday'].min().strftime('%Y-%m-%d')} to {test_df['dteday'].max().strftime('%Y-%m-%d')}"
        },
        "high_demand_threshold": float(ml_data["high_demand_threshold"]),
        "test_class_distribution": {
            "Low Demand (0)": int((ml_data["y_test_cls"] == 0).sum()),
            "High Demand (1)": int((ml_data["y_test_cls"] == 1).sum())
        }
    }

    # 3. Load existing evaluation results
    eval_dir = PROJECT_ROOT / "reports" / "evaluation"
    with open(eval_dir / "regression_results.json", "r") as f:
        reg_data = json.load(f)
    with open(eval_dir / "classification_results.json", "r") as f:
        cls_data = json.load(f)

    # 4. Extract comparison tables
    reg_val_df = pd.DataFrame(reg_data["all_val_results"])
    reg_test_df = pd.DataFrame(reg_data["all_test_results"])

    cls_val_df = pd.DataFrame(cls_data["all_val_results"])
    cls_test_df = pd.DataFrame(cls_data["all_test_results"])

    # Merge Validation and Test metrics into a comprehensive comparison table
    reg_comparison = pd.merge(
        reg_val_df[["model", "MAE", "MSE", "RMSE", "R2"]].rename(
            columns={"MAE": "Val_MAE", "MSE": "Val_MSE", "RMSE": "Val_RMSE", "R2": "Val_R2"}
        ),
        reg_test_df[["model", "MAE", "MSE", "RMSE", "R2"]].rename(
            columns={"MAE": "Test_MAE", "MSE": "Test_MSE", "RMSE": "Test_RMSE", "R2": "Test_R2"}
        ),
        on="model"
    ).sort_values("Test_R2", ascending=False).reset_index(drop=True)
    reg_comparison["Rank"] = reg_comparison.index + 1

    cls_comparison = pd.merge(
        cls_val_df[["model", "Accuracy", "Precision", "Recall", "F1"]].rename(
            columns={"Accuracy": "Val_Accuracy", "Precision": "Val_Precision", "Recall": "Val_Recall", "F1": "Val_F1"}
        ),
        cls_test_df[["model", "Accuracy", "Precision", "Recall", "F1"]].rename(
            columns={"Accuracy": "Test_Accuracy", "Precision": "Test_Precision", "Recall": "Test_Recall", "F1": "Test_F1"}
        ),
        on="model"
    ).sort_values("Test_F1", ascending=False).reset_index(drop=True)
    cls_comparison["Rank"] = cls_comparison.index + 1

    # Save CSVs
    reg_comparison_csv = report_picture_dir / "regression_models_comparison.csv"
    cls_comparison_csv = report_picture_dir / "classification_models_comparison.csv"
    reg_comparison.to_csv(reg_comparison_csv, index=False)
    cls_comparison.to_csv(cls_comparison_csv, index=False)
    print(f"Saved: {reg_comparison_csv}")
    print(f"Saved: {cls_comparison_csv}")

    # 5. Compute true held-out confusion matrices for all 5 classifiers
    print("Evaluating held-out classification confusion matrices...")
    cls_pipelines = get_all_classification_pipelines(preprocessor)
    confusion_matrices = {}

    for name, pipeline in cls_pipelines.items():
        pipeline.fit(train_df[all_feats], ml_data["y_train_cls"])
        y_test_pred = pipeline.predict(test_df[all_feats])
        eval_dict = evaluate_classification(ml_data["y_test_cls"], y_test_pred, name)
        cm = eval_dict["Confusion_Matrix"]  # [[TN, FP], [FN, TP]]
        tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]
        confusion_matrices[name] = {
            "matrix_2x2": cm,
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
            "accuracy": eval_dict["Accuracy"],
            "precision": eval_dict["Precision"],
            "recall": eval_dict["Recall"],
            "f1_score": eval_dict["F1"]
        }

    # Best classifier confusion matrix (Decision Tree Classifier)
    best_classifier_cm = confusion_matrices.get(cls_data["best_model"], {})

    # 6. Technical Environment & Library Versions
    env_versions = {
        "operating_system": platform.platform(),
        "python_version": sys.version.split()[0],
        "streamlit_version": streamlit.__version__,
        "pandas_version": pd.__version__,
        "numpy_version": np.__version__,
        "scikit_learn_version": sklearn.__version__,
        "scipy_version": scipy.__version__,
        "plotly_version": plotly.__version__,
        "joblib_version": joblib.__version__
    }

    # 7. Compile report_details.json
    report_details = {
        "project_title": "BIKEPULSE AI — Smart Bike Rental Demand Prediction, Statistical Intelligence & Resource Planning System",
        "academic_context": "Ramdeobaba University Semester V Statistical Inference Lab Project Report",
        "dataset_statistics": dataset_stats,
        "chronological_splits": splits_info,
        "environment_versions": env_versions,
        "regression_results": {
            "best_model": reg_data["best_model"],
            "selection_criterion": "Highest Validation R² (evaluated strictly on held-out test split)",
            "test_metrics": reg_data["best_test_metrics"],
            "all_models_ranked": reg_comparison.to_dict(orient="records")
        },
        "classification_results": {
            "best_model": cls_data["best_model"],
            "selection_criterion": "Highest Validation F1-score (evaluated strictly on held-out test split)",
            "test_metrics": cls_data["best_test_metrics"],
            "all_models_ranked": cls_comparison.to_dict(orient="records"),
            "best_model_confusion_matrix": best_classifier_cm,
            "all_models_confusion_matrices": confusion_matrices
        }
    }

    report_details_json = report_picture_dir / "report_details.json"
    with open(report_details_json, "w", encoding="utf-8") as f:
        json.dump(report_details, f, indent=2)
    print(f"Saved: {report_details_json}")

if __name__ == "__main__":
    run_extraction()
