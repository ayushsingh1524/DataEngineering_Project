import os

import pyodbc
from dotenv import load_dotenv


load_dotenv()


def get_sqlserver_connection():
    """Create and return a SQL Server connection using Windows Authentication."""

    server = os.getenv("SQLSERVER_HOST")
    database = os.getenv("SQLSERVER_DATABASE")

    connection_string = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={server};"
        f"DATABASE={database};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string)


if __name__ == "__main__":

    connection = None

    try:
        connection = get_sqlserver_connection()

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                DB_NAME(),
                @@SERVERNAME
        """)

        row = cursor.fetchone()

        print("SQL Server connection successful!")
        print(f"Server   : {row[1]}")
        print(f"Database : {row[0]}")

    except Exception as error:
        print(f"SQL Server connection failed: {error}")

    finally:
        if connection:
            connection.close()
            print("Connection closed.")