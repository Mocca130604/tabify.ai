"""Prediction router handling multi-task TabPFN inference requests."""

import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from backend.app.config import settings
from backend.app.schemas.predict import PredictResponse
from backend.app.services.csv_service import csv_service
from backend.app.services.prediction_service import prediction_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Prediction"])


@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Execute local in-context TabPFN prediction",
)
async def predict_task(
    file: UploadFile = File(...),
    task: str = Form(..., description="'classification', 'regression', 'forecast', or 'anomaly'"),
    target_column: Optional[str] = Form(None, description="Name of the target column (required except for anomaly)"),
    time_column: Optional[str] = Form(None, description="Time/Date column for time-series forecast"),
    horizon: int = Form(10, description="Forecast step horizon (default 10)"),
    auto_subsample: bool = Form(True, description="Enable automatic subsampling if data exceeds safety thresholds"),
) -> PredictResponse:
    """Execute local foundation model inference via TabPFN."""
    # 1. Validate file extension
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_FILE_EXTENSION",
                "message": "Only CSV (.csv) files are supported.",
                "hint": "Please upload a valid CSV file.",
            },
        )

    # 2. Check file size limit
    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error_code": "FILE_TOO_LARGE",
                "message": f"Uploaded file exceeds maximum size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
                "hint": "Reduce file size or sample rows before submitting.",
            },
        )

    # 3. Parse CSV
    try:
        df = csv_service.read_csv_bytes(content, filename=file.filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "CSV_PARSING_ERROR",
                "message": str(e),
                "hint": "Verify delimiter and UTF-8 encoding.",
            },
        )

    # 4. Dispatch prediction through service layer
    try:
        response = prediction_service.execute(
            df=df,
            task=task,
            target_column=target_column,
            time_column=time_column,
            horizon=horizon,
            auto_subsample=auto_subsample,
        )
        return response
    except ValueError as e:
        # Business logic / parameter validation errors
        err_msg = str(e)
        logger.warning(f"Validation error during prediction: {err_msg}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail={
                "error_code": "UNPROCESSABLE_DATA",
                "message": err_msg,
                "hint": "Check selected target column, task alignment, and dataset dimensions.",
            },
        )
    except Exception as e:
        # Unexpected model or computation failure
        logger.exception(f"Unexpected prediction failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "MODEL_INFERENCE_FAILURE",
                "message": "Inference computation failed in the local TabPFN engine.",
                "hint": "Check model device compatibility or consult server logs.",
            },
        )
