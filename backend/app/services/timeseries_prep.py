"""Time-series preprocessing and tabular feature engineering for forecasting."""

from typing import List, Tuple
import pandas as pd
import numpy as np


class TimeSeriesPrep:
    """Prepare time-series datasets into tabular features for TabPFNRegressor."""

    @staticmethod
    def prepare_forecast_data(
        df: pd.DataFrame,
        time_column: str,
        target_column: str,
        horizon: int = 10,
    ) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, List[pd.Timestamp]]:
        """
        Convert time-series data into tabular lag/calendar features and generate future forecast horizon.

        Returns:
            X_train: Features for training rows
            y_train: Target values for training rows
            X_future: Features for the future horizon rows to predict
            future_timestamps: Datetime stamps corresponding to the future predictions
        """
        if time_column not in df.columns:
            raise ValueError(f"Time column '{time_column}' not found in data.")
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in data.")

        # Copy and sort by time
        data = df.copy()
        # Flexible datetime parsing
        parsed_dt = None
        for kwargs in [
            {"format": "mixed", "dayfirst": True},
            {"format": "mixed"},
            {"dayfirst": True},
            {},
        ]:
            try:
                parsed_dt = pd.to_datetime(data[time_column], **kwargs)
                break
            except Exception:
                continue

        if parsed_dt is None:
            raise ValueError(
                f"Failed to parse time column '{time_column}' as datetime. "
                "Please ensure the column contains dates in standard formats like DD-MM-YYYY, YYYY-MM-DD, or MM/DD/YYYY."
            )

        data[time_column] = parsed_dt

        data = data.sort_values(by=time_column).reset_index(drop=True)

        # Validate target is numeric
        data[target_column] = pd.to_numeric(data[target_column], errors="coerce")
        if data[target_column].dropna().empty:
            raise ValueError(f"Target column '{target_column}' has no valid numeric values.")

        # Infer frequency or time difference for future timestamps
        if len(data) >= 2:
            time_diffs = data[time_column].diff().dropna()
            step = time_diffs.median()
            if pd.isna(step) or step.total_seconds() <= 0:
                step = pd.Timedelta(days=1)
        else:
            step = pd.Timedelta(days=1)

        last_time = data[time_column].iloc[-1]
        future_timestamps = [last_time + step * (i + 1) for i in range(horizon)]

        # Calendar features generator
        def extract_calendar_features(dt_series: pd.Series) -> pd.DataFrame:
            cal = pd.DataFrame(index=dt_series.index)
            cal["year"] = dt_series.dt.year.astype(float)
            cal["month"] = dt_series.dt.month.astype(float)
            cal["day"] = dt_series.dt.day.astype(float)
            cal["dayofweek"] = dt_series.dt.dayofweek.astype(float)
            cal["dayofyear"] = dt_series.dt.dayofyear.astype(float)
            cal["is_weekend"] = dt_series.dt.dayofweek.isin([5, 6]).astype(float)
            return cal

        cal_df = extract_calendar_features(data[time_column])

        # Lag and rolling features on target
        lags = pd.DataFrame(index=data.index)
        lags["lag_1"] = data[target_column].shift(1)
        lags["lag_2"] = data[target_column].shift(2)
        lags["lag_3"] = data[target_column].shift(3)
        lags["rolling_mean_3"] = data[target_column].shift(1).rolling(3, min_periods=1).mean()

        # Other exogenous numeric features
        exo_cols = [
            c for c in data.columns
            if c not in [time_column, target_column] and pd.api.types.is_numeric_dtype(data[c])
        ]
        exo_df = data[exo_cols].copy() if exo_cols else pd.DataFrame(index=data.index)

        # Combine all features for historical data
        full_features = pd.concat([cal_df, lags, exo_df], axis=1)

        # Drop rows where lag features are NaN (first few rows)
        valid_mask = ~full_features["lag_1"].isna() & ~data[target_column].isna()
        if not valid_mask.any():
            valid_mask = ~data[target_column].isna()

        X_train = full_features[valid_mask].copy().fillna(0.0)
        y_train = data.loc[valid_mask, target_column].copy()

        # Build X_future
        future_series = pd.Series(future_timestamps)
        future_cal = extract_calendar_features(future_series)

        last_known_vals = data[target_column].dropna().tolist()
        val_m1 = last_known_vals[-1] if len(last_known_vals) >= 1 else 0.0
        val_m2 = last_known_vals[-2] if len(last_known_vals) >= 2 else val_m1
        val_m3 = last_known_vals[-3] if len(last_known_vals) >= 3 else val_m2
        roll_3 = np.mean([val_m1, val_m2, val_m3])

        future_lags = pd.DataFrame(index=future_series.index)
        future_lags["lag_1"] = val_m1
        future_lags["lag_2"] = val_m2
        future_lags["lag_3"] = val_m3
        future_lags["rolling_mean_3"] = roll_3

        future_exo = pd.DataFrame(index=future_series.index)
        for col in exo_cols:
            future_exo[col] = data[col].median()

        X_future = pd.concat([future_cal, future_lags, future_exo], axis=1).fillna(0.0)

        # Align columns
        common_cols = [c for c in X_train.columns if c in X_future.columns]
        X_train = X_train[common_cols]
        X_future = X_future[common_cols]

        return X_train, y_train, X_future, future_timestamps


timeseries_prep = TimeSeriesPrep()
