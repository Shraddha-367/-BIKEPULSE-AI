"""
Script: train_models.py
Trains all 11 ML models, saves best artifacts, exports evaluation reports.
Run from project root: .\.venv\Scripts\python.exe scripts\train_models.py
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    from src.data_collection import load_hour_csv
    from src.preprocessing import clean_dataframe, export_cleaned_csv
    from src.model_training import train_all_models
    from src.model_persistence import save_best_models
    from src.reporting import export_summary_report

    # Load and clean data
    raw_path = Path(__file__).parent.parent / "data" / "raw" / "hour.csv"
    logger.info("Loading hour.csv...")
    df_raw = load_hour_csv(raw_path)
    df_clean = clean_dataframe(df_raw)

    # Export cleaned CSV
    export_cleaned_csv(df_clean)

    # Train all models
    logger.info("Starting training of all 11 models...")
    results = train_all_models(df_clean)

    # Save best models
    logger.info("Saving best model artifacts...")
    saved = save_best_models(results, results["ml_data"])

    # Export summary report
    report_path = export_summary_report(
        results["regression"]["val_results"],
        results["classification"]["val_results"],
    )

    # Print summary
    print("\n" + "=" * 60)
    print("BIKEPULSE AI — Training Complete")
    print("=" * 60)
    print(f"\nBest Regressor:  {results['regression']['best_model_name']}")
    best_reg = results["regression"]["best_model_test_metrics"]
    print(f"  Test R²:     {best_reg.get('R2', 'N/A')}")
    print(f"  Test RMSE:   {best_reg.get('RMSE', 'N/A')}")
    print(f"  Test MAE:    {best_reg.get('MAE', 'N/A')}")

    print(f"\nBest Classifier: {results['classification']['best_model_name']}")
    best_cls = results["classification"]["best_model_test_metrics"]
    print(f"  Test F1:       {best_cls.get('F1', 'N/A')}")
    print(f"  Test Accuracy: {best_cls.get('Accuracy', 'N/A')}")
    print(f"  Test Recall:   {best_cls.get('Recall', 'N/A')}")

    print(f"\nSaved artifacts:")
    for name, path in saved.items():
        print(f"  {name}: {path}")

    print(f"\nReport: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
