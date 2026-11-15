import os
import shlex
from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


# Airflow runs in WSL2 and delegates Windows-authenticated SQL Server access
# to the Windows Python environment through PowerShell.
PROJECT = os.getenv(
    "DATA_ENGINEERING_PROJECT_WINDOWS_PATH",
    r"D:\DataEnggProject\snowflake-enterprise-data-platform",
)
POWERSHELL = os.getenv("POWERSHELL_EXECUTABLE", "powershell.exe")
PYTHON_EXE = os.getenv("WINDOWS_PYTHON_EXECUTABLE", ".venv\\Scripts\\python.exe")
DBT_EXE = os.getenv("WINDOWS_DBT_EXECUTABLE", ".venv\\Scripts\\dbt.exe")


def ps_quote(value: str) -> str:
    """Return a PowerShell single-quoted string literal."""
    return "'" + value.replace("'", "''") + "'"


def powershell_task(script: str) -> str:
    """Build a shell-quoted WSL -> PowerShell command."""
    return (
        f"{shlex.quote(POWERSHELL)} -NoProfile -NonInteractive "
        f"-Command {shlex.quote(script)}"
    )


def python_task(script_path: str) -> str:
    executable = f"{PROJECT}\\{PYTHON_EXE}"
    target = f"{PROJECT}\\{script_path.replace('/', chr(92))}"
    script = (
        f"Set-Location -LiteralPath {ps_quote(PROJECT)}; "
        f"& {ps_quote(executable)} {ps_quote(target)}"
    )
    return powershell_task(script)


def dbt_task(arguments: str) -> str:
    executable = f"{PROJECT}\\{DBT_EXE}"
    working_directory = f"{PROJECT}\\de_dbt"
    script = (
        f"Set-Location -LiteralPath {ps_quote(working_directory)}; "
        f"& {ps_quote(executable)} {arguments}"
    )
    return powershell_task(script)


default_args = {
    "owner": "data-engineering",
    "retries": 1,
}

with DAG(
    dag_id="snowflake_enterprise_data_pipeline",
    description="Multi-source ingestion and dbt transformation pipeline",
    default_args=default_args,
    start_date=datetime(2026, 9, 1),
    schedule=None,
    catchup=False,
    tags=["snowflake", "dbt", "data-engineering"],
) as dag:
    csv_ingestion = BashOperator(
        task_id="csv_ingestion",
        bash_command=python_task("ingestion/csv_to_snowflake.py"),
    )

    sqlserver_incremental = BashOperator(
        task_id="sqlserver_incremental_extraction",
        bash_command=python_task("ingestion/sqlserver_incremental.py"),
    )

    sqlserver_stage_upload = BashOperator(
        task_id="sqlserver_stage_upload",
        bash_command=python_task("ingestion/upload_sqlserver_orders.py"),
    )

    api_extraction = BashOperator(
        task_id="api_extraction",
        bash_command=python_task("ingestion/api_to_csv.py"),
    )

    api_stage_upload = BashOperator(
        task_id="api_stage_upload",
        bash_command=python_task("ingestion/upload_api_to_snowflake.py"),
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=dbt_task("run"),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=dbt_task("test"),
    )

    csv_ingestion >> dbt_run
    sqlserver_incremental >> sqlserver_stage_upload >> dbt_run
    api_extraction >> api_stage_upload >> dbt_run
    dbt_run >> dbt_test
