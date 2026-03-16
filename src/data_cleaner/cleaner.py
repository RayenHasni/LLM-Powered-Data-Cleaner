"""Automated cleaning functions applied to a pandas DataFrame."""

from __future__ import annotations

from typing import Literal

import numpy as np
import pandas as pd


class DataCleaner:
    """Applies deterministic cleaning operations to a DataFrame.

    All methods return ``self`` to support method chaining and record every
    operation applied in ``self.log``.
    """

    def __init__(self, df: pd.DataFrame) -> None:
        self.df: pd.DataFrame = df.copy()
        self.log: list[str] = []

    # ------------------------------------------------------------------
    # Cleaning operations
    # ------------------------------------------------------------------

    def drop_duplicates(self) -> "DataCleaner":
        """Remove exact duplicate rows."""
        before = len(self.df)
        self.df = self.df.drop_duplicates().reset_index(drop=True)
        removed = before - len(self.df)
        self.log.append(f"drop_duplicates: removed {removed} duplicate row(s).")
        return self

    def drop_missing(self, threshold: float = 0.5) -> "DataCleaner":
        """Drop columns where the fraction of missing values exceeds *threshold*.

        Args:
            threshold: Maximum allowed proportion of missing values (0–1).
        """
        missing_frac = self.df.isnull().mean()
        cols_to_drop = missing_frac[missing_frac > threshold].index.tolist()
        self.df = self.df.drop(columns=cols_to_drop)
        self.log.append(
            f"drop_missing (threshold={threshold}): dropped columns {cols_to_drop}."
        )
        return self

    def fill_missing(
        self,
        strategy: Literal["mean", "median", "mode", "ffill", "bfill"] = "mean",
        columns: list[str] | None = None,
    ) -> "DataCleaner":
        """Impute missing values.

        Args:
            strategy: Imputation strategy. ``'mean'``/``'median'`` apply only
                to numeric columns; ``'mode'`` applies to all columns;
                ``'ffill'``/``'bfill'`` use forward/back fill.
            columns: Subset of columns to impute. Defaults to all columns.
        """
        cols = columns if columns is not None else self.df.columns.tolist()
        for col in cols:
            if col not in self.df.columns:
                continue
            if strategy == "mean" and pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(self.df[col].mean())
            elif strategy == "median" and pd.api.types.is_numeric_dtype(self.df[col]):
                self.df[col] = self.df[col].fillna(self.df[col].median())
            elif strategy == "mode":
                mode_val = self.df[col].mode()
                if not mode_val.empty:
                    self.df[col] = self.df[col].fillna(mode_val.iloc[0])
            elif strategy == "ffill":
                self.df[col] = self.df[col].ffill()
            elif strategy == "bfill":
                self.df[col] = self.df[col].bfill()
        self.log.append(
            f"fill_missing (strategy={strategy}, columns={cols})."
        )
        return self

    def coerce_types(self) -> "DataCleaner":
        """Try to coerce object columns to numeric or datetime types."""
        for col in self.df.select_dtypes(include=["object", "string"]).columns:
            converted = pd.to_numeric(self.df[col], errors="coerce")
            if converted.notna().sum() > 0.5 * len(self.df):
                self.df[col] = converted
                self.log.append(f"coerce_types: '{col}' converted to numeric.")
                continue
            # Try datetime
            try:
                converted_dt = pd.to_datetime(self.df[col], errors="coerce")
                if converted_dt.notna().sum() > 0.5 * len(self.df):
                    self.df[col] = converted_dt
                    self.log.append(
                        f"coerce_types: '{col}' converted to datetime."
                    )
            except Exception:
                pass
        return self

    def strip_whitespace(self) -> "DataCleaner":
        """Strip leading/trailing whitespace from all string columns."""
        for col in self.df.select_dtypes(include=["object", "string"]).columns:
            self.df[col] = self.df[col].str.strip()
        self.log.append("strip_whitespace: stripped string columns.")
        return self

    def drop_constant_columns(self) -> "DataCleaner":
        """Drop columns that contain only a single unique non-null value."""
        to_drop = [
            col
            for col in self.df.columns
            if self.df[col].dropna().nunique() <= 1
        ]
        self.df = self.df.drop(columns=to_drop)
        self.log.append(
            f"drop_constant_columns: dropped {to_drop}."
        )
        return self

    def clip_outliers(self, columns: list[str] | None = None) -> "DataCleaner":
        """Clip outliers in numeric columns to the IQR-based fence values.

        Args:
            columns: Numeric columns to clip. Defaults to all numeric columns.
        """
        num_cols = self.df.select_dtypes(include="number").columns.tolist()
        cols = columns if columns is not None else num_cols
        for col in cols:
            if col not in self.df.columns:
                continue
            series = self.df[col].dropna()
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            self.df[col] = self.df[col].clip(lower=lower, upper=upper)
        self.log.append(
            f"clip_outliers: clipped columns {cols} to IQR bounds."
        )
        return self

    # ------------------------------------------------------------------
    # Result
    # ------------------------------------------------------------------

    def result(self) -> pd.DataFrame:
        """Return the cleaned DataFrame."""
        return self.df.copy()
