# LLM-Powered Data Cleaner

An AI-powered data cleaning assistant that combines **LangChain** + **Google Gemini** with automated pandas transformations to deliver prompt-driven analysis and cleaning recommendations for tabular datasets.

---

## Features

| Feature | Description |
|---|---|
| 📊 **Dataset profiling** | Missing values, duplicates, outliers, constant columns, data-type audit |
| 🤖 **Gemini-powered analysis** | LLM reads the dataset profile and generates prioritised, actionable cleaning recommendations |
| 💬 **Follow-up chat** | Ask natural-language follow-up questions about your data |
| 🧽 **Automated cleaning** | One-click pipeline: strip whitespace → coerce types → drop duplicates → impute missing values → clip outliers |
| ⬇️ **Download** | Export the cleaned CSV directly from the UI |

---

## Architecture

```
src/data_cleaner/
├── analyzer.py   # DataFrame profiling (DataAnalyzer)
├── cleaner.py    # Deterministic cleaning operations (DataCleaner)
├── prompts.py    # LangChain prompt templates
└── agent.py      # LangChain + Gemini orchestration (DataCleaningAgent)
app.py            # Streamlit web UI
tests/
├── test_analyzer.py
└── test_cleaner.py
```

---

## Quick start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Gemini API key

Create a `.env` file in the project root:

```
GOOGLE_API_KEY=your_key_here
```

Or paste the key directly in the sidebar when the app is running.

> Get a free key at <https://aistudio.google.com/app/apikey>

### 3. Run the Streamlit app

```bash
streamlit run app.py
```

Open <http://localhost:8501> in your browser, upload a CSV, and start cleaning.

---

## Programmatic usage

```python
import pandas as pd
from src.data_cleaner import DataCleaningAgent

df = pd.read_csv("my_data.csv")
agent = DataCleaningAgent(api_key="YOUR_KEY")

# Get LLM-powered recommendations
result = agent.analyze(df)
print(result["recommendations"])

# Auto-clean the dataframe
cleaned_df, log = agent.auto_clean(df, clip_outliers=True)
print(log)
```

---

## Running tests

```bash
pip install pytest
pytest tests/ -v
```