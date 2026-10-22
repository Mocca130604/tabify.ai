"""Inspection schemas for CSV file analysis."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ColumnMetadata(BaseModel):
    """Metadata describing a single column."""

    name: str
    dtype: str
    missing_count: int
    unique_count: int
    sample_values: List[Any] = Field(default_factory=list)


class DroppedColumnNotice(BaseModel):
    """Notice for dropped columns (such as IDs or constants)."""

    column: str
    reason: str


class TaskSuggestions(BaseModel):
    """Automatic suggestions inferred from data analysis."""

    recommended_task: str = Field(..., json_schema_extra={"example": "classification"})
    recommended_target: Optional[str] = Field(None, json_schema_extra={"example": "species"})
    recommended_time_column: Optional[str] = Field(None, json_schema_extra={"example": "date"})


class InspectResponse(BaseModel):
    """Response payload for /api/inspect."""

    filename: str
    row_count: int
    column_count: int
    columns: List[ColumnMetadata]
    preview_rows: List[Dict[str, Any]]
    dropped_columns: List[DroppedColumnNotice] = Field(default_factory=list)
    suggestions: TaskSuggestions
