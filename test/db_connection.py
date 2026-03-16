import os
import pyodbc
from dotenv import load_dotenv


load_dotenv()

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
#genai.configure(api_key=GEMINI_API_KEY)

# Use Gemini Flash model
#model = genai.GenerativeModel("gemini-1.5-flash")

# SQL Server connection using Trusted Connection
def connect_sql():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={SQL_SERVER};"
        f"DATABASE={SQL_DATABASE};"
        "Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

conn = connect_sql()
cursor = conn.cursor()

query = """
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE='BASE TABLE'
"""

cursor.execute(query)

print("Tables in database:\n")

for row in cursor.fetchall():
    print(row.TABLE_NAME)

cursor.close()
conn.close()