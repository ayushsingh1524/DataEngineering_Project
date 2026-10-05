from datetime import datetime

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator


PROJECT = r"D:\DataEnggProject\snowflake-enterprise-data-platform"

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
        bash_command=f"""
        powershell.exe -NoProfile -Command "
        Set-Location '{PROJECT}';
        & '.\\.venv\\Scripts\\python.exe' 'ingestion\\csv_to_snowflake.py'
        "
        """,
    )

    sqlserver_incremental = BashOperator(
        task_id="sqlserver_incremental_extraction",
        bash_command=f"""
        powershell.exe -NoProfile -Command "
        Set-Location '{PROJECT}';
        & '.\\.venv\\Scripts\\python.exe' 'ingestion\\sqlserver_incremental.py'
        "
        """,
    )

    sqlserver_stage_upload = BashOperator(
        task_id="sqlserver_stage_upload",
        bash_command=f"""
        powershell.exe -NoProfile -Command "
        Set-Location '{PROJECT}';
        & '.\\.venv\\Scripts\\python.exe' 'ingestion\\upload_sqlserver_orders.py'
        "
        """,
    )

    api_extraction = BashOperator(
        task_id="api_extraction",
        bash_command=f"""
        powershell.exe -NoProfile -Command "
        Set-Location '{PROJECT}';
        & '.\\.venv\\Scripts\\python.exe' 'ingestion\\api_to_csv.py'
        "
        """,
    )

    api_stage_upload = BashOperator(
        task_id="api_stage_upload",
        bash_command=f"""
        powershell.exe -NoProfile -Command "
        Set-Location '{PROJECT}';
        & '.\\.venv\\Scripts\\python.exe' 'ingestion\\upload_api_to_snowflake.py'
        "
        """,
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"""
        powershell.exe -NoProfile -Command "
        Set-Location '{PROJECT}\\de_dbt';
        & '..\\.venv\\Scripts\\dbt.exe' run
        "
        """,
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"""
        powershell.exe -NoProfile -Command "
        Set-Location '{PROJECT}\\de_dbt';
        & '..\\.venv\\Scripts\\dbt.exe' test
        "
        """,
    )

    csv_ingestion >> dbt_run

    sqlserver_incremental >> sqlserver_stage_upload >> dbt_run

    api_extraction >> api_stage_upload >> dbt_run

    dbt_run >> dbt_test
