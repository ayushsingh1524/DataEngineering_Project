import os
import shlex
import sys
from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator


# The DAG is designed for a macOS/Linux local checkout. If Airflow runs in a
# separate environment/container, set DATA_ENGINEERING_PROJECT_DIR to the
# repository path visible to the Airflow worker.
PROJECT_DIR = Path(
    os.getenv(
        "DATA_ENGINEERING_PROJECT_DIR",
        str(Path(__file__).resolve().parents[2]),
    )
).expanduser()

VENV_DIR = PROJECT_DIR / ".venv"
PYTHON_EXE = os.getenv(
    "PROJECT_PYTHON_EXECUTABLE",
    str(VENV_DIR / "bin" / "python"),
)
DBT_EXE = os.getenv(
    "PROJECT_DBT_EXECUTABLE",
    str(VENV_DIR / "bin" / "dbt"),
)


def shell_command(executable: str, *arguments: str, cwd: Path = PROJECT_DIR) -> str:
    """Build a safely quoted command for the Airflow worker's POSIX shell."""
    parts = ["cd", shlex.quote(str(cwd)), "&&", shlex.quote(executable)]
    parts.extend(shlex.quote(argument) for argument in arguments)
    return " ".join(parts)


def python_task(script_path: str) -> str:
    return shell_command(PYTHON_EXE, str(PROJECT_DIR / script_path))


def dbt_task(*arguments: str) -> str:
    return shell_command(DBT_EXE, *arguments, cwd=PROJECT_DIR / "de_dbt")


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
