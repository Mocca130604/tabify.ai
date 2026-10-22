# Contributing to Tabify.ai

Welcome! Thank you for your interest in contributing to **Tabify.ai**. This project is an open-source web dashboard built for the **Hacktoberfest Open-Source AI Challenge** (category: *"Best Use of TabPFN"*).

---

## 🌟 Hacktoberfest Guidelines

- **Quality Over Quantity**: We welcome meaningful PRs (features, bug fixes, performance improvements, documentation, and UI polish).
- **PR Labels**: Valid pull requests will be tagged with `hacktoberfest-accepted`.
- **Discussion**: Before opening a large PR, please open an issue to propose your ideas.

---

## 🎯 Suggested "Good First Issue" Topics

We have identified several modular tasks ideal for new contributors:

1. **`good first issue` &bull; Add ROC-AUC & Confusion Matrix Heatmap Component**:
   - Create a specialized heatmap visualization for multi-class classification confusion matrices in `src/components/charts/`.
2. **`good first issue` &bull; Add Additional Sample Datasets**:
   - Provide curated, license-free tabular datasets in `sample_data/` (e.g., churn prediction, medical diagnosis, housing valuation).
3. **`good first issue` &bull; Export to Excel (.xlsx)**:
   - Expand table export capabilities in `ResultsView.vue` to allow `.xlsx` format download via client-side libraries.
4. **`good first issue` &bull; Add Custom Forecast Horizon Sliders**:
   - Provide visual date range pickers and rolling forecast confidence intervals for time-series forecasting.
5. **`good first issue` &bull; CUDA / MPS Performance Benchmark Script**:
   - Add a benchmark utility in `backend/benchmarks/` to measure throughput differences across CPU, CUDA, and Apple MPS hardware.

---

## 🛠️ Local Development Setup

### 1. Prerequisites
- Python 3.10 or higher
- Node.js 18+ and npm 9+
- Git

### 2. Fork and Clone
```bash
git clone https://github.com/your-username/Tabify.ai.git
cd Tabify.ai
```

### 3. Setup Backend
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
pytest
```

### 4. Setup Frontend
```bash
cd ../frontend
npm install
npm run dev
```

Or run both simultaneously from the project root:
```bash
python dev.py
```

---

## 🧪 Testing and Quality Standards

- Backend tests must pass:
  ```bash
  backend/.venv/Scripts/pytest backend/tests/test_api.py -v
  ```
- Frontend must build cleanly:
  ```bash
  cd frontend && npm run build
  ```
- Type hints and docstrings should accompany all new Python services and models.

---

## 📜 Code of Conduct

Be welcoming, inclusive, and respectful to all contributors regardless of experience level.
