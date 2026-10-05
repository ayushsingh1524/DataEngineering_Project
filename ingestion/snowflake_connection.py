import os

import snowflake.connector
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


def get_snowflake_connection():
    """Create and return a Snowflake connection."""
    connection = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    return connection


if __name__ == "__main__":
    connection = None

    try:
        connection = get_snowflake_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT CURRENT_USER(), CURRENT_DATABASE(), CURRENT_SCHEMA()")

        result = cursor.fetchone()

        print("Snowflake connection successful!")
        print(f"User     : {result[0]}")
        print(f"Database : {result[1]}")
        print(f"Schema   : {result[2]}")

    except Exception as error:
        print(f"Snowflake connection failed: {error}")

    finally:
        if connection:
            connection.close()
            print("Connection closed.")