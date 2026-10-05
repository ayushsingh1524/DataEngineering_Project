from pathlib import Path
import requests
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_FOLDER = PROJECT_ROOT / "data" / "source" / "api"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

URL = "https://jsonplaceholder.typicode.com/users"

response = requests.get(URL)
response.raise_for_status()

users = response.json()

df = pd.json_normalize(users)

output_file = OUTPUT_FOLDER / "api_users.csv"

df.to_csv(output_file, index=False)

print(f"Rows extracted : {len(df)}")
print(f"File created   : {output_file}")