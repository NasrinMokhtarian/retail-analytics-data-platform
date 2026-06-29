# Local Workflow Runbook

## Purpose

This runbook explains how to run the local workflows for the Retail Analytics Data Platform.

The project currently supports two local task runners:

1. Full local platform refresh
2. Brazil holidays API source refresh

These runners make the project repeatable before adding Airflow orchestration.

## Workflow Overview

The platform currently includes three source areas:

| Source                   | Type                   | Purpose                                                    |
| ------------------------ | ---------------------- | ---------------------------------------------------------- |
| Olist e-commerce data    | CSV files              | Main retail/e-commerce transactional dataset               |
| Supplier product updates | Handmade business file | Simulates messy supplier/business data with quality issues |
| Brazil public holidays   | External API           | Enriches Brazilian order data with public-holiday context  |

The local platform flow is:

```text
source data
→ cleaning / validated outputs
→ PostgreSQL raw schema
→ dbt staging and mart models
→ Power BI dashboard
```

The hardening layer adds:

```text
task runner
→ quality gates
→ PostgreSQL load validation
→ report gates
→ pipeline audit
→ table-level load audit
```

## Runner 1: Full Local Platform Refresh

Script:

```text
scripts/run_local_full_refresh.ps1
```

Purpose:

Use this runner when rebuilding or refreshing the whole local analytics platform.

It covers:

* PostgreSQL schema creation
* audit table creation
* cleaned-file mapping validation
* Olist raw table loading
* supplier raw table loading
* Brazil holidays raw table loading
* PostgreSQL load validation
* PostgreSQL validation gate
* full dbt build
* pipeline-level audit tracking

Command:

```powershell
.\scripts\run_local_full_refresh.ps1 `
  -OlistRunDate 2026-05-26 `
  -SupplierRunDate 2026-06-01 `
  -BrHolidaysRunDate 2026-06-16
```

Optional parameters:

```powershell
-ValidationRunDate 2026-06-16
-LogLevel INFO
```

Expected result:

```text
raw tables loaded
PostgreSQL validation report generated
PostgreSQL validation gate passed
dbt build passed
audit.pipeline_runs status = SUCCESS
```

Use this runner when:

* PostgreSQL was recreated
* Docker volume was lost or reset
* raw tables need to be refreshed together
* dbt models need to be rebuilt against a clean raw layer
* validating the whole platform before documentation or dashboard refresh

## Runner 2: Brazil Holidays API Refresh

Script:

```text
scripts/run_br_holidays_pipeline.ps1
```

Purpose:

Use this runner when refreshing only the Brazil public-holidays API source.

It covers:

* API extraction
* raw JSON landing
* cleaning
* quality checks
* quality gate
* cleaned output validation
* validation gate
* PostgreSQL load into `raw.br_holidays`
* dbt build for holiday-aware models
* pipeline-level audit tracking

Command:

```powershell
.\scripts\run_br_holidays_pipeline.ps1 -RunDate 2026-06-16
```

Optional parameter:

```powershell
-LogLevel INFO
```

Expected result:

```text
Brazil holidays raw JSON refreshed
cleaned holiday CSV generated
quality gate passed
validation gate passed
raw.br_holidays loaded
holiday-aware dbt models built
audit.pipeline_runs status = SUCCESS
```

Use this runner when:

* only the API enrichment source changed
* the Brazil holidays source needs to be refreshed
* testing the source-specific pipeline
* updating the Holiday Impact dashboard page

## Audit Tables

The project uses two audit levels.

### Pipeline-level audit

Table:

```text
audit.pipeline_runs
```

Purpose:

Tracks one row per pipeline execution.

Example pipeline names:

```text
retail_local_full_refresh
br_holidays_local_pipeline
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

### Table-level load audit

Table:

```text
audit.load_audit
```

Purpose:

Tracks one row per raw-table load.

Check latest raw loads:

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

## Validation Reports

PostgreSQL validation reports are written to:

```text
reports/postgres_validation/run_date=<validation_run_date>/postgres_load_validation_report.csv
```

The full local refresh runner checks this report with the report gate.

If an error-level failure exists, the pipeline stops.

## Power BI Refresh After Successful Run

After a successful full refresh or source-specific refresh, open:

```text
powerbi/retail_analytics_dashboard.pbix
```

Then in Power BI Desktop:

```text
Home → Refresh
```

Use the local PostgreSQL connection:

```text
Server: localhost:5433
Database: retail_analytics
Mode: Import
```

## Which Runner Should I Use?

| Situation                                   | Recommended runner             |
| ------------------------------------------- | ------------------------------ |
| Rebuild whole local platform                | `run_local_full_refresh.ps1`   |
| Recover after Docker volume deletion        | `run_local_full_refresh.ps1`   |
| Refresh only Brazil holidays API source     | `run_br_holidays_pipeline.ps1` |
| Rebuild dbt models after raw tables changed | `run_local_full_refresh.ps1`   |
| Test API enrichment pipeline only           | `run_br_holidays_pipeline.ps1` |

## Important Docker Warning

Do not use this command unless you intentionally want to delete the PostgreSQL database volume:

```powershell
docker compose down -v
```

The `-v` flag deletes Docker volumes. For PostgreSQL, this removes the database state.

For normal stopping, use:

```powershell
docker compose down
```

or:

```powershell
docker compose stop
```

## Success Criteria

The local workflow layer is healthy when:

* `run_local_full_refresh.ps1` completes successfully
* `run_br_holidays_pipeline.ps1` completes successfully
* `audit.pipeline_runs` shows `SUCCESS`
* `audit.load_audit` shows successful raw-table loads
* PostgreSQL validation gate passes
* dbt build passes
* Power BI refresh works
