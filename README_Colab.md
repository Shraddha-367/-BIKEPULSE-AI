# BIKEPULSE AI — Google Colab Integration Guide

**Statistical Intelligence & Resource Planning System**  
*Execution Environment Manual for Google Colab Backend & Local Frontend Integration*

---

## 📌 Executive Summary

BIKEPULSE AI now features full cloud-native execution capability on **Google Colab**. This setup decouples heavy scientific computing and machine learning pipeline training from the local presentation tier, allowing you to run, verify, and demonstrate all backend operations in Google Cloud while preserving the interactive Streamlit user interface.

```
                  ┌───────────────────────────────────────────┐
                  │          Google Colab (Cloud)             │
                  │  • Data Ingestion & Cleaning              │
                  │  • Statistical Analysis & CLT             │
                  │  • Hypothesis Testing Battery             │
                  │  • 11 ML Models (6 Regressors, 5 Cls)     │
                  │  • Serialization & Parity Verification    │
                  └─────────────────────┬─────────────────────┘
                                        │
                                        ▼ Artifacts Export
                        bikepulse_colab_artifacts.zip
                        (models/*.joblib, *.json)
                                        │
                                        ▼
                  ┌───────────────────────────────────────────┐
                  │         Local Streamlit Dashboard         │
                  │  • app.py & pages/1–10                    │
                  │  • Sub-millisecond Live Inference         │
                  │  • Interactive Visualizations             │
                  └───────────────────────────────────────────┘
```

---

## 📁 Key Deliverables

| Deliverable | Location | Description |
| :--- | :--- | :--- |
| **Google Colab Notebook** | [`Project_Backend_Google_Colab.ipynb`](Project_Backend_Google_Colab.ipynb) | Complete, 10-section, faculty-ready backend notebook executable with 1-click **Run all**. |
| **Integration Guide** | [`README_Colab.md`](README_Colab.md) | Step-by-step instructions for uploading, running, and bridging artifacts to the UI. |
| **Generator Script** | [`scripts/build_colab_notebook.py`](scripts/build_colab_notebook.py) | Python script to programmatically compile and validate the Colab notebook. |
| **Production Source Modules** | [`src/`](src/) | Unaltered original production modules (17 files, 100% preserved). |
| **Frontend UI** | [`app.py`](app.py), [`pages/`](pages/) | Streamlit multipage application consuming generated model artifacts. |

---

## 🚀 How to Run on Google Colab

### Method A: One-Click Standalone Run (Recommended for Faculty Demo)

You only need **one file** (`Project_Backend_Google_Colab.ipynb`) to demonstrate the complete backend:

