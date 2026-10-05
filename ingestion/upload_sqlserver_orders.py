from pathlib import Path
import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_FOLDER = (
    PROJECT_ROOT
    / "data"
    / "source"
    / "sqlserver_incremental"
)


def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database="DE_PROJECT_DB",
        schema="STAGE",
    )


def upload_files():
    connection = get_snowflake_connection()

    try:
        cursor = connection.cursor()

        files = list(SOURCE_FOLDER.glob("orders_incremental_*.csv"))

        if not files:
            print("No incremental SQL Server files found.")
            return

        for file in files:

            file_path = str(file).replace("\\", "/")

            sql = f"""
                PUT 'file://{file_path}'
                @DE_PROJECT_DB.STAGE.SQLSERVER_ORDERS_STAGE
                AUTO_COMPRESS=TRUE
                OVERWRITE=FALSE
            """

            print("Uploading:", file.name)

            cursor.execute(sql)

            print("Upload completed:", file.name)

    finally:
        connection.close()


if __name__ == "__main__":
    upload_files()