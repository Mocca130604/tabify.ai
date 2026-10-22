"""CSV parsing, inspection, validation, and sanitization service."""

import io
import re
import logging
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

from backend.app.schemas.inspect import ColumnMetadata, DroppedColumnNotice, TaskSuggestions, InspectResponse

logger = logging.getLogger(__name__)


class CSVService:
    """Service handling CSV reading, metadata extraction, and feature preparation."""

    @staticmethod
    def read_csv_bytes(file_bytes: bytes, filename: str = "upload.csv") -> pd.DataFrame:
        """Decode and parse raw bytes into a pandas DataFrame safely."""
        if not file_bytes or len(file_bytes.strip()) == 0:
            raise ValueError("The provided CSV file is empty.")

        # Try UTF-8 first, fallback to Latin-1
        try:
            content = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                content = file_bytes.decode("latin-1")
            except Exception as e:
                raise ValueError(f"Unable to decode CSV file encoding: {e}")

        try:
            df = pd.read_csv(io.StringIO(content))
        except Exception as e:
            raise ValueError(f"Failed to parse CSV: {e}")

        if df.empty or len(df.columns) == 0:
            raise ValueError("Parsed CSV contains no rows or columns.")

        # Strip whitespace from column headers
        df.columns = [str(col).strip() for col in df.columns]
        return df

    @classmethod
    def inspect_dataframe(cls, df: pd.DataFrame, filename: str) -> InspectResponse:
        """Inspect dataframe properties, columns, preview, and generate smart suggestions."""
        columns_meta: List[ColumnMetadata] = []
        dropped_columns: List[DroppedColumnNotice] = []

        total_rows = len(df)
        potential_time_cols: List[str] = []
        potential_cat_cols: List[str] = []
        potential_num_cols: List[str] = []

        for col in df.columns:
            series = df[col]
            missing_count = int(series.isna().sum())
            unique_count = int(series.nunique(dropna=True))
            dtype_str = str(series.dtype)

            # Check if column is constant
            if unique_count <= 1 and total_rows > 1:
                dropped_columns.append(
                    DroppedColumnNotice(
                        column=col,
                        reason="Constant column (all values are identical)."
                    )
                )

            # Check if column is an ID column
            is_id_name = bool(re.search(r"(^id$|_id$|^id_)", col, re.IGNORECASE))
            if is_id_name or (unique_count == total_rows and total_rows > 20 and pd.api.types.is_string_dtype(series)):
                dropped_columns.append(
                    DroppedColumnNotice(
                        column=col,
                        reason="Identifier / Key column (high cardinality or labeled as ID)."
                    )
                )

            # Classify column candidates
            sample_non_null = series.dropna().head(5).tolist()

            # Time check
            if "date" in col.lower() or "time" in col.lower() or "timestamp" in col.lower():
                potential_time_cols.append(col)
            else:
                try:
                    # Quick date parse check on first 5 non-null rows
                    if pd.api.types.is_string_dtype(series) and len(sample_non_null) > 0:
                        pd.to_datetime(sample_non_null, format="mixed", errors="raise")
                        potential_time_cols.append(col)
                except Exception:
                    pass

            # Target candidates
            if pd.api.types.is_numeric_dtype(series):
                potential_num_cols.append(col)
            else:
                if 2 <= unique_count <= 20:
                    potential_cat_cols.append(col)

            columns_meta.append(
                ColumnMetadata(
                    name=col,
                    dtype=dtype_str,
                    missing_count=missing_count,
                    unique_count=unique_count,
                    sample_values=sample_non_null,
                )
            )

        # Smart Task & Target suggestions
        rec_task = "classification"
        rec_target = None
        rec_time = None

        if potential_time_cols:
            rec_task = "forecast"
            rec_time = potential_time_cols[0]
            # pick a numeric column as forecast target
            num_targets = [c for c in potential_num_cols if c != rec_time]
            if num_targets:
                rec_target = num_targets[-1]
        elif potential_cat_cols:
            rec_task = "classification"
            rec_target = potential_cat_cols[-1]
        elif potential_num_cols:
            rec_task = "regression"
            rec_target = potential_num_cols[-1]
        else:
            rec_task = "anomaly"

        # Sanitize preview rows (replace NaN with None for valid JSON serialization)
        preview_df = df.head(5).replace({np.nan: None})
        preview_rows = preview_df.to_dict(orient="records")

        return InspectResponse(
            filename=filename,
            row_count=total_rows,
            column_count=len(df.columns),
            columns=columns_meta,
            preview_rows=preview_rows,
            dropped_columns=dropped_columns,
            suggestions=TaskSuggestions(
                recommended_task=rec_task,
                recommended_target=rec_target,
                recommended_time_column=rec_time,
            ),
        )

    @classmethod
    def clean_features(
        cls,
        df: pd.DataFrame,
        feature_cols: List[str],
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Preprocess feature columns: drop constants, IDs, impute missing, and encode categoricals."""
        warnings: List[str] = []
        cleaned_df = pd.DataFrame(index=df.index)

        for col in feature_cols:
            if col not in df.columns:
                continue

            series = df[col]
            unique_count = series.nunique(dropna=True)

            # Drop constants
            if unique_count <= 1:
                warnings.append(f"Dropped constant feature '{col}'.")
                continue

            # Drop IDs
            is_id_name = bool(re.search(r"(^id$|_id$|^id_)", col, re.IGNORECASE))
            if is_id_name and unique_count > len(df) * 0.9:
                warnings.append(f"Dropped high-cardinality identifier '{col}'.")
                continue

            # Handle Numeric
            if pd.api.types.is_numeric_dtype(series):
                col_data = pd.to_numeric(series, errors="coerce")
                if col_data.isna().all():
                    warnings.append(f"Dropped numeric feature '{col}' because all values are missing.")
                    continue
                median_val = col_data.median()
                cleaned_df[col] = col_data.fillna(median_val if not pd.isna(median_val) else 0.0)
            else:
                # Categorical / string encoding (Ordinal mapping to integers)
                mode_val = series.mode().iloc[0] if not series.mode().empty else "missing"
                filled_series = series.fillna(mode_val).astype(str)
                # Map categories to integer codes
                categories = {cat: idx for idx, cat in enumerate(filled_series.unique())}
                cleaned_df[col] = filled_series.map(categories).astype(float)

        if cleaned_df.empty or len(cleaned_df.columns) == 0:
            raise ValueError("All feature columns were dropped during preprocessing or no valid features remain.")

        return cleaned_df, warnings


csv_service = CSVService()