1. Open [Google Colab](https://colab.research.google.com).
2. Click **Upload** → Browse to and select `Project_Backend_Google_Colab.ipynb`.
3. *(Optional)* Select **Runtime** → **Change runtime type** → Hardware accelerator: **CPU** or **T4 GPU** (both work seamlessly).
4. Run all cells:
   - Click **Runtime** → **Run all** (or press `Ctrl + F9`).
5. **Automated Dataset Handling:**
   - The notebook automatically detects if `hour.csv` is present.
   - If not found, it **automatically downloads the official UCI Bike Sharing archive** directly from the UCI Machine Learning Repository, extracts `hour.csv`, and validates its SHA-256 cryptographic checksum.
   - Alternatively, you can drag and drop `hour.csv` into the Colab left sidebar file browser (`/content/`).

---

### Method B: Google Drive / Full Repository Run

If you want Colab to access your full local project structure:

1. Compress your `BIKEPULSE_AI` folder into a `.zip` file or upload it to Google Drive.
2. In Colab, mount Google Drive or unzip the folder:
   ```python
   # Mount Google Drive
   from google.colab import drive
   drive.mount('/content/drive')
   
   # Or unzip project directly
   !unzip -q /content/BIKEPULSE_AI.zip -d /content/
   %cd /content/BIKEPULSE_AI
   ```
3. Open `Project_Backend_Google_Colab.ipynb` and select **Runtime** → **Run all**.

---

## 🔄 Transferring Colab Model Artifacts to the Local Frontend

Once the Google Colab notebook completes execution:

1. **Automatic Download:**
   - Cell 17 in the notebook automatically packages all trained model binaries into `bikepulse_colab_artifacts.zip` and triggers a browser download.
2. **Extract to Local Workspace:**
   - Move the downloaded `bikepulse_colab_artifacts.zip` into your local `BIKEPULSE_AI` project root.
   - Extract the contents so that the files are placed inside `models/`:
     - `models/best_regressor.joblib`
     - `models/best_classifier.joblib`
     - `models/high_demand_threshold.json`
3. **Launch Streamlit:**
   ```powershell
   # In Windows PowerShell:
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```
4. **Verify Live Inference:**
   - Navigate to **Page 9: Demand Prediction**.
   - Notice that the prediction engine immediately consumes the Colab-trained model pipelines with **zero retraining needed**!

---

## 📊 Verification & Metric Parity Matrix

The Google Colab notebook contains **Section 9: Validation Against Original Outputs**, which programmatically checks live execution against the baseline:

| Metric / Check | Baseline Output | Google Colab Output | Parity Status |
| :--- | :--- | :--- | :---: |
| **Cleaned Dataset Dimensions** | 17,379 rows × 24 cols | 17,379 rows × 24 cols | **PASS (100%)** |
| **Chronological Split (Train)** | 12,165 rows (70.0%) | 12,165 rows (70.0%) | **PASS (100%)** |
| **Chronological Split (Validation)** | 2,606 rows (15.0%) | 2,606 rows (15.0%) | **PASS (100%)** |
| **Chronological Split (Test)** | 2,608 rows (15.0%) | 2,608 rows (15.0%) | **PASS (100%)** |
| **High Demand Binary Threshold** | 234.0 rentals/hr | 234.0 rentals/hr | **PASS (100%)** |
| **Champion Regressor Model** | Random Forest Regression | Random Forest Regression | **PASS (100%)** |
| **Champion Classifier Model** | Decision Tree Classifier | Decision Tree Classifier | **PASS (100%)** |
| **Champion Test $R^2$ Score** | $\approx 0.8352$ | $\approx 0.8352$ | **PASS ($\pm 0.01$)** |
| **Champion Test $F_1$ Score** | $\approx 0.8143$ | $\approx 0.8143$ | **PASS ($\pm 0.01$)** |
| **Reload Parity Difference** | $< 10^{-6}$ | $0.00000000$ | **PASS (Exact)** |

---

## 📑 Faculty Presentation Structure (10 Sections)

When presenting to your faculty, the notebook is structured into 10 clear, professionally titled sections:

1. **Project Title and Overview:** Dataset background, scope (56 topics, 11 models), and dual-tier architecture.
2. **Objective:** Specific aims, leakage prevention principles, and expected deliverables.
3. **Google Colab Environment Setup:** Accelerator detection, directory creation, and random seed anchoring.
4. **Dependency Installation:** Automated package alignment matching `requirements.txt`.
5. **Dataset Loading:** 4-tier robust loader with SHA-256 provenance verification.
6. **Backend Modules and Functions:** Reusable, modular mathematical functions (preprocessing, stats, sampling, hypothesis tests, ML pipelines).
7. **Data Processing / Core Logic:** Step-by-step execution across data cleaning, EDA, hypothesis tests, training 11 models, serialization, and live prediction.
8. **Output Tables and Visualizations:** Formatted comparison leaderboards, actual vs predicted scatter plots, correlation heatmaps, and CLT distributions.
9. **Validation Against Original Outputs:** Automated assertions confirming 100% mathematical parity.
10. **Final Results and Conclusion:** Architectural review, frontend connection guide, and artifact export.

---

## 🛠️ Frequently Asked Questions (FAQ)

**Q: Do I need to modify any of the existing `.py` files in `src/` or `pages/`?**  
A: No. All existing `.py` files, Streamlit pages, and test suites are 100% preserved and untouched.

**Q: Can Streamlit run directly inside a standard Colab notebook cell?**  
A: Streamlit is designed as a standalone interactive web server rather than a static cell output. Running it inside Colab typically requires third-party tunneling proxies (e.g. `localtunnel` or `ngrok`), which are ephemeral and prone to disconnections. The production standard implemented here is to use Colab as the computational backend that generates serialized pipelines, which the frontend serves cleanly.

**Q: What if the UCI download server is temporarily unavailable during my demo?**  
A: The notebook includes a multi-tiered failover: it first checks local directories, then checks uploaded files in `/content/`, then queries the UCI repository, and finally falls back to a verified raw mirror. It will never fail with a `FileNotFoundError`.
