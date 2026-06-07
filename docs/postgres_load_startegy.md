# PostgreSQL Load Strategy

## Purpose

This document defines how cleaned and validated local files will be loaded into PostgreSQL for the Retail Analytics Data Platform project.

The goal is to move from file-based processing into a relational database while keeping the workflow traceable, auditable, and business-aligned.

---

## Current Context

Completed before PostgreSQL loading:

- Olist raw inventory
- Olist raw profiling
- Olist raw quality checks
- Olist cleaning rules
- Olist cleaned output generation
- Olist cleaned output validation
- supplier source generation
- supplier inventory and profiling
- supplier quality checks
- supplier cleaning rules
- supplier cleaned output generation
- supplier cleaned output validation
- PostgreSQL and pgAdmin setup with Docker
- PostgreSQL schemas created with Python

The next step is to load cleaned and validated files into PostgreSQL.

---

## Database Schemas

The project uses the following PostgreSQL schemas:

| schema | purpose |
|---|---|
| raw | Database landing/source-like tables loaded from cleaned validated files |
| staging | SQL-standardized transformation layer |
| mart | Business-ready analytical tables |
| audit | Pipeline and load tracking metadata |

---

## Important Design Decision

The PostgreSQL `raw` schema will receive cleaned and validated local files, not the original unprocessed raw source files.

Reason:

The original files are preserved under `data/raw/`.

The local pipeline already creates validated cleaned files under `data/processed/`.

Therefore, PostgreSQL loading should use the cleaned validated files as the database landing layer.

This keeps the database safer while preserving source traceability through metadata columns such as:

- source_file_name
- ingested_at
- run_date

---

## Sources to Load

### Olist Source

| cleaned file | target schema | target table |
|---|---|---|
| customers_clean.csv | raw | olist_customers |
| geolocation_clean.csv | raw | olist_geolocation |
| order_items_clean.csv | raw | olist_order_items |
| order_payments_clean.csv | raw | olist_order_payments |
| order_reviews_clean.csv | raw | olist_order_reviews |
| orders_clean.csv | raw | olist_orders |
| products_clean.csv | raw | olist_products |
| sellers_clean.csv | raw | olist_sellers |
| product_category_translation_clean.csv | raw | product_category_translation |

### Supplier Source

| cleaned file | target schema | target table |
|---|---|---|
| supplier_product_updates_clean.csv | raw | supplier_product_updates |

---

## First-Version Load Behavior

The first version will use a full-refresh load strategy.

For each target table:

1. Read cleaned CSV file with pandas.
2. Replace the existing PostgreSQL table.
3. Load all rows.
4. Count loaded rows in PostgreSQL.
5. Compare loaded row count with source file row count.
6. Write result to `audit.load_audit`.

This is intentionally simple and reliable for the first database-loading version.

---

## Why Full Refresh First?

Full refresh is easier to reason about while the project is still local.

It helps verify:

- table creation
- column loading
- row count matching
- audit tracking
- SQL query readiness

Incremental loading will be added later when the database workflow is stable.

Future improvements may include:

- append loads
- run_date partitioning inside tables
- upsert logic
- primary keys
- deduplication logic
- incremental source extraction
- orchestration with Airflow

---

## Audit Table

The project will create:

`audit.load_audit`

Purpose:

Track every file-to-database load.

Planned columns:

| column_name | description |
|---|---|
| load_id | Unique load record ID |
| run_date | Logical pipeline run date |
| source_name | Source group such as `olist` or `supplier` |
| source_file | Cleaned file name loaded |
| target_schema | PostgreSQL target schema |
| target_table | PostgreSQL target table |
| source_row_count | Row count from cleaned file |
| loaded_row_count | Row count in PostgreSQL table after load |
| load_started_at | UTC load start time |
| load_finished_at | UTC load finish time |
| status | SUCCESS or FAILED |
| error_message | Error details if the load failed |

---

## Validation Rule

For each table load:

```text
source_row_count must equal loaded_row_count