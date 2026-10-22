"""Prediction request and response schemas."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """Information regarding the underlying TabPFN model and execution."""

    name: str = Field(..., json_schema_extra={"example": "TabPFNClassifier (v2)"})
    version: str = Field(..., json_schema_extra={"example": "9.2.0"})
    device: str = Field(..., json_schema_extra={"example": "cpu"})
    is_fallback: bool = Field(False, description="Whether fallback model was used")


class PredictionItem(BaseModel):
    """Single prediction record."""

    row_index: int
    actual: Optional[Any] = None
    value: Any
    probability: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None


class ExecutionSummary(BaseModel):
    """Summary of data context and inference timing."""

    rows_train: int
    rows_predict: int
    features_count: int
    duration_ms: float
    subsampled: bool = False


class PredictResponse(BaseModel):
    """Response payload for /api/predict."""

    task: str = Field(..., json_schema_extra={"example": "classification"})
    model_info: ModelInfo
    metrics: Optional[Dict[str, Any]] = None
    predictions: List[PredictionItem]
    summary: ExecutionSummary
    anomaly_scores: Optional[List[float]] = None
