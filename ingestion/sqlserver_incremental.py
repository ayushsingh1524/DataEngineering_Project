from pathlib import Path
import os

import pandas as pd
import pyodbc
import snowflake.connector
from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FOLDER = PROJECT_ROOT / "data" / "source" / "sqlserver_incremental"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


INCREMENTAL_ORDERS_QUERY = """
    SELECT
        ORDER_ID,
        CUSTOMER_ID,
        ORDER_DATE,
        ORDER_STATUS,
        TOTAL_AMOUNT,
        CREATED_AT,
        UPDATED_AT
    FROM OPERATIONS.ORDERS
    WHERE UPDATED_AT > ?
    ORDER BY UPDATED_AT
"""


def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def build_sqlserver_connection_string() -> str:
    """Build an ODBC connection string for a SQL Server Docker container."""
    host = os.getenv("SQLSERVER_HOST", "localhost")
    port = os.getenv("SQLSERVER_PORT", "1433")
    database = os.getenv("SQLSERVER_DATABASE")
    username = os.getenv("SQLSERVER_USER")
    password = os.getenv("SQLSERVER_PASSWORD")
    driver = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 18 for SQL Server")

    missing = [
        name
        for name, value in {
            "SQLSERVER_DATABASE": database,
            "SQLSERVER_USER": username,
            "SQLSERVER_PASSWORD": password,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError("Set the following values in .env: " + ", ".join(missing))

    # ODBC brace-quoted values safely support semicolons and closing braces.
    def odbc_value(value: str) -> str:
        return "{" + value.replace("}", "}}") + "}"

    server = f"tcp:{host},{port}"
    return (
        f"DRIVER={odbc_value(driver)};"
        f"SERVER={odbc_value(server)};"
        f"DATABASE={odbc_value(database)};"
        f"UID={odbc_value(username)};"
        f"PWD={odbc_value(password)};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=15;"
    )


def get_sqlserver_connection():
    """Connect from the Mac host to the SQL Server container's published port."""
    return pyodbc.connect(build_sqlserver_connection_string())

def get_watermark():
    connection = get_snowflake_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT TO_VARCHAR(
                LAST_WATERMARK,
                'YYYY-MM-DD HH24:MI:SS.FF7'
            )
            FROM DE_PROJECT_DB.CONTROL.INGESTION_WATERMARK
            WHERE SOURCE_NAME = 'SQL_SERVER'
              AND TABLE_NAME = 'ORDERS'
        """)

        row = cursor.fetchone()

        if row is None:
            raise ValueError(
                "No watermark found for SQL_SERVER / ORDERS"
            )

        return row[0]

    finally:
        connection.close()


def extract_incremental_orders():
    watermark = get_watermark()

    print("Last watermark:", watermark)

    sqlserver_connection = get_sqlserver_connection()

    try:
        df = pd.read_sql(
            INCREMENTAL_ORDERS_QUERY,
            sqlserver_connection,
            params=[watermark],
        )

        print("Rows extracted:", len(df))

        if df.empty:
            print("No new or changed records found.")
            return

        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")

        output_file = (
            OUTPUT_FOLDER /
            f"orders_incremental_{timestamp}.csv"
        )

        df.to_csv(
            output_file,
            index=False
        )

        print("File created:", output_file)

    finally:
        sqlserver_connection.close()


if __name__ == "__main__":
    extract_incremental_orders()