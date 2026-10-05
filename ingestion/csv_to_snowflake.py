from pathlib import Path
import os

import snowflake.connector
from dotenv import load_dotenv


load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SOURCE_FOLDERS = [
    PROJECT_ROOT / "data" / "source" / "csv",
    PROJECT_ROOT / "data" / "source" / "sqlserver",
]


def get_snowflake_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )


def upload_files():
    connection = None
    cursor = None

    try:
        connection = get_snowflake_connection()
        cursor = connection.cursor()

        for folder in SOURCE_FOLDERS:

            if not folder.exists():
                print(f"Folder not found: {folder}")
                continue

            print(f"\nProcessing folder: {folder}")

            for csv_file in folder.glob("*.csv"):

                file_path = str(csv_file).replace("\\", "/")

                put_command = f"""
                    PUT 'file://{file_path}'
                    @DE_PROJECT_DB.STAGE.BRONZE_STAGE
                    AUTO_COMPRESS=TRUE
                    OVERWRITE=TRUE
                """

                print(f"Uploading: {csv_file.name}")

                cursor.execute(put_command)

                print(f"Uploaded: {csv_file.name}")

        print("\nAll files uploaded successfully.")

    except Exception as error:
        print(f"\nUpload failed: {error}")
        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


if __name__ == "__main__":
    upload_files()