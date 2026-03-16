"""LangChain prompt templates for the data-cleaning assistant."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

# ---------------------------------------------------------------------------
# Analysis & recommendation prompt
# ---------------------------------------------------------------------------

ANALYSIS_SYSTEM = (
    "You are an expert data quality engineer. "
    "Given a JSON-formatted dataset profile, you produce concise, actionable "
    "cleaning recommendations. "
    "For each issue you identify, describe: (1) the problem, (2) the affected "
    "column(s), and (3) the recommended cleaning action. "
    "Be specific and practical. Avoid vague advice."
)

ANALYSIS_HUMAN = (
    "Here is the quality profile of the dataset:\n\n"
    "{profile}\n\n"
    "Please analyze the data quality issues and provide a numbered list of "
    "cleaning recommendations."
)

analysis_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ANALYSIS_SYSTEM),
        ("human", ANALYSIS_HUMAN),
    ]
)

# ---------------------------------------------------------------------------
# Follow-up / clarification prompt (multi-turn)
# ---------------------------------------------------------------------------

CHAT_SYSTEM = (
    "You are an expert data quality engineer assisting a user in cleaning "
    "their dataset. "
    "You have already analyzed the dataset and provided initial recommendations. "
    "Answer follow-up questions clearly and concisely. "
    "If the user asks you to apply a specific cleaning step, describe exactly "
    "what transformation to perform on which column(s)."
)

chat_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", CHAT_SYSTEM),
        ("human", "{question}"),
    ]
)
