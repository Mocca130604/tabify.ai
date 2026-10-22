"""High-level prediction service orchestrating preprocessing, splitting, TabPFN execution, and metrics."""

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    r2_score,
    mean_absolute_error,
    mean_squared_error,
)

from backend.app.schemas.predict import (
    PredictResponse,
    ModelInfo,
    PredictionItem,
    ExecutionSummary,
)
from backend.app.services.csv_service import csv_service
from backend.app.services.timeseries_prep import timeseries_prep
from backend.app.ml.tabpfn_engine import tabpfn_engine

logger = logging.getLogger(__name__)


class PredictionService:
    """Service orchestrating prediction workflows across classification, regression, forecast, and anomaly."""

    @classmethod
    def execute(
        cls,
        df: pd.DataFrame,
        task: str,
        target_column: Optional[str] = None,
        time_column: Optional[str] = None,
        horizon: int = 10,
        auto_subsample: bool = True,
    ) -> PredictResponse:
        """Main dispatcher for running predictions."""
        task = task.lower().strip()
        valid_tasks = {"classification", "regression", "forecast", "anomaly"}
        if task not in valid_tasks:
            raise ValueError(f"Task '{task}' is not supported. Must be one of {valid_tasks}.")

        if task in {"classification", "regression", "forecast"}:
            if not target_column:
                raise ValueError(f"target_column is required for task '{task}'.")
            if target_column not in df.columns:
                raise ValueError(f"target_column '{target_column}' does not exist in dataset columns.")

        if task == "classification":
            return cls._handle_classification(df, target_column, auto_subsample)
        elif task == "regression":
            return cls._handle_regression(df, target_column, auto_subsample)
        elif task == "forecast":
            return cls._handle_forecast(df, target_column, time_column, horizon, auto_subsample)
        elif task == "anomaly":
            return cls._handle_anomaly(df, auto_subsample)
        else:
            raise ValueError(f"Unhandled task: {task}")

    @classmethod
    def _handle_classification(
        cls,
        df: pd.DataFrame,
        target_col: str,
        auto_subsample: bool,
    ) -> PredictResponse:
        """Handle classification task using TabPFNClassifier."""
        target_series = df[target_col]
        feature_cols = [c for c in df.columns if c != target_col]
        X_clean, warnings = csv_service.clean_features(df, feature_cols)

        # Semantics: empty target vs hold-out split
        missing_mask = target_series.isna()
        has_unlabeled = missing_mask.any()

        if has_unlabeled:
            train_mask = ~missing_mask
            X_train = X_clean[train_mask]
            y_train = target_series[train_mask]
            X_pred = X_clean[missing_mask]
            pred_indices = df[missing_mask].index.tolist()
            actuals = [None] * len(pred_indices)
            metrics = None
        else:
            # 80/20 train/test holdout
            if len(df) < 5:
                raise ValueError("Dataset is too small for hold-out evaluation (minimum 5 rows).")

            # Check class distribution
            class_counts = target_series.value_counts()
            stratify_opt = target_series if (class_counts >= 2).all() else None

            X_tr, X_val, y_tr, y_val, idx_tr, idx_val = train_test_split(
                X_clean,
                target_series,
                df.index,
                test_size=0.2,
                random_state=42,
                stratify=stratify_opt,
            )
            X_train, y_train = X_tr, y_tr
            X_pred = X_val
            pred_indices = idx_val.tolist()
            actuals = y_val.tolist()

        # Validate context limits
        tabpfn_engine.check_data_limits(len(X_train), len(X_clean.columns), auto_subsample)

        preds, probs, meta = tabpfn_engine.fit_predict_classifier(
            X_train, y_train, X_pred, auto_subsample=auto_subsample
        )

        metrics = None
        if not has_unlabeled:
            acc = float(accuracy_score(actuals, preds))
            f1 = float(f1_score(actuals, preds, average="macro", zero_division=0))
            prec = float(precision_score(actuals, preds, average="macro", zero_division=0))
            rec = float(recall_score(actuals, preds, average="macro", zero_division=0))
            classes = meta.get("classes", sorted(list(set(actuals) | set(preds))))
            cm = confusion_matrix(actuals, preds, labels=classes).tolist()
            metrics = {
                "accuracy": acc,
                "f1_macro": f1,
                "precision_macro": prec,
                "recall_macro": rec,
                "confusion_matrix": {
                    "labels": [str(c) for c in classes],
                    "matrix": cm,
                },
            }

        prediction_items: List[PredictionItem] = []
        classes = meta.get("classes", [])
        for i, idx in enumerate(pred_indices):
            val = preds[i]
            # Convert numpy scalar to python native
            val_native = val.item() if hasattr(val, "item") else str(val)
            prob_dict = None
            if probs is not None and len(classes) == probs.shape[1]:
                prob_dict = {
                    str(cls_name): float(probs[i, c_idx])
                    for c_idx, cls_name in enumerate(classes)
                }

            act_native = actuals[i]
            if act_native is not None and hasattr(act_native, "item"):
                act_native = act_native.item()

            prediction_items.append(
                PredictionItem(
                    row_index=int(idx),
                    actual=act_native,
                    value=val_native,
                    probability=prob_dict,
                )
            )

        return PredictResponse(
            task="classification",
            model_info=ModelInfo(
                name=meta["model_name"],
                version=meta["version"],
                device=meta["device"],
                is_fallback=meta["is_fallback"],
            ),
            metrics=metrics,
            predictions=prediction_items,
            summary=ExecutionSummary(
                rows_train=len(X_train),
                rows_predict=len(X_pred),
                features_count=len(X_clean.columns),
                duration_ms=meta["duration_ms"],
                subsampled=meta["subsampled"],
            ),
            anomaly_scores=None,
        )

    @classmethod
    def _handle_regression(
        cls,
        df: pd.DataFrame,
        target_col: str,
        auto_subsample: bool,
    ) -> PredictResponse:
        """Handle numerical regression using TabPFNRegressor."""
        # Convert target to numeric
        target_series = pd.to_numeric(df[target_col], errors="coerce")
        feature_cols = [c for c in df.columns if c != target_col]
        X_clean, warnings = csv_service.clean_features(df, feature_cols)

        missing_mask = target_series.isna()
        has_unlabeled = missing_mask.any()

        if has_unlabeled:
            train_mask = ~missing_mask
            if train_mask.sum() == 0:
                raise ValueError("No rows with non-empty target values available to train TabPFNRegressor.")
            X_train = X_clean[train_mask]
            y_train = target_series[train_mask]
            X_pred = X_clean[missing_mask]
            pred_indices = df[missing_mask].index.tolist()
            actuals = [None] * len(pred_indices)
            metrics = None
        else:
            if len(df) < 5:
                raise ValueError("Dataset is too small for hold-out regression evaluation (minimum 5 rows).")

            X_tr, X_val, y_tr, y_val, idx_tr, idx_val = train_test_split(
                X_clean,
                target_series,
                df.index,
                test_size=0.2,
                random_state=42,
            )
            X_train, y_train = X_tr, y_tr
            X_pred = X_val
            pred_indices = idx_val.tolist()
            actuals = y_val.tolist()

        tabpfn_engine.check_data_limits(len(X_train), len(X_clean.columns), auto_subsample)

        preds, meta = tabpfn_engine.fit_predict_regressor(
            X_train, y_train, X_pred, auto_subsample=auto_subsample
        )

        metrics = None
        if not has_unlabeled:
            r2 = float(r2_score(actuals, preds))
            mae = float(mean_absolute_error(actuals, preds))
            mse = float(mean_squared_error(actuals, preds))
            rmse = float(np.sqrt(mse))
            metrics = {
                "r2_score": r2,
                "mae": mae,
                "mse": mse,
                "rmse": rmse,
            }

        prediction_items: List[PredictionItem] = []
        for i, idx in enumerate(pred_indices):
            val = float(preds[i])
            act = float(actuals[i]) if actuals[i] is not None else None
            prediction_items.append(
                PredictionItem(
                    row_index=int(idx),
                    actual=act,
                    value=val,
                )
            )

        return PredictResponse(
            task="regression",
            model_info=ModelInfo(
                name=meta["model_name"],
                version=meta["version"],
                device=meta["device"],
                is_fallback=meta["is_fallback"],
            ),
            metrics=metrics,
            predictions=prediction_items,
            summary=ExecutionSummary(
                rows_train=len(X_train),
                rows_predict=len(X_pred),
                features_count=len(X_clean.columns),
                duration_ms=meta["duration_ms"],
                subsampled=meta["subsampled"],
            ),
            anomaly_scores=None,
        )

    @classmethod
    def _handle_forecast(
        cls,
        df: pd.DataFrame,
        target_col: str,
        time_col: Optional[str],
        horizon: int,
        auto_subsample: bool,
    ) -> PredictResponse:
        """Handle time-series tabular forecasting using TabPFNRegressor."""
        if not time_col:
            # Try to auto-detect time column
            for c in df.columns:
                if c != target_col and ("date" in c.lower() or "time" in c.lower()):
                    time_col = c
                    break
        if not time_col or time_col not in df.columns:
            raise ValueError("time_column is required or could not be detected for forecast task.")

        X_train, y_train, X_future, future_timestamps = timeseries_prep.prepare_forecast_data(
            df, time_column=time_col, target_column=target_col, horizon=horizon
        )

        tabpfn_engine.check_data_limits(len(X_train), len(X_train.columns), auto_subsample)

        # In-sample validation metrics on last 20%
        val_size = max(1, int(len(X_train) * 0.2))
        X_tr = X_train.iloc[:-val_size]
        y_tr = y_train.iloc[:-val_size]
        X_val = X_train.iloc[-val_size:]
        y_val = y_train.iloc[-val_size:]

        val_preds, _ = tabpfn_engine.fit_predict_regressor(
            X_tr, y_tr, X_val, auto_subsample=auto_subsample
        )
        mae = float(mean_absolute_error(y_val, val_preds))
        mse = float(mean_squared_error(y_val, val_preds))
        rmse = float(np.sqrt(mse))
        r2 = float(r2_score(y_val, val_preds))

        # Predict future horizon using full historical context
        future_preds, meta = tabpfn_engine.fit_predict_regressor(
            X_train, y_train, X_future, auto_subsample=auto_subsample
        )

        prediction_items: List[PredictionItem] = []
        for i, ts in enumerate(future_timestamps):
            val = float(future_preds[i])
            prediction_items.append(
                PredictionItem(
                    row_index=i,
                    actual=None,
                    value=round(val, 2),
                    timestamp=ts.strftime("%Y-%m-%d") if hasattr(ts, "strftime") else str(ts),
                    probability=None,
                )
            )

        metrics = {
            "validation_mae": mae,
            "validation_rmse": rmse,
            "validation_r2": r2,
            "forecast_horizon": horizon,
        }

        return PredictResponse(
            task="forecast",
            model_info=ModelInfo(
                name=meta["model_name"],
                version=meta["version"],
                device=meta["device"],
                is_fallback=meta["is_fallback"],
            ),
            metrics=metrics,
            predictions=prediction_items,
            summary=ExecutionSummary(
                rows_train=len(X_train),
                rows_predict=len(X_future),
                features_count=len(X_train.columns),
                duration_ms=meta["duration_ms"],
                subsampled=meta["subsampled"],
            ),
            anomaly_scores=None,
        )

    @classmethod
    def _handle_anomaly(
        cls,
        df: pd.DataFrame,
        auto_subsample: bool,
    ) -> PredictResponse:
        """Handle unsupervised anomaly detection."""
        feature_cols = list(df.columns)
        X_clean, warnings = csv_service.clean_features(df, feature_cols)

        tabpfn_engine.check_data_limits(len(X_clean), len(X_clean.columns), auto_subsample)

        scores, meta = tabpfn_engine.fit_predict_anomaly(
            X_clean, auto_subsample=auto_subsample
        )

        # Anomaly threshold at 90th percentile
        threshold = float(np.percentile(scores, 90))
        outliers_count = int(np.sum(scores >= threshold))

        prediction_items: List[PredictionItem] = []
        for idx in range(len(df)):
            score = float(scores[idx])
            is_anomaly = bool(score >= threshold)
            prediction_items.append(
                PredictionItem(
                    row_index=idx,
                    actual=None,
                    value=is_anomaly,
                    probability={"anomaly_score": round(score, 4)},
                )
            )

        metrics = {
            "anomaly_threshold_90p": threshold,
            "detected_anomalies_count": outliers_count,
            "anomaly_rate_percent": round((outliers_count / len(df)) * 100.0, 2),
            "max_anomaly_score": float(np.max(scores)),
            "mean_anomaly_score": float(np.mean(scores)),
        }

        return PredictResponse(
            task="anomaly",
            model_info=ModelInfo(
                name=meta["model_name"],
                version=meta["version"],
                device=meta["device"],
                is_fallback=meta["is_fallback"],
            ),
            metrics=metrics,
            predictions=prediction_items,
            summary=ExecutionSummary(
                rows_train=len(X_clean),
                rows_predict=len(X_clean),
                features_count=len(X_clean.columns),
                duration_ms=meta["duration_ms"],
                subsampled=meta["subsampled"],
            ),
            anomaly_scores=[round(float(s), 4) for s in scores],
        )


prediction_service = PredictionService()
