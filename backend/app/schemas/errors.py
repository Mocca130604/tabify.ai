"""Structured error schemas."""

from typing import Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Structured error payload compliant with Tabify.ai API contract."""

    error_code: str = Field(..., description="Unique machine-readable error identifier")
    message: str = Field(..., description="Human-readable description of the error")
    hint: Optional[str] = Field(None, description="Actionable suggestion to resolve the error")
