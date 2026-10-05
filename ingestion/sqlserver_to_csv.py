from pathlib import Path

import pandas as pd

from sqlserver_connection import get_sqlserver_connection


# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Destination for extracted SQL Server files
OUTPUT_FOLDER = PROJECT_ROOT / "data" / "source" / "sqlserver"

# Create folder if it doesn't exist
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)


TABLES = {
    "orders": "SELECT * FROM OPERATIONS.ORDERS",
    "order_items": "SELECT * FROM OPERATIONS.ORDER_ITEMS",
}


def extract_sqlserver_tables():
    connection = None

    try:
        connection = get_sqlserver_connection()

        for table_name, query in TABLES.items():

            print(f"\nExtracting: {table_name}")

            df = pd.read_sql(query, connection)

            output_file = OUTPUT_FOLDER / f"{table_name}.csv"

            df.to_csv(
                output_file,
                index=False
            )

            print(f"Rows extracted : {len(df)}")
            print(f"File created   : {output_file}")

        print("\nSQL Server extraction completed successfully.")

    except Exception as error:
        print(f"\nSQL Server extraction failed: {error}")
        raise

    finally:
        if connection:
            connection.close()
            print("SQL Server connection closed.")


if __name__ == "__main__":
    extract_sqlserver_tables()