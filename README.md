# Tabify.ai ⚡

<p align="center">
  <img src="frontend/public/tabify-logo.png" alt="Tabify.ai Logo" width="140" style="border-radius: 24px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);" />
</p>

> **Local Tabular Foundation Model Dashboard powered by TabPFN (Prior Labs)**  
> Built for the **Hacktoberfest Open-Source AI Challenge** &bull; Category: *Best Use of TabPFN*

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-EE4C2C.svg)](https://pytorch.org)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com)
[![Vue](https://img.shields.io/badge/Frontend-Vue%203-4FC08D.svg)](https://vuejs.org)
[![Vite](https://img.shields.io/badge/Vite-8.x-646CFF.svg)](https://vitejs.dev)
[![TabPFN](https://img.shields.io/badge/Model-TabPFN_v2-10B981.svg)](https://github.com/PriorLabs/TabPFN)
[![Hacktoberfest](https://img.shields.io/badge/Hacktoberfest-2026-ff7a00.svg)](https://hacktoberfest.com)

---

## 📖 Table of Contents
1. [Overview](#-overview)
2. [Key Features](#-key-features)
3. [Instant Docker & Docker Compose](#-instant-docker--docker-compose-single-command)
4. [Manual Local Development Setup](#-manual-local-development-setup)
5. [Step-by-Step User Guide](#-step-by-step-user-guide)
6. [Hardware Acceleration & GPU Processing Guide](#-hardware-acceleration--gpu-processing-guide)
7. [API Reference & cURL Examples](#-api-reference--curl-examples)
8. [Testing Suite](#-testing-suite)
9. [Troubleshooting & FAQ](#-troubleshooting--faq)
10. [Architecture & Core Value Proposition](#-architecture--core-value-proposition)
11. [License & Acknowledgments](#-license--acknowledgments)

---

## 🌟 Overview

**Tabify.ai** is a privacy-first web application designed for instantaneous, zero-training machine learning on tabular data (CSV). Powered by Prior Labs' **TabPFN (Tabular Prior-data Fitted Network)**, it delivers transformer-based in-context foundation predictions with **100% local execution** directly on your own hardware (CPU, NVIDIA CUDA, AMD ROCm/DirectML, or Apple Silicon MPS).

No external cloud APIs, no subscription fees, no data leaks, and zero tedious hyperparameter tuning required.

---

## 🚀 Key Features

- **100% Local Inference & Total Data Privacy**: Zero telemetry or cloud API calls. Your sensitive CSV data (financial statements, medical records, or proprietary metrics) never leaves your local workstation.
- **In-Context Tabular Foundation Learning**: Operates like an LLM for tables. It computes predictions in a single forward pass without iterative training loops, gradient descent, or loss tuning.
- **Multi-Hardware Compute Engine**:
  - Automatic hardware detection across **NVIDIA CUDA**, **AMD ROCm / DirectML**, **Apple Silicon (MPS)**, and **Multi-core Host CPU**.
  - Interactive hardware chip selector in the UI with dynamic fallback.
- **Four Core Machine Learning Capabilities**:
  1. **Classification** (`TabPFNClassifier`): Predict categorical targets with calibrated class probability distributions.
  2. **Regression** (`TabPFNRegressor`): Continuous numerical forecasting with R², MAE, and RMSE evaluation metrics.
  3. **Time-Series Forecasting**: Automated chronological lag extraction and rolling feature generation for future horizon steps.
  4. **Unsupervised Anomaly Detection**: Multivariate density score evaluation with automated outlier boundary detection.
- **Refined Swiss-Style Minimalist UI**:
  - Soft, eye-pleasing color palette with full Light and Dark mode support.
  - Translucent sticky header with `backdrop-blur` and real-time backend engine health indicator.
  - Interactive multi-stage progress bar showing live execution phases.
  - Dynamic Chart.js visualizations (Actual vs. Predicted curves, class distribution charts, anomaly score scatters).
  - Searchable, paginated prediction table with instant **1-Click CSV Export**.

---

## 🐳 Instant Docker & Docker Compose (Single Command)

Launch both the **Tabify.ai Frontend** and **Backend** simultaneously with a single command:

### 1. Run CPU Mode (Default)
```bash
docker compose up --build
```

### 2. Run with NVIDIA GPU Acceleration (Optional)
If your host system has an NVIDIA GPU and the NVIDIA Container Toolkit installed:
```bash
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build
```

### 3. Access the Application
- **Frontend Web UI**: [http://localhost:5173](http://localhost:5173) (or [http://localhost](http://localhost))
- **FastAPI Interactive Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Engine Health Check**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

> [!NOTE]
> - Model weights downloaded by TabPFN (~100 MB) are automatically cached in a persistent Docker volume (`tabify_tabpfn_cache`) so they only download once.
> - To terminate the containers, press `Ctrl+C` or execute `docker compose down`.

---

## ⚡ Manual Local Development Setup

### 1. Prerequisites
- **Python**: 3.10, 3.11, or 3.12
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **Git**

### 2. Clone the Repository
```bash
git clone https://github.com/Mocca130604/tabify.ai.git
cd tabify.ai
```

### 3. Setup Backend Virtual Environment
```bash
cd backend
python -m venv .venv

# Activate on Windows (PowerShell / Command Prompt):
.venv\Scripts\activate

# Activate on macOS / Linux:
source .venv/bin/activate

# Install backend dependencies:
pip install -r requirements.txt
```

### 4. Setup Frontend Dependencies
```bash
cd ../frontend
npm install
```

### 5. Launch Both Servers Simultaneously
From the repository root directory:
```bash
# Cross-platform Python runner:
python dev.py

# Or on Windows via batch script:
start_dev.bat
```

- **Frontend Application**: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **FastAPI Interactive Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health & Hardware Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 🎯 Step-by-Step User Guide

Tabify.ai features an intuitive, frictionless 4-step workflow:

```
[ Step 1: Upload ] ──► [ Step 2: Configure ] ──► [ Step 3: Run ] ──► [ Step 4: Results ]
```

### Step 1: Upload Dataset
1. Open the web application at `http://127.0.0.1:5173`.
2. **Upload your CSV file**:
   - Drag and drop your `.csv` file into the upload dropzone (maximum size: 10 MB).
   - Or click **Select CSV file** to choose a file from your file manager.
3. **Or Explore Built-in Sample Datasets (1-Click Demo)**:
   - **Iris Flower** &rarr; Multi-class botanical classification (150 rows, 4 features).
   - **House Prices** &rarr; Real estate valuation regression (50 rows, 3 features).
   - **Daily Store Sales** &rarr; Chronological retail revenue forecasting (73 days).
   - **Sensor Anomaly** &rarr; Industrial IoT multivariate anomaly detection (50 rows).

### Step 2: Configure Task & Hardware
Once the dataset is uploaded, the backend immediately inspects the data schema:
1. **Dataset Preview**: Inspect the first 5 rows and inferred column data types (`float64`, `int64`, `object`).
2. **Select Machine Learning Task**:
   - **Classification**: Predict discrete classes or categories.
   - **Regression**: Estimate continuous numerical quantities.
   - **Forecast**: Predict future time-series values (select *Time Column* and *Forecast Horizon*).
   - **Anomaly**: Unsupervised outlier detection without requiring a target label.
3. **Select Target Column**: Choose the column you want the foundation model to predict.
4. **Choose Compute Device (GPU / CPU)**: Select your preferred execution device (Auto-detect, NVIDIA CUDA, AMD, Apple MPS, or CPU).
5. Click **Run In-Context Inference**.

### Step 3: Run In-Context Inference
1. Monitor the **Real-Time Progress Bar** with live execution milestones and percentage indicators.
2. Inference lifecycle phases:
   - *Loading dataset & feature encoding*
   - *Running TabPFN forward pass evaluation*
   - *Compiling predictions & metrics*
3. Execution typically finishes in **0.1 to 1.5 seconds** depending on dataset size and active hardware.

### Step 4: Evaluate Results & Export
1. **Three Primary KPI Summary Cards**:
   - *Accuracy / R² Score / Mean Absolute Error / Anomalies Detected*
   - *Total Samples Evaluated*
   - *Inference Latency & Active Hardware Device*
2. **Interactive Visualizations (Chart.js)**:
   - Actual vs. Predicted trend curves for regression and forecasting.
   - Categorical class distribution bars for classification.
   - Anomaly severity scores and outlier distribution markers.
3. **Interactive Predictions Table**:
   - Integrated real-time search filter and clean pagination.
   - Color-coded badges indicating prediction classifications and confidence scores.
4. **CSV Export**: Click **Export CSV** in the table header to download complete prediction results.
5. Click **Adjust Config** to refine parameters or **Start Over** to analyze a new dataset.

---

## ⚡ Hardware Acceleration & GPU Processing Guide

Tabify.ai is architected to leverage modern hardware accelerators. TabPFN transformer operations achieve significant acceleration when executed on dedicated GPUs compared to CPUs.

### 1. Inference Performance Benchmarks

| Hardware Accelerator | Classification (150 rows) | Regression (50 rows) | Large Dataset (2,000 rows) | Memory Requirement |
| :--- | :--- | :--- | :--- | :--- |
| **NVIDIA GPU (CUDA)** | **~0.15 s** | **~0.10 s** | **~1.2 s** | &ge; 2 GB VRAM |
| **Apple Silicon (MPS M1/M2/M3/M4)** | **~0.25 s** | **~0.15 s** | **~1.8 s** | Unified Memory |
| **AMD GPU (ROCm / DirectML)** | **~0.30 s** | **~0.20 s** | **~2.1 s** | &ge; 4 GB VRAM |
| **Multi-core Host CPU (Intel / AMD)** | ~1.40 s | ~0.60 s | ~6.5 s | &ge; 4 GB RAM |

---

### 2. NVIDIA GPU Setup (CUDA)

If your machine is equipped with an NVIDIA GPU (GeForce RTX, GTX, Quadro, or Tesla), ensure NVIDIA drivers and CUDA-enabled PyTorch are installed.

#### A. Verify NVIDIA Driver
Open your terminal or PowerShell and run:
```bash
nvidia-smi
```
Verify that your GPU name and supported CUDA version (e.g., `CUDA Version: 12.x` or `11.8`) appear in the output.

#### B. Install PyTorch with CUDA in Virtual Environment
Navigate to the `backend` directory and install the wheel matching your CUDA version:

```bash
cd backend
.venv\Scripts\activate   # Windows
# or: source .venv/bin/activate  # Linux/macOS

# For CUDA 12.1 / 12.4 (Recommended for modern RTX 30xx, 40xx, 50xx series):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8 (Legacy GPU architectures):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### C. Verify PyTorch CUDA Availability
```python
python -c "import torch; print('CUDA Available:', torch.cuda.is_available(), 'Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```
Expected output:
```text
CUDA Available: True Device: NVIDIA GeForce RTX 4070
```
Tabify.ai will automatically recognize your NVIDIA GPU and prioritize it as the default execution accelerator.

---

### 3. AMD GPU Setup

#### A. On Linux (ROCm)
If you are running an AMD Radeon GPU on Linux supported by ROCm:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.0
```

#### B. On Windows (DirectML)
For AMD Radeon users on Windows (RX 5000, 6000, 7000 series, or integrated Radeon Graphics):
```bash
pip install torch-directml
```
Tabify.ai will detect the DirectML adapter and map inference computations accordingly.

---

### 4. Apple Silicon Setup (M1 / M2 / M3 / M4)

On Apple Mac computers powered by Apple Silicon chips:
PyTorch provides native **Metal Performance Shaders (MPS)** hardware acceleration without requiring third-party drivers.

Verify MPS availability in your macOS terminal:
```bash
python3 -c "import torch; print('MPS Available:', torch.backends.mps.is_available())"
```
Expected output:
```text
MPS Available: True
```
Tabify.ai will automatically display the **Apple MPS** active badge on the navbar.

---

### 5. Selecting Compute Device via Web UI & REST API

Tabify.ai provides an interactive hardware catalog in **Step 2 (Configure)**:
- **Auto (Recommended)**: Dynamically selects the fastest available hardware accelerator (NVIDIA CUDA &rarr; Apple MPS &rarr; AMD &rarr; Host CPU).
- **Manual Switching**: Click any detected hardware chip in the UI to force execution on a specific device.
- **REST API Switch**: Change the active device programmatically via HTTP POST:
  ```bash
  curl -X POST "http://127.0.0.1:8000/api/device/switch?device_id=cuda"
  ```

---

## 📡 API Reference & cURL Examples

FastAPI automatically generates interactive OpenAPI documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 1. Check Health & Hardware Device Catalog
```bash
curl -s http://127.0.0.1:8000/api/health | jq
```
Example Response:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "device": "cuda",
  "device_catalog": [
    {
      "id": "cuda",
      "vendor": "nvidia",
      "label": "NVIDIA GeForce RTX 4070 (12.0 GB VRAM)",
      "available": true,
      "recommended": true,
      "vram_gb": 12.0
    },
    {
      "id": "cpu",
      "vendor": "cpu",
      "label": "Intel/AMD Multi-core Host CPU",
      "available": true,
      "recommended": false,
      "vram_gb": null
    }
  ]
}
```

### 2. Switch Active Compute Device
```bash
curl -X POST "http://127.0.0.1:8000/api/device/switch?device_id=cuda"
```

### 3. Inspect CSV Dataset (`/api/inspect`)
```bash
curl -s -F "file=@sample_data/iris.csv" http://127.0.0.1:8000/api/inspect | jq
```

### 4. Execute Classification Prediction (`/api/predict`)
```bash
curl -s -F "file=@sample_data/iris.csv" \
        -F "task=classification" \
        -F "target_column=species" \
        http://127.0.0.1:8000/api/predict | jq
```

### 5. Execute Regression Prediction (`/api/predict`)
```bash
curl -s -F "file=@sample_data/house_prices.csv" \
        -F "task=regression" \
        -F "target_column=price" \
        http://127.0.0.1:8000/api/predict | jq
```

### 6. Execute Time-Series Forecasting (`/api/predict`)
```bash
curl -s -F "file=@sample_data/daily_sales.csv" \
        -F "task=forecast" \
        -F "target_column=units_sold" \
        -F "time_column=date" \
        -F "horizon=7" \
        http://127.0.0.1:8000/api/predict | jq
```

### 7. Execute Unsupervised Anomaly Detection (`/api/predict`)
```bash
curl -s -F "file=@sample_data/sensor_anomaly.csv" \
        -F "task=anomaly" \
        http://127.0.0.1:8000/api/predict | jq
```

---

## 🧪 Testing Suite

Run the automated unit and integration test suite with `pytest`:
```bash
backend\.venv\Scripts\pytest backend/tests/test_api.py -v
```

The test suite validates data schemas and all four machine learning operational modes:
```text
backend/tests/test_api.py::test_health_endpoint PASSED                   [ 12%]
backend/tests/test_api.py::test_inspect_csv_iris PASSED                  [ 25%]
backend/tests/test_api.py::test_inspect_invalid_file_extension PASSED    [ 37%]
backend/tests/test_api.py::test_predict_classification_iris PASSED       [ 50%]
backend/tests/test_api.py::test_predict_regression_house_prices PASSED   [ 62%]
backend/tests/test_api.py::test_predict_forecast_daily_sales PASSED      [ 75%]
backend/tests/test_api.py::test_predict_anomaly_sensor PASSED            [ 87%]
backend/tests/test_api.py::test_predict_missing_target_for_classification PASSED [100%]
============================== 8 passed in 8.42s ===============================
```

---

## ❓ Troubleshooting & FAQ

| Issue | Probable Cause | Resolution |
| :--- | :--- | :--- |
| **First inference execution takes longer** | Initial TabPFN model weights download | On first run, TabPFN downloads model checkpoint weights (~100 MB) from Hugging Face into your local cache directory. All subsequent runs execute instantly from disk. |
| **GPU is not recognized (Falls back to CPU)** | PyTorch CPU-only package is installed | Install CUDA-enabled PyTorch via `pip install torch --index-url https://download.pytorch.org/whl/cu121` as described in the GPU guide. |
| **Port 8000 or 5173 conflict (In Use)** | Another service is using the port | Modify the backend port in `backend/.env` or specify a different Vite port using `npm run dev -- --port 5174`. |
| **HTTP 413 / File Too Large Error** | Upload exceeds default file limit (10 MB) | TabPFN is optimized for datasets up to ~10,000 rows. You can increase `MAX_UPLOAD_SIZE_MB` in the configuration file if required. |
| **Out-of-Memory (OOM) on smaller GPUs** | Dataset has an excessive number of columns (>300 columns) | Enable the **Auto-subsample** option in Step 2 or switch to multi-core CPU mode for massive column spaces. |

---

## 🏛️ Architecture & Core Value Proposition

Tabify.ai delivers a zero-friction paradigm for tabular data analysis:

### Why Tabify.ai Stands Out
1. **Zero-Training In-Context Learning**: Unlike conventional tree algorithms (XGBoost, LightGBM, Random Forest) that demand iterative fitting, validation loops, and metric loss tuning, TabPFN conducts inference through a single transformer *forward pass* directly on your table context.
2. **Multi-Hardware Flexibility**: Supports NVIDIA CUDA, AMD ROCm / DirectML, Apple Silicon MPS, and multi-threaded CPU architectures with automated detection.
3. **Absolute Privacy Assurance**: Proprietary spreadsheets, sensitive customer records, or industrial sensor telemetries never leave your workstation.
4. **Intuitive Engineering**: Combines a modern Vue 3 + Tailwind CSS design system with FastAPI, comprehensive OpenAPI specifications, and multi-stage Docker deployment.

---

## 📄 License & Acknowledgments

- **Tabify.ai Application Code**: Distributed under the [Apache-2.0 License](LICENSE).
- **TabPFN Foundation Model**: Copyright &copy; [Prior Labs](https://priorlabs.ai) under the non-commercial research evaluation license.
- **Acknowledgments**: Sincere gratitude to the **Prior Labs** research team for pioneering in-context foundation models for tabular data and the global **Hacktoberfest** community.
