import pandas as pd
import requests
import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")


class DataIngestion:
    @staticmethod
    def _resolve_path(filename):
        if os.path.isabs(filename):
            return filename
        return os.path.join(DATA_DIR, filename)

    @staticmethod
    def _parse_db_target(target):
        """
        Parse target string format:
        server=MY_SERVER;database=MY_DB;table=MY_TABLE
        Optional schema key defaults to dbo.
        """
        parsed = {}

        for part in target.split(";"):
            part = part.strip()
            if not part:
                continue
            if "=" not in part:
                raise ValueError(
                    "Invalid DB target format. Use server=...;database=...;table=..."
                )
            key, value = part.split("=", 1)
            parsed[key.strip().lower()] = value.strip()

        required = ["server", "database", "table"]
        missing = [key for key in required if not parsed.get(key)]
        if missing:
            raise ValueError(f"Missing DB target fields: {', '.join(missing)}")

        parsed.setdefault("schema", "dbo")
        return parsed

    @staticmethod
    def _build_trusted_sqlserver_engine(server, database):
        odbc = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
        )
        connection_url = f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc)}"
        return create_engine(connection_url)
    
    def load_csv(self, filename):
        file_path = self._resolve_path(filename)
        try:
            df = pd.read_csv(file_path)
            print("CSV loaded successfully!")
            return df
        except Exception as e:
            print(f"Error Loading CSV : {e}")
            return None
    
    def load_excel(self, filename, sheetname=0):
        file_path = self._resolve_path(filename)
        try:
            df = pd.read_excel(file_path, sheet_name=sheetname)
            print("Excel loaded successfully!")
            return df
        except Exception as e:
            print(f"Error Loading Excel : {e}")
            return None

    def fetch_api(self, api_url):
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                print("Data Fetched Successfully!")
                return df
            else:
                print(f"Request Failed : {response.status_code}")
                return None
        except Exception as e:
            print(f"Error : {e}")
            return None

    def load_sql_server_trusted(self, target):
        """
        Read a table from SQL Server via trusted connection.

        target format:
        server=MY_SERVER;database=MY_DB;table=MY_TABLE
        optional: ;schema=MY_SCHEMA
        """
        try:
            parsed = self._parse_db_target(target)
            engine = self._build_trusted_sqlserver_engine(
                server=parsed["server"],
                database=parsed["database"],
            )
            table_name = f"[{parsed['schema']}].[{parsed['table']}]"
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, engine)
            print("SQL Server table loaded successfully!")
            return df
        except Exception as e:
            print(f"Error loading SQL Server data: {e}")
            return None