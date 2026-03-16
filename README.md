# Data Cleaner

A practical data cleaning workspace that supports three input channels:

- File upload (CSV / Excel)
- SQL Server table (Trusted Connection)
- External API endpoint

The project includes:

- FastAPI backend for cleaning services
- Streamlit frontend with source switcher in sidebar (`FILE`, `DB`, `API`)
- CLI runner for quick local cleaning tasks

## Project Structure

```text
app/
  app.py                 # Streamlit UI
scripts/
  backend.py             # FastAPI endpoints
  data_ingestion.py      # File/API/SQL Server ingestion
  data_cleaning.py       # Cleaning logic
  agent.py               # Optional AI summary
  main.py                # CLI entrypoint
data/
requirements.txt
README.md
```

## Requirements

- Python 3.10+
- SQL Server ODBC driver installed locally (for DB mode):
  - ODBC Driver 17 for SQL Server (or compatible)
- Windows trusted connection access to your SQL Server instance

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional (AI summary): set your Gemini key in `.env`:

```env
GEMINI_API_KEY=your_key_here
```

## Run Backend (FastAPI)

```bash
uvicorn scripts.backend:app --reload
```

Backend endpoints:

- `POST /clean-data` (multipart file)
- `POST /clean-api` (JSON body)
- `POST /clean-db` (JSON body with DB target string)

## Run Streamlit App

```bash
streamlit run app/app.py
```

## UI Preview

(app/UI.png)

The sidebar lets you choose the cleaning source:

- `FILE`
- `DB`
- `API`

## DB Target String (Trusted Connection)

Use this exact key-value format in DB mode:

```text
server=MY_SERVER;database=MY_DB;table=MY_TABLE;schema=dbo
```

- `schema` is optional (defaults to `dbo`)
- trusted auth is used automatically (`Trusted_Connection=yes`)

## CLI Usage (`scripts/main.py`)

### File

```bash
python scripts/main.py --source file --path data/data.csv
```

### API

```bash
python scripts/main.py --source api --api-url https://jsonplaceholder.typicode.com/posts
```

### SQL Server

```bash
python scripts/main.py --source db --db-target "server=MY_SERVER;database=MY_DB;table=MY_TABLE;schema=dbo"
```

### Optional AI Summary

Add `--with-ai` to any mode.

```bash
python scripts/main.py --source file --path data/data.csv --with-ai
```

## Notes

- Response rows are JSON-safe (`NaN` values are converted to `null`).
- Current deterministic cleaning step removes duplicate rows.
- AI output is returned as `ai_summary` and does not block deterministic cleaning.

## Next Improvements

- Add column-level cleaning strategy config (missing values/outliers/type coercion).
- Add automated tests for `clean-data`, `clean-api`, and `clean-db` endpoints.
- Add write-back option to SQL Server for cleaned tables.
