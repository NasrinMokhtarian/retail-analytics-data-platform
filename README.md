# Retail Analytics Data Platform

A production-style, incremental data engineering project built around realistic retail/e-commerce data workflows.

---

## Project Purpose

This project supports my transition into the data job market as a career changer with a technical background but no commercial data engineering experience yet.

This repository is intentionally built incrementally.  
It starts with local data ingestion, profiling, cleaning, and SQL practice before moving into PostgreSQL, dbt, Spark, orchestration, and cloud integration.

---

## Business Context

The project is a retail analytics data platform for an e-commerce business.

The business wants to understand:

- order volume,
- customer behavior,
- product performance,
- seller performance,
- delivery performance,
- payment behavior,
- customer reviews,
- and operational data quality.

The initial dataset is a  E-Commerce dataset, which contains realistic e-commerce data such as customers, orders, products, payments, sellers, reviews, and geolocation.

Additional source types will be introduced gradually to simulate a more realistic data environment.

---

## Data Sources

### Current Source

| Source | Type | Status |
|---|---|---|
| Commerce Dataset | CSV, API, transactional Database | In progress |

### Planned Additional Sources

| Source Type | Purpose |
|---|---|
| JSON API | Practice API extraction, JSON parsing, error handling, and incremental ingestion |
| Messy Excel files | Simulate supplier/business files with inconsistent structure |
| Semi-structured JSON data | Practice nested data handling, flattening, schema drift, and event-style data |

The project starts with CSV files, but it is not intended to remain a CSV-only project.  
The long-term goal is to build a repeatable source onboarding pattern that can support different source types.

---

## Engineering Principles

This project follows production-style thinking from the beginning, without adding unnecessary complexity too early.

### Current Project Structure
## Current Project Status

The project has completed the local source onboarding, PostgreSQL loading, staging, mart modeling, and first business analysis workflow.

Current status:

```text
Local source onboarding
→ data profiling
→ data quality checks
→ cleaning
→ cleaned output validation
→ PostgreSQL loading
→ load audit
→ staging views
→ mart views
→ business analysis
```

This is currently a **local production-style data platform**, not yet a cloud production system.

The project is intentionally built locally first to strengthen SQL, Python, data quality, modeling, debugging, and business-oriented thinking before adding cloud complexity.

## dbt Transformation Layer

The project now includes a dbt transformation layer on top of the PostgreSQL raw schema.

The earlier manually written PostgreSQL staging and mart views were used as a validated SQL prototype. After validation, the transformation logic was migrated into dbt models.

Current dbt flow:

```text
PostgreSQL raw tables
→ dbt sources
→ dbt staging models
→ dbt mart models
→ dbt tests
→ dbt documentation and lineage

---

## Current Architecture

```text
data/raw/
    ├── olist/
    └── suppliers/

data/processed/
    ├── olist_clean/
    └── supplier_clean/

PostgreSQL
    ├── raw
    ├── staging
    ├── mart
    └── audit
