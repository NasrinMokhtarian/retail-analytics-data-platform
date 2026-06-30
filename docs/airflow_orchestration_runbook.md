# Airflow Orchestration Runbook

## Purpose

This runbook explains how Apache Airflow is used in the Retail Analytics Data Platform.

Airflow is used as the local orchestration layer. It coordinates already-tested Python CLI commands, PostgreSQL validation steps, report gates, and dbt builds.

Airflow does not contain the business logic of the platform. The business logic remains in:

* Python modules and CLI commands
* dbt models
* validation modules
* report gates
* PostgreSQL audit tables

This keeps the platform modular, testable, and easier to extend later to cloud infrastructure.

## Current Airflow Scope

The project currently includes two local Airflow DAGs:

| DAG                         | Purpose                                                  |
| --------------------------- | -------------------------------------------------------- |
| `retail_local_full_refresh` | Refreshes the full local analytics platform              |
| `br_holidays_api_refresh`   | Refreshes only the public holidays API enrichment source |

Both DAGs are manually triggered for now.

Scheduling can be added later after the local orchestration layer is stable.

## Airflow Services

Airflow runs locally through Docker Compose.

Main services:

| Service             | Purpose                                |
| ------------------- | -------------------------------------- |
| `postgres`          | Retail analytics PostgreSQL warehouse  |
| `pgadmin`           | PostgreSQL UI                          |
| `airflow-postgres`  | Airflow metadata database              |
| `airflow-webserver` | Airflow web UI                         |
| `airflow-scheduler` | Airflow scheduler and task coordinator |

The Airflow metadata database is separate from the retail analytics PostgreSQL warehouse.

## Starting Airflow

From the project root:

```powershell
cd G:\retail-analytics-data-platform
docker compose up -d postgres pgadmin airflow-postgres airflow-webserver airflow-scheduler
```

Check containers:

```powershell
docker compose ps
```

Open Airflow:

```text
http://localhost:8081
```

Login:

```text
username: airflow
password: airflow
```

## DAG 1: Full Local Platform Refresh

DAG:

```text
retail_local_full_refresh
```

Purpose:

Refresh the full local platform from cleaned outputs into PostgreSQL and dbt.

Task flow:

```text
create PostgreSQL schemas
→ create load audit table
→ start pipeline audit
→ validate cleaned-file mappings
→ load Olist, supplier, and public holidays raw tables
→ validate PostgreSQL loads
→ run PostgreSQL validation gate
→ run dbt build
→ mark pipeline run as SUCCESS or FAILED
```

Default parameters:

```json
{
  "olist_run_date": "2026-05-26",
  "supplier_run_date": "2026-06-01",
  "br_holidays_run_date": "2026-06-16",
  "validation_run_date": "2026-06-16",
  "log_level": "INFO"
}
```

Use this DAG when:

* rebuilding the whole local platform
* recovering after PostgreSQL volume deletion
* refreshing all raw tables together
* checking the full local pipeline before dashboard refresh
* validating the whole project before a commit or demo

## DAG 2: public Holidays API Refresh

DAG:

```text
br_holidays_api_refresh
```

Purpose:

Refresh only the public public-holidays API source and rebuild holiday-aware dbt models.

Task flow:

```text
create PostgreSQL schemas
→ create load audit table
→ start pipeline audit
→ extract public holidays API data
→ clean public holidays data
→ run quality checks
→ run quality gate
→ run cleaned output validation
→ run validation gate
→ load raw.br_holidays
→ build holiday-aware dbt models
→ mark pipeline run as SUCCESS or FAILED
```

Default parameters:

```json
{
  "run_date": "2026-06-16",
  "log_level": "INFO"
}
```

Use this DAG when:

* only the external API source needs refresh
* testing the API enrichment workflow
* updating the Holiday Impact dashboard page
* validating the holiday-aware dbt mart

## Why Airflow Does Not Contain Business Logic

The DAG files only coordinate existing commands.

This is intentional.

Good Airflow responsibility:

```text
run this task
then run that task
retry if needed
show logs
show dependencies
record success or failure
```

Avoided Airflow responsibility:

```text
large pandas transformations inside DAG files
business rules inside DAG files
SQL marts inside DAG files
data quality logic hidden inside DAG files
```

Keeping logic outside Airflow makes the project:

* easier to test
* easier to debug
* easier to run without Airflow
* easier to move later to AWS or another orchestrator
* easier to explain in interviews

## Audit Tables

The orchestration layer writes to two audit levels.

### Pipeline-level audit

Table:

```text
audit.pipeline_runs
```

Check latest pipeline runs:

```sql
SELECT
    pipeline_run_id,
    pipeline_name,
    run_date,
    selected_sources,
    started_at,
    finished_at,
    status,
    error_message
FROM audit.pipeline_runs
ORDER BY started_at DESC
LIMIT 10;
```

Expected pipeline names:

```text
retail_local_full_refresh_airflow
br_holidays_api_refresh_airflow
```

### Table-level load audit

Table:

```text
audit.load_audit
```

Check latest table loads:

```sql
SELECT
    source_name,
    target_schema,
    target_table,
    source_row_count,
    loaded_row_count,
    status,
    load_started_at,
    error_message
FROM audit.load_audit
ORDER BY load_started_at DESC
LIMIT 20;
```

## Verifying dbt Results

After a successful DAG run:

```sql
SELECT
    (SELECT COUNT(*) FROM dbt_mart.fct_orders) AS fct_orders_count,
    (SELECT COUNT(*) FROM dbt_mart.fct_orders_holiday_context) AS holiday_context_count,
    (SELECT COUNT(*) FROM dbt_mart.dim_br_holidays) AS holiday_count;
```

Expected:

```text
fct_orders_count = holiday_context_count
holiday_count = 42
```

## Power BI Refresh

After a successful Airflow run, refresh the Power BI file manually:

```text
powerbi/retail_analytics_dashboard.pbix
```

In Power BI Desktop:

```text
Home → Refresh
```

The dashboard consumes the dbt mart layer.

## Troubleshooting

### DAG does not appear

Restart scheduler and webserver:

```powershell
docker compose restart airflow-scheduler airflow-webserver
```

Check scheduler logs:

```powershell
docker compose logs airflow-scheduler --tail=200
```

### Task fails

In Airflow UI:

```text
DAG → failed task → Logs
```

Read the task log first. Most failures will come from:

* missing cleaned files
* wrong run date
* PostgreSQL connection issue
* failed validation gate
* dbt model/test failure

### Airflow cannot connect to PostgreSQL

Inside Docker, Airflow connects to PostgreSQL using:

```text
host = postgres
port = 5432
```

Not:

```text
localhost:5433
```

`localhost:5433` is for tools running on the Windows host, such as pgAdmin or local PowerShell commands.

### Airflow metadata database

Airflow uses a separate metadata database:

```text
airflow-postgres
```

Do not mix Airflow metadata tables with the retail analytics warehouse tables.

## Current Orchestration Status

Implemented:

* local Airflow Docker services
* full-platform refresh DAG
* public holidays API refresh DAG
* pipeline audit integration
* report gate integration
* dbt build integration

Not yet implemented:

* scheduled DAG runs
* alerting
* Airflow connections UI
* AWS orchestration
* Terraform integration

These are intentionally deferred until the local orchestration layer is stable.
