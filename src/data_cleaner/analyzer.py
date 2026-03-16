"""DataFrame profiling utilities for the data-cleaning assistant."""

from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd


class DataAnalyzer:
    """Analyzes a pandas DataFrame and produces a structured quality report."""

    def __init__(self, df: pd.DataFrame) -> None:
        self.df = df.copy()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def profile(self) -> dict[str, Any]:
        """Return a full quality profile of the dataset."""
        return {
            "shape": self._shape(),
            "dtypes": self._dtypes(),
            "missing": self._missing(),
            "duplicates": self._duplicates(),
            "numeric_stats": self._numeric_stats(),
            "outliers": self._outliers(),
            "constant_columns": self._constant_columns(),
        }

    def profile_as_text(self) -> str:
        """Return the profile serialised as a pretty-printed JSON string."""
        return json.dumps(self.profile(), indent=2, default=str)

    # ------------------------------------------------------------------
    # Individual checks
    # ------------------------------------------------------------------

    def _shape(self) -> dict[str, int]:
        rows, cols = self.df.shape
        return {"rows": rows, "columns": cols}

    def _dtypes(self) -> dict[str, str]:
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}

    def _missing(self) -> dict[str, Any]:
        total = int(self.df.isnull().sum().sum())
        per_column = {
            col: {
                "count": int(n),
                "pct": round(float(n) / max(len(self.df), 1) * 100, 2),
            }
            for col, n in self.df.isnull().sum().items()
            if n > 0
        }
        return {"total": total, "per_column": per_column}

    def _duplicates(self) -> dict[str, int]:
        return {"count": int(self.df.duplicated().sum())}

    def _numeric_stats(self) -> dict[str, Any]:
        num_df = self.df.select_dtypes(include="number")
        if num_df.empty:
            return {}
        stats: dict[str, Any] = {}
        for col in num_df.columns:
            series = num_df[col].dropna()
            stats[col] = {
                "mean": round(float(series.mean()), 4),
                "median": round(float(series.median()), 4),
                "std": round(float(series.std()), 4),
                "min": round(float(series.min()), 4),
                "max": round(float(series.max()), 4),
            }
        return stats

    def _outliers(self) -> dict[str, Any]:
        """IQR-based outlier detection for numeric columns."""
        num_df = self.df.select_dtypes(include="number")
        result: dict[str, Any] = {}
        for col in num_df.columns:
            series = num_df[col].dropna()
            q1, q3 = float(series.quantile(0.25)), float(series.quantile(0.75))
            iqr = q3 - q1
            lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
            n_outliers = int(((series < lower) | (series > upper)).sum())
            if n_outliers > 0:
                result[col] = {
                    "count": n_outliers,
                    "lower_bound": round(lower, 4),
                    "upper_bound": round(upper, 4),
                }
        return result

    def _constant_columns(self) -> list[str]:
        """Columns with only one unique non-null value."""
        return [
            col
            for col in self.df.columns
            if self.df[col].dropna().nunique() <= 1
        ]
