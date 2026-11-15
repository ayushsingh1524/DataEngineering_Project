from pathlib import Path
from typing import Any

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FOLDER = PROJECT_ROOT / "data" / "source" / "api"
API_URL = "https://jsonplaceholder.typicode.com/users"
REQUEST_TIMEOUT_SECONDS = 30


def fetch_users(url: str = API_URL, timeout: int = REQUEST_TIMEOUT_SECONDS) -> list[dict[str, Any]]:
    """Fetch users from the source API and fail clearly on HTTP errors."""
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    users = response.json()
    if not isinstance(users, list):
        raise ValueError("Expected the users API to return a JSON array.")
    return users


def save_users(users: list[dict[str, Any]], output_file: Path) -> int:
    """Normalize API records and save them as a CSV file."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.json_normalize(users)
    frame.to_csv(output_file, index=False)
    return len(frame)


def main() -> None:
    users = fetch_users()
    output_file = OUTPUT_FOLDER / "api_users.csv"
    row_count = save_users(users, output_file)
    print(f"Rows extracted: {row_count}")
    print(f"File created: {output_file}")


if __name__ == "__main__":
    main()
