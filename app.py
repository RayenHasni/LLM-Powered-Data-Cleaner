"""Streamlit UI for the LLM-Powered Data Cleaner."""

from __future__ import annotations

import io
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.data_cleaner import DataCleaningAgent, DataAnalyzer

load_dotenv()

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="LLM-Powered Data Cleaner",
    page_icon="🧹",
    layout="wide",
)

st.title("🧹 LLM-Powered Data Cleaner")
st.caption(
    "Upload a CSV dataset, get AI-driven quality analysis powered by Gemini, "
    "and apply automated cleaning in one click."
)

# ---------------------------------------------------------------------------
# Sidebar – configuration
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input(
        "Google Gemini API key",
        value=os.environ.get("GOOGLE_API_KEY", ""),
        type="password",
        help="Get your key at https://aistudio.google.com/app/apikey",
    )
    model = st.selectbox(
        "Gemini model",
        ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
        index=0,
    )

    st.divider()
    st.header("🔧 Auto-clean options")
    opt_drop_dup = st.checkbox("Drop duplicate rows", value=True)
    opt_strip_ws = st.checkbox("Strip whitespace from strings", value=True)
    opt_coerce = st.checkbox("Coerce object columns to correct types", value=True)
    opt_drop_missing_threshold = st.slider(
        "Drop columns with > X% missing values",
        min_value=0,
        max_value=100,
        value=50,
        step=5,
        format="%d%%",
    )
    opt_fill_strategy = st.selectbox(
        "Fill remaining missing values with",
        ["mean", "median", "mode", "ffill", "bfill"],
        index=0,
    )
    opt_drop_constant = st.checkbox("Drop constant columns", value=True)
    opt_clip_outliers = st.checkbox("Clip IQR outliers", value=False)

# ---------------------------------------------------------------------------
# File upload
# ---------------------------------------------------------------------------

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is None:
    st.info("⬆️ Upload a CSV file to get started.")
    st.stop()

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

df_raw = pd.read_csv(uploaded_file)

st.subheader("📋 Raw dataset")
st.dataframe(df_raw, use_container_width=True)
st.markdown(
    f"**Shape:** {df_raw.shape[0]:,} rows × {df_raw.shape[1]:,} columns"
)

# ---------------------------------------------------------------------------
# Quick profile (no LLM required)
# ---------------------------------------------------------------------------

with st.expander("📊 Dataset profile", expanded=True):
    analyzer = DataAnalyzer(df_raw)
    profile = analyzer.profile()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Rows", f"{profile['shape']['rows']:,}")
    col2.metric("Columns", profile["shape"]["columns"])
    col3.metric("Missing values", profile["missing"]["total"])
    col4.metric("Duplicate rows", profile["duplicates"]["count"])

    if profile["missing"]["per_column"]:
        st.markdown("**Missing values per column:**")
        missing_df = pd.DataFrame(profile["missing"]["per_column"]).T
        st.dataframe(missing_df, use_container_width=True)

    if profile["outliers"]:
        st.markdown("**Detected outliers (IQR method):**")
        outlier_df = pd.DataFrame(profile["outliers"]).T
        st.dataframe(outlier_df, use_container_width=True)

    if profile["constant_columns"]:
        st.markdown(
            f"**Constant columns:** {', '.join(profile['constant_columns'])}"
        )

# ---------------------------------------------------------------------------
# LLM analysis
# ---------------------------------------------------------------------------

st.subheader("🤖 AI Cleaning Recommendations")

if not api_key:
    st.warning(
        "Enter your Google Gemini API key in the sidebar to enable AI analysis."
    )
else:
    if st.button("✨ Analyze with Gemini", type="primary"):
        with st.spinner("Analyzing dataset with Gemini…"):
            try:
                agent = DataCleaningAgent(api_key=api_key, model=model)
                result = agent.analyze(df_raw)
                st.session_state["agent"] = agent
                st.session_state["recommendations"] = result["recommendations"]
            except Exception as exc:
                st.error(f"LLM analysis failed: {exc}")

    if "recommendations" in st.session_state:
        st.markdown(st.session_state["recommendations"])

        # Follow-up chat
        with st.expander("💬 Ask a follow-up question"):
            question = st.text_input(
                "Your question",
                placeholder="e.g. What strategy should I use for the 'age' column?",
            )
            if st.button("Ask") and question:
                with st.spinner("Thinking…"):
                    try:
                        answer = st.session_state["agent"].chat(question)
                        st.markdown(answer)
                    except Exception as exc:
                        st.error(f"Chat failed: {exc}")

# ---------------------------------------------------------------------------
# Automated cleaning
# ---------------------------------------------------------------------------

st.subheader("🧽 Automated Cleaning")

if st.button("🚀 Apply cleaning", type="primary"):
    if not api_key and not any(
        [opt_drop_dup, opt_strip_ws, opt_coerce, opt_drop_constant, opt_clip_outliers]
    ):
        st.info("Select at least one cleaning option from the sidebar.")
    else:
        agent_for_clean = DataCleaningAgent(api_key=api_key or "placeholder", model=model)
        cleaned_df, clean_log = agent_for_clean.auto_clean(
            df_raw,
            drop_duplicates=opt_drop_dup,
            drop_missing_threshold=opt_drop_missing_threshold / 100,
            fill_missing_strategy=opt_fill_strategy,
            coerce_types=opt_coerce,
            strip_whitespace=opt_strip_ws,
            drop_constant=opt_drop_constant,
            clip_outliers=opt_clip_outliers,
        )
        st.session_state["cleaned_df"] = cleaned_df
        st.session_state["clean_log"] = clean_log

if "cleaned_df" in st.session_state:
    cleaned_df = st.session_state["cleaned_df"]
    clean_log = st.session_state["clean_log"]

    st.success("✅ Cleaning complete!")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(
            f"**Before:** {df_raw.shape[0]:,} rows × {df_raw.shape[1]:,} columns"
        )
    with col_b:
        st.markdown(
            f"**After:** {cleaned_df.shape[0]:,} rows × {cleaned_df.shape[1]:,} columns"
        )

    with st.expander("🗒️ Cleaning log"):
        for entry in clean_log:
            st.markdown(f"- {entry}")

    st.subheader("✨ Cleaned dataset")
    st.dataframe(cleaned_df, use_container_width=True)

    # Download
    csv_bytes = cleaned_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download cleaned CSV",
        data=csv_bytes,
        file_name="cleaned_data.csv",
        mime="text/csv",
    )
