"""Tests for DataCleaner."""

import numpy as np
import pandas as pd
import pytest

from src.data_cleaner.cleaner import DataCleaner


@pytest.fixture()
def sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "age": [25.0, 30.0, None, 40.0, 25.0],
            "salary": [50000.0, None, 70000.0, 80000.0, 50000.0],
            "name": ["  Alice  ", "Bob", None, "Dave", "  Alice  "],
            "constant": [1, 1, 1, 1, 1],
            "numeric_str": ["1", "2", "3", "4", "5"],
        }
    )


def test_drop_duplicates():
    df = pd.DataFrame(
        {
            "age": [25.0, 30.0, 25.0],
            "name": ["Alice", "Bob", "Alice"],
        }
    )
    cleaner = DataCleaner(df)
    cleaner.drop_duplicates()
    assert len(cleaner.result()) < len(df)
    assert any("drop_duplicates" in entry for entry in cleaner.log)


def test_drop_missing_threshold():
    df = pd.DataFrame({"a": [1, None, None], "b": [1, 2, 3]})
    cleaner = DataCleaner(df)
    cleaner.drop_missing(threshold=0.5)
    assert "a" not in cleaner.result().columns
    assert "b" in cleaner.result().columns


def test_fill_missing_mean(sample_df):
    cleaner = DataCleaner(sample_df)
    cleaner.fill_missing(strategy="mean", columns=["age", "salary"])
    result = cleaner.result()
    assert result["age"].isnull().sum() == 0
    assert result["salary"].isnull().sum() == 0


def test_fill_missing_mode():
    df = pd.DataFrame({"cat": ["a", "a", None, "b"]})
    cleaner = DataCleaner(df)
    cleaner.fill_missing(strategy="mode", columns=["cat"])
    assert cleaner.result()["cat"].isnull().sum() == 0
    assert cleaner.result()["cat"].iloc[2] == "a"


def test_strip_whitespace(sample_df):
    cleaner = DataCleaner(sample_df)
    cleaner.strip_whitespace()
    result = cleaner.result()
    assert result["name"].iloc[0] == "Alice"
    assert result["name"].iloc[4] == "Alice"


def test_coerce_types(sample_df):
    cleaner = DataCleaner(sample_df)
    cleaner.coerce_types()
    result = cleaner.result()
    assert pd.api.types.is_numeric_dtype(result["numeric_str"])


def test_drop_constant_columns(sample_df):
    cleaner = DataCleaner(sample_df)
    cleaner.drop_constant_columns()
    assert "constant" not in cleaner.result().columns


def test_clip_outliers():
    df = pd.DataFrame({"val": [1.0, 2.0, 3.0, 4.0, 100.0]})
    cleaner = DataCleaner(df)
    cleaner.clip_outliers(columns=["val"])
    result = cleaner.result()
    assert result["val"].max() < 100.0


def test_method_chaining(sample_df):
    result_df = (
        DataCleaner(sample_df)
        .strip_whitespace()
        .drop_duplicates()
        .fill_missing(strategy="mean")
        .result()
    )
    assert isinstance(result_df, pd.DataFrame)


def test_log_populated(sample_df):
    cleaner = DataCleaner(sample_df)
    cleaner.drop_duplicates()
    cleaner.fill_missing()
    assert len(cleaner.log) == 2


def test_result_returns_copy(sample_df):
    cleaner = DataCleaner(sample_df)
    result1 = cleaner.result()
    result2 = cleaner.result()
    result1.loc[0, "age"] = 9999
    assert result2.loc[0, "age"] != 9999
