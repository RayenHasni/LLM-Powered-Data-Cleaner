import sys
import os
import pandas as pd
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import aiohttp
import uvicorn

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from scripts.agent import Ai_agent
from scripts.data_cleaning import DataCleaning
from scripts.data_ingestion import DataIngestion

app = FastAPI()

agent = Ai_agent()
cleaner = DataCleaning()
ingestion = DataIngestion()


def dataframe_to_records(df: pd.DataFrame):
    json_safe_df = df.astype(object).where(pd.notna(df), None)
    return json_safe_df.to_dict(orient="records")


def build_clean_response(df: pd.DataFrame):
    df_cleaned = cleaner.clean_data(df)
    ai_summary = None

    try:
        ai_summary = agent.process_data(df_cleaned)
    except Exception as ai_error:
        ai_summary = f"AI cleaning skipped: {ai_error}"

    return {
        "cleaned data": dataframe_to_records(df_cleaned),
        "ai_summary": ai_summary,
    }

#--------------------- CSV / Excel Cleaning Endpoint ------------------

@app.post("/clean-data")
async def clean_data(file : UploadFile = File(...)):
    """Receive File from UI"""
    try:
        content = await file.read()
        file_extension = file.filename.split(".")[-1]

        if file_extension == "csv":
            df = pd.read_csv(io.StringIO(content.decode("latin-1")))
        elif file_extension == "xlsx":
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=500, detail="Unsupported file format. Please upload a CSV or Excel file")

        return build_clean_response(df)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#--------------------- API Cleaning Endpoint ------------------

class APIRequest(BaseModel):
    api_url: str

@app.post("/clean-api")
async def clean_api(api_request: APIRequest):
    """Fetch fata from API, clean it and return a JSON"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_request.api_url) as response:
                if response.status != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch data from API.")
                
                data = await response.json()
                df = pd.DataFrame(data)

                return build_clean_response(df)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing API data: {str(e)}")


#--------------------- DB Cleaning Endpoint ------------------

class DBRequest(BaseModel):
    db_target: str


@app.post("/clean-db")
async def clean_db(db_request: DBRequest):
    """
    Read from SQL Server using trusted connection target string and clean it.

    target format:
    server=MY_SERVER;database=MY_DB;table=MY_TABLE
    optional: ;schema=MY_SCHEMA
    """
    try:
        df = ingestion.load_sql_server_trusted(db_request.db_target)
        if df is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not load SQL Server data. "
                    "Check db_target format and SQL Server connectivity."
                ),
            )

        return build_clean_response(df)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing DB data: {str(e)}")
    

#--------------------- Run Server ------------------

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
