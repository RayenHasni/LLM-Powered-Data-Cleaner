"""Tests for DataAnalyzer."""

import numpy as np
import pandas as pd
import pytest

from src.data_cleaner.analyzer import DataAnalyzer


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [25, 30, None, 40, 200],  # 200 is an outlier
            "salary": [50000, None, 70000, 80000, 90000],
            "name": ["Alice", "Bob", None, "Dave", "Eve"],
            "constant": [1, 1, 1, 1, 1],
            "duplicate_check": [1, 2, 3, 4, 5],
        }
    )


def test_shape(sample_df):
    profile = DataAnalyzer(sample_df).profile()
    assert profile["shape"] == {"rows": 5, "columns": 5}


def test_missing_detected(sample_df):
    profile = DataAnalyzer(sample_df).profile()
    assert profile["missing"]["total"] > 0
    assert "age" in profile["missing"]["per_column"]
    assert "salary" in profile["missing"]["per_column"]
    assert "name" in profile["missing"]["per_column"]


def test_no_duplicates(sample_df):
    profile = DataAnalyzer(sample_df).profile()
    assert profile["duplicates"]["count"] == 0


def test_duplicates_detected():
    df = pd.DataFrame({"a": [1, 1, 2], "b": ["x", "x", "y"]})
    profile = DataAnalyzer(df).profile()
    assert profile["duplicates"]["count"] == 1


def test_numeric_stats_computed(sample_df):
    profile = DataAnalyzer(sample_df).profile()
    assert "age" in profile["numeric_stats"]
    assert "mean" in profile["numeric_stats"]["age"]


def test_outlier_detected(sample_df):
    profile = DataAnalyzer(sample_df).profile()
    assert "age" in profile["outliers"]


def test_constant_column_detected(sample_df):
    profile = DataAnalyzer(sample_df).profile()
    assert "constant" in profile["constant_columns"]


def test_profile_as_text_is_json(sample_df):
    import json
    text = DataAnalyzer(sample_df).profile_as_text()
    parsed = json.loads(text)
    assert "shape" in parsed


def test_empty_dataframe():
    profile = DataAnalyzer(pd.DataFrame()).profile()
    assert profile["shape"]["rows"] == 0
    assert profile["missing"]["total"] == 0