```

### Local File Layers

| layer             | purpose                                                         |
| ----------------- | --------------------------------------------------------------- |
| `data/raw/`       | Original source files preserved unchanged                       |
| `data/processed/` | Cleaned and validated local outputs                             |
| `reports/`        | Inventory, profiling, quality, cleaning, and validation reports |
| `docs/`           | Design decisions, findings, and project documentation           |

### PostgreSQL Schemas

| schema    | purpose                                                                 |
| --------- | ----------------------------------------------------------------------- |
| `raw`     | Database landing/source-like tables loaded from cleaned validated files |
| `staging` | Typed and standardized SQL transformation views                         |
| `mart`    | Business-facing analytical views                                        |
| `audit`   | Load tracking and pipeline metadata                                     |

---

## Sources Included

### 1. Olist E-Commerce Dataset

The Olist dataset is used as the main e-commerce data source.

It includes customers, orders, order items, payments, reviews, products, sellers, geolocation, and product category translations.

### 2. Handmade Supplier Product Updates

A handmade supplier source was added to simulate a realistic messy business file.

It includes issues such as:

* missing product IDs
* missing currency values
* invalid prices
* negative prices
* unknown stock statuses
* invalid timestamps
* duplicate business keys

This source is used to practice realistic business-file ingestion, data quality checks, cleaning, and flagging.

---

## Completed Engineering Workflow

### Source Onboarding and Cleaning

Completed for Olist and supplier sources:

* raw file inventory
* column profiling
* profile findings documentation
* automated quality checks
* quality findings documentation
* cleaning rules
* cleaning jobs
* cleaned output validation

### PostgreSQL Loading

Cleaned and validated files are loaded into PostgreSQL using Python.

The load process includes:

* cleaned file to table mapping
* full-refresh loading into the `raw` schema
* row-count validation
* load audit records in `audit.load_audit`
* independent PostgreSQL load validation report

### Staging Layer

The `staging` schema contains typed and standardized SQL views.

Examples:

* `staging.stg_orders`
* `staging.stg_order_items`
* `staging.stg_customers`
* `staging.stg_products`
* `staging.stg_supplier_product_updates`

The staging layer prepares data for analytical modeling by casting timestamps, numeric fields, booleans, and preserving business keys.

### Mart Layer

The `mart` schema contains business-facing analytical views.

Current mart views:

| mart view                           | purpose                                             |
| ----------------------------------- | --------------------------------------------------- |
| `mart.dim_customers`                | Customer geography and identity                     |
| `mart.dim_products`                 | Product attributes and translated category          |
| `mart.dim_sellers`                  | Seller identity and geography                       |
| `mart.fct_orders`                   | Order lifecycle and delivery metrics                |
| `mart.fct_order_items`              | Item-level revenue and seller/product relationships |
| `mart.fct_payments`                 | Payment behavior                                    |
| `mart.fct_reviews`                  | Review scores and sentiment grouping                |
| `mart.fct_supplier_product_updates` | Supplier update records and quality flags           |

---

## Validation Gates Implemented

The project includes validation at multiple stages:

| stage                      | validation purpose                                                             |
| -------------------------- | ------------------------------------------------------------------------------ |
| Raw quality checks         | Confirm source files and critical fields are usable                            |
| Cleaned output validation  | Confirm cleaned files exist, preserve row counts, and contain metadata         |
| PostgreSQL load validation | Confirm database tables match cleaned files and audit records                  |
| Staging validation         | Confirm staging views preserve row counts, keys, types, and join readiness     |
| Mart validation            | Confirm business-facing views respect grain, metrics, joins, and quality flags |

This validation-first approach helps prevent silent data issues from reaching business analysis.

---

## First Business Analysis Results

The mart layer was used to answer first business questions around revenue, customers, products, delivery, reviews, payments, and supplier quality.

Key findings:

* November 2017 was the highest revenue month among the reviewed months, with item revenue of 1,010,271.37.
* The highest revenue product categories were `health_beauty`, `watches_gifts`, `bed_bath_table`, `sports_leisure`, and `computers_accessories`.
* SP was the dominant customer state by both item revenue and order count.
* Late deliveries had a significantly lower average review score than non-late deliveries: 2.57 vs 4.29.
* Credit card was the dominant payment method by total payment value.
* Supplier records with quality issues remain visible through quality flags and the `needs_business_review` field.

These findings show that the platform supports both technical data engineering workflows and business-facing analysis.

---

## Current Technical Stack

| area             | tools                                     |
| ---------------- | ----------------------------------------- |
| Programming      | Python                                    |
| Data processing  | pandas                                    |
| Database         | PostgreSQL                                |
| Database UI      | pgAdmin                                   |
| Containerization | Docker Compose for PostgreSQL and pgAdmin |
| SQL modeling     | PostgreSQL views                          |
| Data quality     | Custom Python checks and SQL validation   |
| Logging          | Structured logging                        |
| Version control  | Git                                       |
| Documentation    | Markdown                                  |

---

## Why This Project Is Built Locally First

This project is intentionally built as a local production-style platform before moving to cloud.

The goal is to strengthen:

* SQL fluency
* Python fluency
* data quality thinking
* source onboarding discipline
* debugging confidence
* relational modeling
* business analysis
* documentation habits
* Git-based workflow

A cloud extension is planned later, but the foundation is built locally first to avoid hiding weak data logic behind cloud tooling.

---

## Planned Next Phases

### Phase 3 — dbt Migration

The validated PostgreSQL staging and mart SQL will be migrated into dbt.

Planned dbt work:

* dbt sources
* staging models
* mart models
* schema tests
* relationship tests
* accepted value tests
* dbt documentation
* lineage

### Phase 4 — BI Layer

A BI dashboard will be built on top of the mart layer.

Possible tools:

* Power BI
* Tableau

The BI layer should consume business-ready mart models, not raw tables.

### Phase 5 — Workflow Hardening

Planned improvements:

* task runner or Makefile
* improved test structure
* stronger error handling
* repeatable local workflow commands
* Docker refinement

### Phase 6 — Orchestration

Airflow will be added after the individual jobs are stable.

Airflow will orchestrate:

* source onboarding
* quality checks
* cleaning
* validation
* PostgreSQL loading
* dbt transformations

### Phase 7 — AWS Cloud Extension

A controlled AWS extension is planned later.

Possible AWS components:

* S3 for raw/processed/curated zones
* Parquet outputs
* Glue or Athena for query/processing
* Redshift if warehouse loading is added
* CloudWatch for monitoring

The cloud extension will build on the same workflow already proven locally.

---

## Portfolio Positioning

This project is not presented as an enterprise production platform.

It is a **production-style local data engineering and analytics platform** designed to simulate realistic commercial workflows.

It demonstrates:

* source onboarding
* data profiling
* data quality checks
* cleaning and validation
* PostgreSQL loading
* audit logging
* staging and mart modeling
* business analysis
* documentation
* Git-based incremental development

The project is designed to support transition into junior or bridge data roles such as:

* BI Developer
* ETL Developer
* Junior Analytics Engineer
* SQL Developer
* Data Analyst with Python/SQL
* Data Engineer
