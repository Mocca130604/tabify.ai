"""TabPFN ML Engine for local in-context inference."""

import os
import time
import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from backend.app.config import settings
from backend.app.ml.device import get_available_device

logger = logging.getLogger(__name__)


class TabPFNEngine:
    """Wrapper and execution manager for local TabPFN foundation models."""

    def __init__(self) -> None:
        self.device = get_available_device()
        self._ensure_environment()

    def _ensure_environment(self) -> None:
        """Set environment flags to guarantee headless and local behavior."""
        os.environ["TABPFN_NO_BROWSER"] = settings.TABPFN_NO_BROWSER
        if settings.TABPFN_TOKEN:
            os.environ["TABPFN_TOKEN"] = settings.TABPFN_TOKEN
        if settings.TABPFN_MODEL_CACHE_DIR:
            os.environ["TABPFN_MODEL_CACHE_DIR"] = settings.TABPFN_MODEL_CACHE_DIR

    def get_version(self) -> str:
        """Return installed TabPFN version."""
        try:
            import tabpfn
            return getattr(tabpfn, "__version__", "unknown")
        except ImportError:
            return "not-installed"

    def is_model_cached(self) -> bool:
        """Check if TabPFN model weights are already present locally in cache."""
        cache_dirs = [
            os.environ.get("TABPFN_MODEL_CACHE_DIR"),
            os.path.expanduser("~/.cache/tabpfn"),
            os.path.expanduser("~/.cache/huggingface/hub"),
            os.path.join(os.path.expanduser("~"), ".cache"),
        ]
        for cdir in cache_dirs:
            if cdir and os.path.exists(cdir):
                for root, _, files in os.walk(cdir):
                    for file in files:
                        if file.endswith(".ckpt") or "tabpfn" in file.lower():
                            return True
        return False

    def check_data_limits(
        self,
        n_samples: int,
        n_features: int,
        auto_subsample: bool = True,
    ) -> bool:
        """Validate sample and feature limits against TabPFN context capacity."""
        if not auto_subsample:
            if n_samples > settings.MAX_RECOMMENDED_SAMPLES:
                raise ValueError(
                    f"Dataset has {n_samples} rows which exceeds the recommended "
                    f"TabPFN context limit ({settings.MAX_RECOMMENDED_SAMPLES}). "
                    f"Please enable auto-subsampling or reduce rows."
                )
            if n_features > settings.MAX_RECOMMENDED_FEATURES:
                raise ValueError(
                    f"Dataset has {n_features} features which exceeds the recommended "
                    f"TabPFN limit ({settings.MAX_RECOMMENDED_FEATURES})."
                )
        return True

    def fit_predict_classifier(
        self,
        X_train: pd.DataFrame | np.ndarray,
        y_train: pd.Series | np.ndarray,
        X_pred: pd.DataFrame | np.ndarray,
        auto_subsample: bool = True,
    ) -> Tuple[np.ndarray, Optional[np.ndarray], Dict[str, Any]]:
        """Run classification using TabPFNClassifier locally."""
        start_time = time.time()
        from tabpfn import TabPFNClassifier

        # Convert to numpy arrays if necessary
        X_tr = np.asarray(X_train, dtype=np.float32)
        y_tr = np.asarray(y_train)
        X_pr = np.asarray(X_pred, dtype=np.float32)

        subsampled = False
        max_samples = (
            settings.MAX_CPU_SAMPLES
            if self.device == "cpu"
            else settings.MAX_RECOMMENDED_SAMPLES
        )
        if auto_subsample and len(X_tr) > max_samples:
            indices = np.random.RandomState(42).choice(
                len(X_tr), size=max_samples, replace=False
            )
            X_tr = X_tr[indices]
            y_tr = y_tr[indices]
            subsampled = True

        # CPU: fewer estimators for speed; GPU: use auto for better accuracy
        n_estimators = 2 if self.device == "cpu" else "auto"
        clf = TabPFNClassifier(
            model_path="tabpfn-v2-classifier.ckpt",
            device=self.device,
            n_estimators=n_estimators,
            ignore_pretraining_limits=True,
        )
        clf.fit(X_tr, y_tr)
        predictions = clf.predict(X_pr)

        probabilities = None
        try:
            probabilities = clf.predict_proba(X_pr)
            classes = clf.classes_.tolist()
        except Exception as e:
            logger.warning(f"Could not compute probabilities: {e}")
            classes = []

        duration_ms = (time.time() - start_time) * 1000.0

        meta = {
            "model_name": "TabPFNClassifier (v2)",
            "version": self.get_version(),
            "device": self.device,
            "is_fallback": False,
            "classes": classes,
            "duration_ms": duration_ms,
            "subsampled": subsampled,
        }
        return predictions, probabilities, meta

    def fit_predict_regressor(
        self,
        X_train: pd.DataFrame | np.ndarray,
        y_train: pd.Series | np.ndarray,
        X_pred: pd.DataFrame | np.ndarray,
        auto_subsample: bool = True,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Run numerical regression using TabPFNRegressor locally."""
        start_time = time.time()
        from tabpfn import TabPFNRegressor

        X_tr = np.asarray(X_train, dtype=np.float32)
        y_tr = np.asarray(y_train, dtype=np.float32)
        X_pr = np.asarray(X_pred, dtype=np.float32)

        subsampled = False
        max_samples = (
            settings.MAX_CPU_SAMPLES
            if self.device == "cpu"
            else settings.MAX_RECOMMENDED_SAMPLES
        )
        if auto_subsample and len(X_tr) > max_samples:
            indices = np.random.RandomState(42).choice(
                len(X_tr), size=max_samples, replace=False
            )
            X_tr = X_tr[indices]
            y_tr = y_tr[indices]
            subsampled = True

        # CPU: fewer estimators for speed; GPU: use auto for better accuracy
        n_estimators = 2 if self.device == "cpu" else "auto"
        reg = TabPFNRegressor(
            model_path="tabpfn-v2-regressor.ckpt",
            device=self.device,
            n_estimators=n_estimators,
            ignore_pretraining_limits=True,
        )
        reg.fit(X_tr, y_tr)
        predictions = reg.predict(X_pr)

        duration_ms = (time.time() - start_time) * 1000.0

        meta = {
            "model_name": "TabPFNRegressor",
            "version": self.get_version(),
            "device": self.device,
            "is_fallback": False,
            "duration_ms": duration_ms,
            "subsampled": subsampled,
        }
        return predictions, meta

    def fit_predict_anomaly(
        self,
        X: pd.DataFrame | np.ndarray,
        auto_subsample: bool = True,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Run unsupervised anomaly detection using tabpfn-extensions or robust fallback."""
        start_time = time.time()
        X_arr = np.asarray(X, dtype=np.float32)

        subsampled = False
        max_samples = (
            settings.MAX_CPU_SAMPLES
            if self.device == "cpu"
            else settings.MAX_RECOMMENDED_SAMPLES
        )
        if auto_subsample and len(X_arr) > max_samples:
            indices = np.random.RandomState(42).choice(
                len(X_arr), size=max_samples, replace=False
            )
            X_arr_fit = X_arr[indices]
            subsampled = True
        else:
            X_arr_fit = X_arr

        # Attempt PriorLabs tabpfn-extensions unsupervised module
        try:
            from tabpfn import TabPFNClassifier, TabPFNRegressor
            from tabpfn_extensions.unsupervised import TabPFNUnsupervisedModel

            n_estimators = 2 if self.device == "cpu" else "auto"
            clf = TabPFNClassifier(
                model_path="tabpfn-v2-classifier.ckpt",
                device=self.device,
                n_estimators=n_estimators,
                ignore_pretraining_limits=True,
            )
            reg = TabPFNRegressor(
                model_path="tabpfn-v2-regressor.ckpt",
                device=self.device,
                n_estimators=n_estimators,
                ignore_pretraining_limits=True,
            )
            model = TabPFNUnsupervisedModel(tabpfn_clf=clf, tabpfn_reg=reg)
            model.fit(X_arr_fit)
            raw_scores = model.outliers(X_arr)
            # Normalize scores between 0 and 1
            min_s, max_s = np.min(raw_scores), np.max(raw_scores)
            norm_scores = (
                (raw_scores - min_s) / (max_s - min_s + 1e-8)
                if max_s > min_s
                else np.zeros_like(raw_scores)
            )

            duration_ms = (time.time() - start_time) * 1000.0
            meta = {
                "model_name": "TabPFNUnsupervisedModel (tabpfn-extensions)",
                "version": self.get_version(),
                "device": self.device,
                "is_fallback": False,
                "duration_ms": duration_ms,
                "subsampled": subsampled,
            }
            return norm_scores, meta
        except Exception as exc:
            logger.info(
                f"tabpfn-extensions unsupervised unavailable ({exc}). Using IsolationForest fallback."
            )
            from sklearn.ensemble import IsolationForest

            iso = IsolationForest(
                n_estimators=100,
                contamination="auto",
                random_state=42,
            )
            iso.fit(X_arr_fit)
            # decision_function gives opposite score (lower is more anomalous)
            raw_scores = -iso.decision_function(X_arr)
            min_s, max_s = np.min(raw_scores), np.max(raw_scores)
            norm_scores = (
                (raw_scores - min_s) / (max_s - min_s + 1e-8)
                if max_s > min_s
                else np.zeros_like(raw_scores)
            )

            duration_ms = (time.time() - start_time) * 1000.0
            meta = {
                "model_name": "IsolationForest (Fallback - tabpfn-extensions not installed)",
                "version": self.get_version(),
                "device": self.device,
                "is_fallback": True,
                "duration_ms": duration_ms,
                "subsampled": subsampled,
            }
            return norm_scores, meta


# Singleton engine instance
tabpfn_engine = TabPFNEngine()
