# PostgreSQL Recovery Runbook

## Purpose

This runbook explains how to rebuild the local PostgreSQL warehouse for the Retail Analytics Data Platform after the Docker PostgreSQL volume is deleted, corrupted, or recreated.

The project is designed to be reproducible from source files, cleaned outputs, Python loading code, and dbt models. The PostgreSQL database should not be treated as the only source of truth.

## When to Use This Runbook

Use this runbook when:

* the Docker PostgreSQL volume was deleted
* PostgreSQL starts with an empty database
* raw, staging, mart, dbt, or audit schemas are missing
* dbt models fail because raw tables do not exist
* Power BI visuals fail after the database was recreated

## Recovery Overview

The recovery process has five stages:

1. Start Docker/PostgreSQL
2. Recreate required database schemas and audit table
3. Reload cleaned data into the raw schema
4. Rebuild dbt staging and mart models
5. Refresh the Power BI dashboard

## 1. Start Docker/PostgreSQL

From the project root:

```powershell
cd retail-analytics-data-platform
docker compose up -d
docker compose ps
```

Confirm the PostgreSQL container is running.

## 2. Recreate Schemas and Audit Table

Connect to the `retail_analytics` database in pgAdmin and run:

```sql
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS audit;

CREATE TABLE IF NOT EXISTS audit.load_audit (
    load_audit_id BIGSERIAL PRIMARY KEY,
    run_date DATE,
    source_name TEXT NOT NULL,
    source_file TEXT NOT NULL,
    target_schema TEXT NOT NULL,
    target_table TEXT NOT NULL,
    source_row_count INTEGER,
    loaded_row_count INTEGER,
    load_started_at TIMESTAMPTZ,
    load_finished_at TIMESTAMPTZ,
    status TEXT NOT NULL,
    error_message TEXT
);
```

## 3. Reload Cleaned Files into PostgreSQL

From the project root:

```powershell
cd retail-analytics-data-platform
```

Run the full raw-load process:

```powershell
python -m retail_analytics.cli.load_cleaned_to_postgres --olist-run-date <run-date> --supplier-run-date <run-date> --br-holidays-run-date <run-date> --only olist supplier br_holidays
```

This recreates the raw schema tables from cleaned CSV outputs.

Expected raw tables:

* `raw.olist_customers`
* `raw.olist_geolocation`
* `raw.olist_order_items`
* `raw.olist_order_payments`
* `raw.olist_order_reviews`
* `raw.olist_orders`
* `raw.olist_products`
* `raw.olist_sellers`
* `raw.product_category_translation`
* `raw.supplier_product_updates`
* `raw.br_holidays`

## 4. Verify Raw Tables

Run in pgAdmin:

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'raw'
ORDER BY table_name;
```

Check key row counts:

```sql
SELECT COUNT(*) AS row_count FROM raw.olist_orders;
SELECT COUNT(*) AS row_count FROM raw.supplier_product_updates;
SELECT COUNT(*) AS row_count FROM raw.br_holidays;
```

Expected key counts:

| Table                          | Expected row count |
| ------------------------------ | -----------------: |
| `raw.olist_orders`             |             99,441 |
| `raw.supplier_product_updates` |                 10 |
| `raw.br_holidays`              |                 42 |

Check latest audit records:

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

## 5. Rebuild dbt Models

From the dbt project directory:

```powershell
cd dbt_retail_analytics
```

Run:

```powershell
& ..\.venv\Scripts\dbt.exe parse
& ..\.venv\Scripts\dbt.exe build
```

This rebuilds the dbt staging and mart schemas.

Expected dbt schemas:

* `dbt_staging`
* `dbt_mart`

Important dbt models include:

* `dbt_staging.stg_orders`
* `dbt_staging.stg_br_holidays`
* `dbt_mart.fct_orders`
* `dbt_mart.dim_br_holidays`
* `dbt_mart.fct_orders_holiday_context`

## 6. Verify dbt Mart Layer

Run in pgAdmin:

```sql
SELECT COUNT(*) AS row_count FROM dbt_mart.fct_orders;
SELECT COUNT(*) AS row_count FROM dbt_mart.dim_br_holidays;
SELECT COUNT(*) AS row_count FROM dbt_mart.fct_orders_holiday_context;
```

Check that the order-level holiday mart has the same row count as `fct_orders`:

```sql
SELECT
    (SELECT COUNT(*) FROM dbt_mart.fct_orders) AS fct_orders_count,
    (SELECT COUNT(*) FROM dbt_mart.fct_orders_holiday_context) AS holiday_context_count;
```

The two counts should match.

## 7. Refresh Power BI

Open:

```text
powerbi/retail_analytics_dashboard.pbix
```

In Power BI Desktop:

```text
Home → Refresh
```

If Power BI asks for credentials, use the local PostgreSQL connection details:

```text
Server: localhost:5433
Database: retail_analytics
Mode: Import
```

After refresh, check the dashboard pages:

* Executive Overview
* Revenue & Orders
* Product & Seller Performance
* Delivery & Reviews
* Supplier Data Quality
* Holiday Impact

## 8. Commands to Avoid

Do not use this command unless you intentionally want to delete the PostgreSQL database volume:

```powershell
docker compose down -v
```

The `-v` flag deletes Docker volumes. For PostgreSQL, this removes the database data.

For normal stopping, use:

```powershell
docker compose down
```

or:

```powershell
docker compose stop
```

## Recovery Success Criteria

The recovery is complete when:

* PostgreSQL container is running
* `raw`, `staging`, `mart`, and `audit` schemas exist
* cleaned data is reloaded into the raw schema
* `audit.load_audit` contains successful load records
* dbt build passes
* `dbt_staging` and `dbt_mart` are recreated
* Power BI refresh succeeds
* dashboard visuals work again

## Portfolio Explanation

This recovery process demonstrates that the local analytics warehouse is reproducible. The project does not depend on a manually maintained PostgreSQL state. It can be rebuilt from version-controlled code, cleaned data outputs, and dbt models.
