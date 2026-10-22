"""Health router exposing status, TabPFN version, device catalog, and live device switching."""

import logging
from typing import Literal
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.schemas.health import HealthResponse
from backend.app.ml.tabpfn_engine import tabpfn_engine
from backend.app.ml.device import is_cuda_available, is_mps_available, get_device_catalog

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["System"])


@router.get("/health", response_model=HealthResponse)
def get_health() -> HealthResponse:
    """Check backend operational health and TabPFN environment status."""
    catalog_data = get_device_catalog()
    return HealthResponse(
        status="healthy",
        tabpfn_version=tabpfn_engine.get_version(),
        device=tabpfn_engine.device,
        cuda_available=is_cuda_available(),
        mps_available=is_mps_available(),
        model_cached=tabpfn_engine.is_model_cached(),
        supported_tasks=["classification", "regression", "forecast", "anomaly"],
        device_catalog=catalog_data["devices"],
    )


# ── Runtime device switching ──────────────────────────────────────────────────

class DeviceSwitchRequest(BaseModel):
    """Request body for changing the active compute device."""
    device: str = Field(
        ...,
        description="Target device: 'cpu', 'cuda' (NVIDIA or AMD ROCm), or 'mps' (Apple Silicon)",
    )


class DeviceSwitchResponse(BaseModel):
    previous_device: str
    active_device: str
    message: str


@router.post("/device", response_model=DeviceSwitchResponse, summary="Switch compute device at runtime")
def switch_device(body: DeviceSwitchRequest) -> DeviceSwitchResponse:
    """Switch the TabPFN engine to a different compute device at runtime.

    Valid values: `cpu`, `cuda` (NVIDIA / AMD ROCm), `mps` (Apple Silicon).
    The change persists for the lifetime of the server process.
    """
    requested = body.device.lower().strip()
    valid = {"cpu", "cuda", "mps"}
    if requested not in valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error_code": "INVALID_DEVICE",
                "message": f"Device '{requested}' is not supported. Choose from: {sorted(valid)}.",
                "hint": "Use 'cuda' for both NVIDIA and AMD ROCm GPUs.",
            },
        )

    # Availability guard
    if requested == "cuda" and not is_cuda_available():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "DEVICE_UNAVAILABLE",
                "message": "No CUDA-capable GPU (NVIDIA or AMD ROCm) was detected on this machine.",
                "hint": "Install PyTorch with CUDA or ROCm support and ensure GPU drivers are present.",
            },
        )
    if requested == "mps" and not is_mps_available():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error_code": "DEVICE_UNAVAILABLE",
                "message": "Apple MPS is not available on this machine.",
                "hint": "MPS requires an Apple Silicon Mac (M1/M2/M3+) running macOS 12.3+.",
            },
        )

    previous = tabpfn_engine.device
    tabpfn_engine.device = requested
    logger.info(f"Device switched: {previous} → {requested}")

    return DeviceSwitchResponse(
        previous_device=previous,
        active_device=tabpfn_engine.device,
        message=f"TabPFN engine will now run on '{requested}'.",
    )
