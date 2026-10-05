from pathlib import Path
import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FILE_PATH = PROJECT_ROOT / "data" / "source" / "api" / "api_users.csv"

conn = snowflake.connector.connect(
    account=os.getenv("SNOWFLAKE_ACCOUNT"),
    user=os.getenv("SNOWFLAKE_USER"),
    password=os.getenv("SNOWFLAKE_PASSWORD"),
    warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
    database="DE_PROJECT_DB",
    schema="STAGE"
)

cur = conn.cursor()

try:
    path = str(FILE_PATH).replace("\\", "/")

    sql = f"""
        PUT 'file://{path}'
        @DE_PROJECT_DB.STAGE.API_STAGE
        AUTO_COMPRESS=TRUE
        OVERWRITE=TRUE
    """

    cur.execute(sql)

    print("API file uploaded successfully!")

finally:
    cur.close()
    conn.close()