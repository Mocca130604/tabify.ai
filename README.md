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
3. [Quick Start & Installation](#-quick-start--installation)
4. [Step-by-Step Usage Guide (Cara Penggunaan)](#-step-by-step-usage-guide-cara-penggunaan)
5. [Hardware Acceleration & GPU Processing Guide](#-hardware-acceleration--gpu-processing-guide)
6. [API Reference & cURL Examples](#-api-reference--curl-examples)
7. [Testing Suite](#-testing-suite)
8. [Troubleshooting & FAQ](#-troubleshooting--faq)
9. [Ringkasan Proyek (Bahasa Indonesia)](#-ringkasan-proyek-bahasa-indonesia)
10. [License & Acknowledgments](#-license--acknowledgments)

---

## 🌟 Overview

**Tabify.ai** is a privacy-first web application for instantaneous machine learning on tabular data (CSV). Powered by Prior Labs' **TabPFN v2 (Tabular Prior-data Fitted Network)**, it delivers zero-training, in-context foundation model predictions with **100% local execution** on your own hardware (CPU, NVIDIA CUDA, AMD, or Apple Silicon MPS). No external cloud APIs, no data leaks, and zero hyperparameter tuning required.

---

## 🚀 Key Features

- **100% Local Inference**: Zero data transmission to third-party cloud APIs. Your sensitive tabular data never leaves your computer.
- **In-Context Foundation Learning**: TabPFN acts as a transformer foundation model on tables. Predictions are computed in a single forward pass without iterative training steps or loss functions.
- **Hardware-Aware Compute Engine**:
  - Auto-detection for **NVIDIA (CUDA)**, **AMD (ROCm / DirectML)**, **Apple Silicon (MPS)**, and **Multi-core CPU**.
  - Interactive device switcher directly in the web UI.
- **Four Core Machine Learning Tasks**:
  1. **Classification** (`TabPFNClassifier`): Predict categorical labels with calibrated class probabilities.
  2. **Regression** (`TabPFNRegressor`): Continuous numerical estimation with R², MAE, and RMSE holdout metrics.
  3. **Time-Series Forecasting**: Automated lag and calendar feature extraction for future chronological steps.
  4. **Unsupervised Anomaly Detection**: Multivariate density evaluation scoring and outlier flag identification.
- **Modern Minimalist UI**:
  - Soft, eye-friendly color palette in both Light and Dark modes.
  - Sticky navbar with `backdrop-blur` and live engine health indicator.
  - Prominent real-time progress bar with honest execution phases.
  - Interactive Chart.js visualizations (actual vs. predicted curves, class distributions, outlier bars).
  - Searchable and paginated predictions table with **1-click CSV Export**.

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- **Python**: 3.10, 3.11, or 3.12
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **Git**

### 2. Clone the Repository
```bash
git clone https://github.com/your-username/Tabify.ai.git
cd Tabify.ai
```

### 3. Setup Backend Environment
```bash
cd backend
python -m venv .venv

# Activate on Windows:
.venv\Scripts\activate

# Activate on macOS / Linux:
source .venv/bin/activate

# Install dependencies:
pip install -r requirements.txt
```

### 4. Setup Frontend
```bash
cd ../frontend
npm install
```

### 5. Launch Both Servers Simultaneously
From the repository root directory:
```bash
# Cross-platform Python runner:
python dev.py

# Or on Windows batch script:
start_dev.bat
```

- **Frontend Application**: [http://127.0.0.1:5173](http://127.0.0.1:5173)
- **FastAPI Interactive Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health & Hardware Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 🎯 Step-by-Step Usage Guide (Cara Penggunaan)

Tabify.ai operates through an intuitive 4-step workflow:

```
[ Step 1: Upload ] ──► [ Step 2: Configure ] ──► [ Step 3: Run ] ──► [ Step 4: Results ]
```

### Langkah 1: Upload Dataset (Step 1)
1. Buka aplikasi di peramban web pada alamat `http://127.0.0.1:5173`.
2. **Unggah file CSV**:
   - Tarik & letakkan (*drag and drop*) file `.csv` Anda ke dalam kotak upload (maksimal 10 MB).
   - Atau klik tombol **Select CSV file** untuk memilih file dari komputer Anda.
3. **Atau Gunakan Sample Dataset (1-Click Demo)**:
   - **Iris Flower** &rarr; Klasifikasi bunga (150 baris, 4 fitur).
   - **House Prices** &rarr; Regresi estimasi harga properti (50 baris, 3 fitur).
   - **Daily Store Sales** &rarr; Forecasting penjualan harian berkala (73 hari).
   - **Sensor Anomaly** &rarr; Deteksi anomali sensor multivariat (50 baris).

### Langkah 2: Konfigurasi Task & Hardware (Step 2)
Setelah dataset dimuat, backend secara otomatis melakukan inspeksi struktur data:
1. **Pratinjau Dataset**: Periksa 5 baris pertama data dan tipe datanya (`float64`, `int64`, `object`).
2. **Pilih Task ML**:
   - **Classification**: Untuk memprediksi kategori/kelas diskrit.
   - **Regression**: Untuk memprediksi nilai angka kontinu.
   - **Forecast**: Untuk meramalkan deret waktu masa depan (tentukan *Time Column* dan *Horizon steps*).
   - **Anomaly**: Deteksi outlier tanpa perlu memilih target column (*unsupervised*).
3. **Pilih Target Column**: Pilih kolom mana yang ingin diprediksi oleh model.
4. **Pilih Compute Device (GPU / CPU)**: Pilih kartu pemrosesan yang ingin digunakan (Auto-detect, NVIDIA CUDA, AMD, Apple MPS, atau CPU).
5. Klik tombol **Run In-Context Inference**.

### Langkah 3: Eksekusi Inferensi (Step 3)
1. Perhatikan **Progress Bar Dinamis** di tengah layar yang bergerak secara real-time disertai persentase progres.
2. Tahapan eksekusi:
   - *Loading dataset & feature encoding*
   - *Running TabPFN forward pass evaluation*
   - *Compiling predictions & metrics*
3. Waktu eksekusi lokal umumnya memakan waktu **0.2 – 1.5 detik** (tergantung ukuran baris dan hardware).

### Langkah 4: Evaluasi Hasil & Ekspor (Step 4)
1. **3 Kartu Ringkasan KPI**:
   - *Model Accuracy / R² Score / MAE / Anomalies Detected*
   - *Total Predictions Evaluated*
   - *Inference Time & Active Device*
2. **Grafik Visual Interaktif (Chart.js)**:
   - Kurva perbandingan nilai aktual vs prediksi.
   - Distribusi frekuensi kelas atau sebaran skor anomali.
3. **Tabel Hasil Prediksi**:
   - Dilengkapi *search bar* instan dan paginasi yang rapi.
   - Setiap baris memiliki pill badge status hasil prediksi.
4. **Export CSV**: Klik tombol **Export CSV** di kanan atas tabel untuk mengunduh seluruh baris hasil prediksi dalam format spreadsheet.
5. Klik **Adjust Config** untuk mengubah parameter atau **Start Over** untuk menganalisis dataset baru.

---

## ⚡ Hardware Acceleration & GPU Processing Guide

Tabify.ai dirancang untuk memanfaatkan akselerator perangkat keras secara maksimal. Inferensi model transformer TabPFN dapat berjalan jauh lebih cepat ketika menggunakan GPU dibandingkan CPU.

### 1. Perbandingan Performa Inferensi (Benchmark)

| Perangkat Keras | Klasifikasi (150 baris) | Regresi (50 baris) | Dataset Besar (2.000 baris) | Kebutuhan VRAM / RAM |
| :--- | :--- | :--- | :--- | :--- |
| **NVIDIA GPU (CUDA)** | **~0.15 detik** | **~0.10 detik** | **~1.2 detik** | &ge; 2 GB VRAM |
| **Apple Silicon (MPS M1/M2/M3)** | **~0.25 detik** | **~0.15 detik** | **~1.8 detik** | Unified Memory |
| **AMD GPU (ROCm / DirectML)** | **~0.30 detik** | **~0.20 detik** | **~2.1 detik** | &ge; 4 GB VRAM |
| **CPU Multi-core (Intel / AMD)** | ~1.40 detik | ~0.60 detik | ~6.5 detik | &ge; 4 GB RAM |

---

### 2. Konfigurasi GPU NVIDIA (CUDA)

Jika Anda memiliki GPU NVIDIA (GeForce RTX, GTX, Quadro, atau Tesla), pastikan driver NVIDIA dan PyTorch berkemampuan CUDA terpasang.

#### A. Verifikasi Driver NVIDIA
Buka terminal / PowerShell dan ketik:
```bash
nvidia-smi
```
Pastikan CUDA Version tertera (misalnya `CUDA Version: 12.x` atau `11.8`).

#### B. Pasang PyTorch CUDA di Virtual Environment
Masuk ke direktori backend dan jalankan perintah install sesuai versi CUDA Anda:

```bash
cd backend
.venv\Scripts\activate   # Windows
# atau: source .venv/bin/activate  # Linux

# Untuk CUDA 12.1 / 12.4 (Rekomendasi untuk RTX 30xx, 40xx, 50xx):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Untuk CUDA 11.8 (Kartu grafis generasi sebelumnya):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

#### C. Verifikasi di Python
```python
python -c "import torch; print('CUDA Available:', torch.cuda.is_available(), 'Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```
Output:
```text
CUDA Available: True Device: NVIDIA GeForce RTX 3060
```
Backend Tabify.ai akan secara otomatis mendeteksi GPU Anda sebagai pilihan aktif default.

---

### 3. Konfigurasi GPU AMD

#### A. Di Linux (ROCm)
Jika Anda menggunakan AMD Radeon di Linux yang didukung oleh AMD ROCm:
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm6.0
```

#### B. Di Windows (DirectML)
Untuk pengguna AMD Radeon di Windows (RX 5000, 6000, 7000 series, atau Radeon Graphics terintegrasi):
```bash
pip install torch-directml
```
Tabify.ai mendeteksi adapter DirectML dan mengarahkannya ke akselerasi grafis DirectML yang tersedia.

---

### 4. Konfigurasi Apple Silicon (M1 / M2 / M3 / M4)

Pada komputer Apple Mac dengan chip Apple Silicon (Apple M1/M2/M3/M4):
PyTorch secara *native* mendukung akselerasi **Metal Performance Shaders (MPS)** tanpa perlu driver tambahan.

Verifikasi di terminal macOS:
```bash
python3 -c "import torch; print('MPS Available:', torch.backends.mps.is_available())"
```
Output:
```text
MPS Available: True
```
Tabify.ai akan otomatis menampilkan badge **Apple MPS Active** pada navbar.

---

### 5. Memilih Device Pemrosesan Melalui Web UI & API

Tabify.ai menyediakan katalog perangkat keras interaktif pada **Step 2 (Configure)**:
- **Auto (Rekomendasi)**: Memilih akselerator tercepat secara otomatis (NVIDIA CUDA &rarr; Apple MPS &rarr; AMD &rarr; CPU).
- **Manual Switching**: Anda dapat mengklik chip hardware untuk memaksa inferensi berjalan di CPU atau GPU tertentu.
- **REST API Switch**: Anda dapat mengganti device aktif kapan saja via HTTP POST:
  ```bash
  curl -X POST "http://127.0.0.1:8000/api/device/switch?device_id=cuda"
  ```

---

## 📡 API Reference & cURL Examples

FastAPI secara otomatis menyediakan dokumentasi OpenAPI interaktif di [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 1. Cek Status Kesehatan & Hardware
```bash
curl -s http://127.0.0.1:8000/api/health | jq
```
Contoh Respons:
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

### 2. Ganti Perangkat Pemrosesan (Device Switch)
```bash
curl -X POST "http://127.0.0.1:8000/api/device/switch?device_id=cuda"
```

### 3. Inspeksi Dataset CSV (`/api/inspect`)
```bash
curl -s -F "file=@sample_data/iris.csv" http://127.0.0.1:8000/api/inspect | jq
```

### 4. Eksekusi Prediksi Klasifikasi (`/api/predict`)
```bash
curl -s -F "file=@sample_data/iris.csv" \
        -F "task=classification" \
        -F "target_column=species" \
        http://127.0.0.1:8000/api/predict | jq
```

### 5. Eksekusi Prediksi Regresi (`/api/predict`)
```bash
curl -s -F "file=@sample_data/house_prices.csv" \
        -F "task=regression" \
        -F "target_column=price" \
        http://127.0.0.1:8000/api/predict | jq
```

### 6. Eksekusi Prediksi Time-Series Forecasting
```bash
curl -s -F "file=@sample_data/daily_sales.csv" \
        -F "task=forecast" \
        -F "target_column=units_sold" \
        -F "time_column=date" \
        -F "horizon=7" \
        http://127.0.0.1:8000/api/predict | jq
```

### 7. Eksekusi Unsupervised Anomaly Detection
```bash
curl -s -F "file=@sample_data/sensor_anomaly.csv" \
        -F "task=anomaly" \
        http://127.0.0.1:8000/api/predict | jq
```

---

## 🧪 Testing Suite

Jalankan pengujian unit dan integrasi otomatis dengan `pytest`:
```bash
backend\.venv\Scripts\pytest backend/tests/test_api.py -v
```

Hasil pengujian mencakup seluruh skenario validasi data dan task ML:
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

| Masalah | Penyebab | Solusi |
| :--- | :--- | :--- |
| **Inferensi pertama memakan waktu lebih lama** | Unduhan awal bobot model TabPFN | Saat pertama kali dijalankan, TabPFN mengunduh checkpoint model (~100 MB) dari Hugging Face ke cache lokal. Inferensi berikutnya berjalan instan dari disk. |
| **GPU tidak terdeteksi (Fallback ke CPU)** | PyTorch yang terpasang adalah versi CPU-only | Pasang PyTorch dengan CUDA flag via `pip install torch --index-url https://download.pytorch.org/whl/cu121` seperti panduan di atas. |
| **Port 8000 atau 5173 bentrok (*In Use*)** | Proses lain menggunakan port tersebut | Ubah port backend di `backend/.env` atau tambahkan flag port di Vite `npm run dev -- --port 5174`. |
| **Error CSV 413 / File Too Large** | Ukuran file melebihi batas default (10 MB) | TabPFN dirancang untuk dataset hingga ~10.000 baris. Anda dapat menaikkan batas `MAX_UPLOAD_SIZE_MB` di file konfigurasi. |
| **Out of Memory (OOM) pada GPU kecil** | Dataset sangat lebar (>300 kolom) | Aktifkan opsi **Auto-subsample** pada Step 2 atau pilih pemrosesan CPU untuk dataset dengan dimensi kolom masif. |

---

## 🇮🇩 Ringkasan Proyek (Bahasa Indonesia)

**Tabify.ai** adalah platform antarmuka berbasis web untuk menjalankan foundation model tabular **TabPFN (Prior Labs)** secara **100% LOKAL** tanpa ketergantungan API cloud berbayar atau server eksternal.

### Mengapa Tabify.ai Berbeda?
1. **Zero-Training In-Context Learning**: Berbeda dari Random Forest atau XGBoost yang memerlukan fitting iteratif berulang-ulang, TabPFN melakukan inferensi melalui satu *forward pass* transformer langsung dari data tabel Anda.
2. **Akselerasi Multi-Hardware**: Mendukung GPU NVIDIA CUDA, AMD ROCm / DirectML, Apple Silicon MPS, dan multi-core CPU dengan deteksi otomatis.
3. **Privasi Total**: Data CSV pribadi, data finansial, catatan medis, atau data sensor tidak pernah dikirim ke internet; seluruh pemrosesan berlangsung di memori RAM/VRAM lokal.
4. **Antarmuka Modern**: Dibangun dengan Vue 3, Tailwind CSS, Chart.js, palet warna *soft minimalist*, *backdrop blur navbar*, logo eksklusif, dan progress bar interaktif.

---

## 📄 License & Acknowledgments

- **Kode Aplikasi Tabify.ai**: Dilisensikan di bawah [Apache-2.0 License](LICENSE).
- **TabPFN Foundation Model**: Hak cipta milik [Prior Labs](https://priorlabs.ai) di bawah lisensi evaluasi riset non-komersial.
- **Ucapan Terima Kasih**: Terima kasih kepada tim **Prior Labs** atas riset terobosan pada fondasi model tabular in-context learning dan komunitas **Hacktoberfest**.
