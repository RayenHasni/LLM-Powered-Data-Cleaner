"""LangChain + Gemini orchestration for the data-cleaning assistant."""

from __future__ import annotations

import os
from typing import Any

import pandas as pd
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from .analyzer import DataAnalyzer
from .cleaner import DataCleaner
from .prompts import analysis_prompt, chat_prompt


class DataCleaningAgent:
    """Orchestrates dataset profiling, LLM-powered analysis, and automated cleaning.

    Args:
        api_key: Google Gemini API key.  Falls back to the
            ``GOOGLE_API_KEY`` environment variable when omitted.
        model: Gemini model name (default ``"gemini-1.5-flash"``).
        temperature: Sampling temperature for the LLM (default ``0``).
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gemini-1.5-flash",
        temperature: float = 0,
    ) -> None:
        resolved_key = api_key or os.environ.get("GOOGLE_API_KEY", "")
        self._llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=temperature,
            google_api_key=resolved_key,
        )
        self._analysis_chain = analysis_prompt | self._llm | StrOutputParser()
        self._chat_chain = chat_prompt | self._llm | StrOutputParser()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, df: pd.DataFrame) -> dict[str, Any]:
        """Profile *df* and ask the LLM for cleaning recommendations.

        Returns a dict with:
        - ``"profile"``: the raw profile dict from :class:`DataAnalyzer`
        - ``"recommendations"``: the LLM's text recommendations
        """
        analyzer = DataAnalyzer(df)
        profile = analyzer.profile()
        profile_text = analyzer.profile_as_text()
        recommendations = self._analysis_chain.invoke({"profile": profile_text})
        return {"profile": profile, "recommendations": recommendations}

    def chat(self, question: str) -> str:
        """Answer a follow-up question about the dataset or cleaning steps."""
        return self._chat_chain.invoke({"question": question})

    def auto_clean(
        self,
        df: pd.DataFrame,
        drop_duplicates: bool = True,
        drop_missing_threshold: float = 0.5,
        fill_missing_strategy: str = "mean",
        coerce_types: bool = True,
        strip_whitespace: bool = True,
        drop_constant: bool = True,
        clip_outliers: bool = False,
    ) -> tuple[pd.DataFrame, list[str]]:
        """Apply a sequence of automated cleaning operations to *df*.

        Returns a tuple of ``(cleaned_df, log)`` where ``log`` is a list of
        human-readable descriptions of every operation that was applied.
        """
        cleaner = DataCleaner(df)
        if strip_whitespace:
            cleaner.strip_whitespace()
        if coerce_types:
            cleaner.coerce_types()
        if drop_duplicates:
            cleaner.drop_duplicates()
        if drop_missing_threshold < 1.0:
            cleaner.drop_missing(threshold=drop_missing_threshold)
        if fill_missing_strategy:
            cleaner.fill_missing(strategy=fill_missing_strategy)  # type: ignore[arg-type]
        if drop_constant:
            cleaner.drop_constant_columns()
        if clip_outliers:
            cleaner.clip_outliers()
        return cleaner.result(), cleaner.log
