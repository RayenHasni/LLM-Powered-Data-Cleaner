"""LLM-Powered Data Cleaner package."""

from .analyzer import DataAnalyzer
from .cleaner import DataCleaner

__all__ = ["DataAnalyzer", "DataCleaner", "DataCleaningAgent"]


def __getattr__(name: str):  # noqa: N807
    if name == "DataCleaningAgent":
        from .agent import DataCleaningAgent  # noqa: PLC0415
        return DataCleaningAgent
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
