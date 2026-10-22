"""Pytest test suite for Tabify.ai FastAPI backend."""

import os
import sys
from pathlib import Path

# Add repo root to sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "sample_data"


def test_health_endpoint():
    """Test /api/health returns 200 with operational metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "tabpfn_version" in data
    assert "device" in data
    assert "supported_tasks" in data
    assert "classification" in data["supported_tasks"]


def test_inspect_csv_iris():
    """Test /api/inspect successfully parses sample iris.csv dataset."""
    iris_path = SAMPLE_DIR / "iris.csv"
    assert iris_path.exists(), f"Missing {iris_path}"

    with open(iris_path, "rb") as f:
        response = client.post(
            "/api/inspect",
            files={"file": ("iris.csv", f, "text/csv")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "iris.csv"
    assert data["row_count"] == 150
    assert data["column_count"] >= 5
    assert len(data["preview_rows"]) == 5
    assert data["suggestions"]["recommended_task"] == "classification"
    assert data["suggestions"]["recommended_target"] == "species"


def test_inspect_invalid_file_extension():
    """Test /api/inspect rejects non-csv files with 400."""
    response = client.post(
        "/api/inspect",
        files={"file": ("notes.txt", b"some text content", "text/plain")},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "INVALID_FILE_EXTENSION"


def test_predict_classification_iris():
    """Test /api/predict on classification task with iris dataset."""
    iris_path = SAMPLE_DIR / "iris.csv"
    with open(iris_path, "rb") as f:
        response = client.post(
            "/api/predict",
            files={"file": ("iris.csv", f, "text/csv")},
            data={"task": "classification", "target_column": "species"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["task"] == "classification"
    assert data["model_info"]["device"] in ["cpu", "cuda", "mps"]
    assert "metrics" in data
    assert data["metrics"]["accuracy"] > 0.8
    assert len(data["predictions"]) > 0
    assert data["summary"]["rows_train"] > 0


def test_predict_regression_house_prices():
    """Test /api/predict on regression task with house_prices dataset."""
    hp_path = SAMPLE_DIR / "house_prices.csv"
    with open(hp_path, "rb") as f:
        response = client.post(
            "/api/predict",
            files={"file": ("house_prices.csv", f, "text/csv")},
            data={"task": "regression", "target_column": "price"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["task"] == "regression"
    assert "metrics" in data
    assert "mae" in data["metrics"]
    assert len(data["predictions"]) > 0


def test_predict_forecast_daily_sales():
    """Test /api/predict on forecasting task with daily_sales dataset."""
    sales_path = SAMPLE_DIR / "daily_sales.csv"
    with open(sales_path, "rb") as f:
        response = client.post(
            "/api/predict",
            files={"file": ("daily_sales.csv", f, "text/csv")},
            data={
                "task": "forecast",
                "target_column": "units_sold",
                "time_column": "date",
                "horizon": "5",
            },
        )
    assert response.status_code == 200
    data = response.json()
    assert data["task"] == "forecast"
    assert "metrics" in data
    assert data["metrics"]["forecast_horizon"] == 5
    assert len(data["predictions"]) == 5
    assert data["predictions"][0]["timestamp"] is not None


def test_predict_forecast_dayfirst_date_format():
    """Test forecasting works with day-first dates like 19-02-2010."""
    csv_content = (
        "Date,sales\n"
        "19-02-2010,100\n"
        "20-02-2010,120\n"
        "21-02-2010,130\n"
        "22-02-2010,115\n"
        "23-02-2010,140\n"
        "24-02-2010,160\n"
        "25-02-2010,150\n"
    )
    response = client.post(
        "/api/predict",
        files={"file": ("custom_sales.csv", csv_content.encode("utf-8"), "text/csv")},
        data={
            "task": "forecast",
            "target_column": "sales",
            "time_column": "Date",
            "horizon": "3",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["task"] == "forecast"
    assert len(data["predictions"]) == 3


def test_predict_anomaly_sensor():
    """Test /api/predict on unsupervised anomaly detection."""
    sensor_path = SAMPLE_DIR / "sensor_anomaly.csv"
    with open(sensor_path, "rb") as f:
        response = client.post(
            "/api/predict",
            files={"file": ("sensor_anomaly.csv", f, "text/csv")},
            data={"task": "anomaly"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["task"] == "anomaly"
    assert "anomaly_scores" in data
    assert len(data["anomaly_scores"]) == 50
    assert "detected_anomalies_count" in data["metrics"]


def test_predict_missing_target_for_classification():
    """Test validation returns 422 when required target column is omitted."""
    iris_path = SAMPLE_DIR / "iris.csv"
    with open(iris_path, "rb") as f:
        response = client.post(
            "/api/predict",
            files={"file": ("iris.csv", f, "text/csv")},
            data={"task": "classification"},
        )
    assert response.status_code == 422
    data = response.json()
    assert data["error_code"] == "UNPROCESSABLE_DATA"
