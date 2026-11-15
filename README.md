# Snowflake Enterprise Data Platform

A portfolio-scale data engineering project that ingests CSV files, SQL Server order data, and REST API records into Snowflake; transforms warehouse data with dbt; and orchestrates the workflow with Apache Airflow.

 > **Execution environment:** This repository is developed on macOS. The Airflow DAG uses POSIX shell commands and paths. SQL Server connectivity on macOS requires a compatible Microsoft ODBC driver and SQL Server authentication; Windows Integrated Authentication is not assumed. This is a local portfolio implementation, not a cloud-hosted production deployment.

## Architecture

```text
CSV files --------------------\
SQL Server -- watermark -------> Python ingestion -> Snowflake stages / Bronze
REST API ---------------------/                         |
                                                        v
                                             dbt Silver -> Gold
                                                        |
                                                        v
                                               Power BI analytics

Apache Airflow orchestrates ingestion, dbt runs, and dbt tests.
```

## Technology stack

- Python, Pandas, Requests
- Microsoft SQL Server and Snowflake
- dbt-snowflake and SQL
- Apache Airflow
- Power BI
- pytest for Python unit tests

## Data sources and pipeline

1. **CSV ingestion:** uploads source CSV files to the configured Snowflake stage.
2. **SQL Server incremental extraction:** reads the last persisted watermark from Snowflake and extracts rows whose `UPDATED_AT` value is newer.
3. **REST API ingestion:** fetches user records from JSONPlaceholder, normalizes the JSON with Pandas, and writes a CSV extract.
4. **Snowflake loading:** uploads generated extracts to their corresponding internal stages.
5. **dbt transformations:** builds staging models and analytics marts.
6. **Data quality:** dbt schema tests check key uniqueness, non-null values, and fact-to-dimension relationships.
7. **Orchestration:** Airflow coordinates the ingestion tasks, dbt run, and dbt tests.

## Warehouse modelling

The project uses a Bronze / Silver / Gold pattern:

- **Bronze:** raw staged source data.
- **Silver:** standardized staging models, including latest-record selection for orders.
- **Gold:** analytics-ready fact and dimension models.

The dbt project is under `de_dbt/`. Model-level tests are defined alongside the staging and mart models.

## Repository layout

```text
.
├── airflow/
│   └── dags/
├── data/
│   └── source/
├── de_dbt/
│   ├── macros/
│   └── models/
│       ├── staging/
│       └── marts/
├── ingestion/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.10+
- Access to a SQL Server instance and the Microsoft ODBC Driver for SQL Server
- A Snowflake account with the database, schemas, stages, and watermark control table used by the scripts
- dbt-snowflake configured with a local dbt profile
- For Airflow orchestration: a compatible Airflow installation with the DAG's required providers installed

Airflow is intentionally managed separately from the project Python dependencies because Airflow installations should use the constraints file for the selected Airflow and Python versions. Do not install Airflow by adding it to the application requirements file.

## Local setup

Create and activate a virtual environment, then install project dependencies:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\\Scripts\\Activate.ps1

python -m pip install --upgrade pip
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and provide your own connection values. Never commit `.env`, passwords, tokens, or private dbt profiles.

On macOS, install the Microsoft ODBC Driver for SQL Server and configure SQL Server authentication using `SQLSERVER_USER` and `SQLSERVER_PASSWORD`. The current Windows `Trusted_Connection` approach is not portable to macOS. Configure the Snowflake account, user, password, warehouse, database, and schema in the environment.

## Running ingestion scripts

Run scripts from the repository root:

```bash
python ingestion/api_to_csv.py
python ingestion/sqlserver_incremental.py
python ingestion/csv_to_snowflake.py
python ingestion/upload_sqlserver_orders.py
python ingestion/upload_api_to_snowflake.py
```

The SQL Server and Snowflake scripts require valid external connections and the corresponding source objects/stages to exist. They cannot be fully exercised without those services and credentials. The SQL Server connection settings must be compatible with macOS and the installed ODBC driver.

## Running dbt

Configure a local dbt profile for the `de_dbt` project using your Snowflake credentials. Keep the profile outside version control.

```bash
cd de_dbt
dbt debug
dbt run
dbt test
```

## Airflow orchestration (macOS / Linux)

The DAG is `airflow/dags/snowflake_enterprise_pipeline.py`. It resolves the repository root relative to the DAG file by default, uses `.venv/bin/python` and `.venv/bin/dbt`, and executes commands through the Airflow worker's POSIX shell.

If Airflow runs in a separate container or environment, set `DATA_ENGINEERING_PROJECT_DIR` to the repository path mounted and visible to the worker. Optionally override `PROJECT_PYTHON_EXECUTABLE` and `PROJECT_DBT_EXECUTABLE` if your executables are installed elsewhere. Ensure the Airflow scheduler and workers can access the same project files and environment variables. The DAG is manually triggered (`schedule=None`). Install Airflow and its required providers separately using the constraints file for your Airflow/Python version; do not install Airflow as an unconstrained application dependency.

## Tests

Run the local unit tests:

```bash
python -m pytest -q
```

The unit tests cover the API ingestion helpers and incremental extraction query parameterization. They do not require live SQL Server or Snowflake credentials. dbt tests require a configured Snowflake profile and warehouse.

## Security and operational boundaries

- Keep credentials in environment variables or a local `.env` file; do not commit secrets.
- macOS SQL Server access requires the configured ODBC driver and SQL Server credentials; Windows Integrated Authentication is not assumed.
- The current project is a local portfolio implementation. Production deployment, managed secrets, alerting, cloud-hosted Airflow, and automated infrastructure provisioning are not claimed.
- The pipeline uses batch and watermark-based incremental extraction; it is not a real-time streaming platform.

## Future improvements

- Persist and advance ingestion watermarks transactionally after successful target loads.
- Add integration tests against disposable/test database schemas.
- Add Airflow failure alerting and execution monitoring.
- Add CI checks for Python tests and dbt project parsing/compilation.
- Move orchestration and secrets to managed production infrastructure when deploying beyond local development.
