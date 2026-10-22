"""Inspection router to analyze uploaded CSV datasets."""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from backend.app.config import settings
from backend.app.schemas.inspect import InspectResponse
from backend.app.services.csv_service import csv_service

router = APIRouter(prefix="/api", tags=["Inspection"])


@router.post(
    "/inspect",
    response_model=InspectResponse,
    summary="Inspect CSV dataset structure and suggest task/target",
)
async def inspect_csv(file: UploadFile = File(...)) -> InspectResponse:
    """Analyze uploaded CSV, extract column metadata, 5 preview rows, and task suggestions."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_FILE_EXTENSION",
                "message": "Only CSV (.csv) files are supported.",
                "hint": "Ensure your file has a .csv extension and valid tabular format.",
            },
        )

    content = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "error_code": "FILE_TOO_LARGE",
                "message": f"Uploaded file exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.",
                "hint": "Please upload a smaller dataset or sub-sample rows before uploading.",
            },
        )

    try:
        df = csv_service.read_csv_bytes(content, filename=file.filename)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "CSV_PARSING_ERROR",
                "message": str(e),
                "hint": "Verify delimiter, UTF-8 encoding, and ensure the CSV is not empty.",
            },
        )

    try:
        response = csv_service.inspect_dataframe(df, filename=file.filename)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "INSPECTION_FAILED",
                "message": "An error occurred while inspecting data structure.",
                "hint": str(e),
            },
        )
