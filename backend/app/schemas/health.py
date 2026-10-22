"""Health check response schema."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DeviceInfo(BaseModel):
    """Info about a single compute device option."""
    id: str = Field(..., description="PyTorch device string: 'cpu', 'cuda', or 'mps'")
    label: str = Field(..., description="Human-readable device name")
    vendor: str = Field(..., description="'cpu' | 'nvidia' | 'amd' | 'apple'")
    vram_gb: Optional[float] = Field(None, description="GPU VRAM in GB (GPU only)")
    available: bool = Field(..., description="Whether this device is currently usable")
    recommended: bool = Field(False, description="True if this is a faster-than-CPU option")


class HealthResponse(BaseModel):
    """System and TabPFN health response."""

    status: str = Field(..., json_schema_extra={"example": "healthy"})
    tabpfn_version: str = Field(..., json_schema_extra={"example": "2.0.0"})
    device: str = Field(..., description="Active device used by TabPFN engine", json_schema_extra={"example": "cpu"})
    cuda_available: bool = Field(..., json_schema_extra={"example": False})
    mps_available: bool = Field(..., json_schema_extra={"example": False})
    model_cached: bool = Field(..., json_schema_extra={"example": True})
    supported_tasks: List[str] = Field(
        default_factory=lambda: ["classification", "regression", "forecast", "anomaly"]
    )
    # Full device catalog for the UI selector
    device_catalog: List[DeviceInfo] = Field(default_factory=list)
