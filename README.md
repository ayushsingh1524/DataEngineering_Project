
# Snowflake Enterprise Data Platform

End-to-end data engineering project integrating CSV, SQL Server, and REST API sources into Snowflake, with dbt transformations, Power BI analytics, and Apache Airflow orchestration.

## Architecture

```text
CSV Files --------\
SQL Server --------> Python Ingestion -> Snowflake Stage -> Bronze -> Silver -> Gold -> Power BI
REST API ----------/                                  |          |
                                                     CDC        dbt
                                                  /Watermark   Tests

Apache Airflow orchestrates the ingestion and dbt workflow.
````

## Tech Stack

* Python 3.10
* SQL Server
* Snowflake
* dbt
* Power BI
* Apache Airflow
* WSL2
* Git / GitHub

## Data Sources

The platform integrates three heterogeneous sources:

* CSV files for customer, product, and supplier data
* SQL Server for transactional order data
* REST API for external user data

## Data Architecture

The Snowflake warehouse follows a layered architecture:

### Bronze

Raw ingested data is loaded into Snowflake with minimal transformation.

Example objects:

* CUSTOMERS
* ORDERS
* PRODUCTS
* SUPPLIERS
* API_USERS

### Silver

The Silver layer cleans and standardizes Bronze data using dbt.

Examples:

* `stg_customers`
* `stg_orders`
* `stg_products`
* `stg_api_users`

Transformations include:

* column standardization
* data type normalization
* customer name derivation
* data quality checks
* deduplication patterns

### Gold

The Gold layer provides analytics-ready business models.

Models include:

* `FACT_ORDERS`
* `DIM_CUSTOMERS`
* `DIM_PRODUCTS`
* `DIM_API_USERS`
* `CUSTOMER_ORDER_SUMMARY`

## Snowflake Layer Structure

## Incremental Data Loading

SQL Server incremental extraction uses a watermark based on `UPDATED_AT`.

The pipeline:

```text
Read last watermark
        |
        v
Query SQL Server for newer rows
        |
        v
Generate incremental CSV
        |
        v
Upload to Snowflake Stage
        |
        v
Process new data
```

Timestamp precision was preserved to avoid duplicate extraction caused by differences between SQL Server `datetime2` precision and Python timestamp handling.

Snowflake Streams were also used to demonstrate CDC behavior for inserts, updates, and deletes.

## dbt Transformations and Testing

dbt is used for both Silver and Gold transformations.

Data quality tests include:

* unique primary keys
* not-null checks
* relationship integrity between fact and dimension tables

All configured dbt tests completed successfully.

## Data Quality Validation

A reconciliation check identified an orphan order where the customer record had previously been removed during CDC testing.

The issue was traced across Bronze, Silver, and Gold layers, the missing customer record was restored, and revenue totals were reconciled successfully.

This demonstrated the importance of:

* referential integrity testing
* source-to-target reconciliation
* validating aggregate metrics across transformation layers

## Power BI Dashboard

A Sales Performance Dashboard was built on top of the Snowflake Gold layer.

Metrics include:

* Total Revenue
* Total Orders
* Average Order Value
* Revenue by Customer Segment
* Revenue by Country
* Orders by Status
* Revenue Trend
* Top Customers

Power BI measures were validated directly against Snowflake SQL results.

## Apache Airflow Orchestration

Apache Airflow orchestrates the ingestion and transformation workflow.

The DAG contains seven tasks:

```text
sqlserver_incremental_extraction
        |
sqlserver_stage_upload --------\
                                \
csv_ingestion ------------------> dbt_run -> dbt_test
                                /
api_extraction ----------------/
        |
api_stage_upload
```

Airflow runs inside WSL2 while invoking the existing Windows Python and dbt environment.

This design allows the local development environment to reuse Windows Authentication for SQL Server while still demonstrating workflow orchestration using Airflow.

## Project Structure

```text
snowflake-enterprise-data-platform/
├── airflow/
│   └── dags/
├── dashboards/
├── data/
│   └── source/
├── de_dbt/
│   ├── macros/
│   └── models/
│       ├── staging/
│       └── marts/
├── ingestion/
├── .env.example
├── .gitignore
└── README.md
```

## Environment Configuration

Create a `.env` file using `.env.example` as a template.

Example:

```env
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=DE_PROJECT_DB
```

Real credentials are excluded from source control.

## Running dbt

```powershell
cd de_dbt
dbt run
dbt test
```

## Running Airflow

The Airflow DAG is located at:

```text
airflow/dags/snowflake_enterprise_pipeline.py
```

In the local implementation, Airflow runs in WSL2 and invokes the Windows project environment through PowerShell.

## Key Engineering Concepts Demonstrated

* Multi-source data ingestion
* Batch and incremental loading
* Watermark-based change detection
* Snowflake internal stages
* Bronze / Silver / Gold architecture
* Snowflake Streams and CDC
* dbt transformations and tests
* Dimensional modeling
* Data reconciliation
* Power BI semantic modeling
* Airflow dependency orchestration
* Git-based project structure

## Production Considerations

The current implementation is designed as a local engineering project.

A production implementation would typically add:

* centralized secrets management
* Airflow Connections or environment-managed credentials
* production Airflow metadata database and executor
* automated scheduling
* alerting and monitoring
* CI/CD for dbt and DAG deployment
* role-based Snowflake access
* automated Snowflake ingestion and watermark updates

## Project Outcome

This project demonstrates an end-to-end data engineering workflow from heterogeneous operational sources through ingestion, transformation, testing, orchestration, and analytics.

The final architecture provides a centralized Snowflake data warehouse with governed transformation layers, validated business metrics, and automated pipeline execution.



