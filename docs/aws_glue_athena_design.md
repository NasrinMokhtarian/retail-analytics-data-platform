# AWS Glue and Athena Design

## Purpose

This document defines the Glue Data Catalog and Athena query design for the Retail Analytics Data Platform.

The goal is to query cleaned data stored in S3 using a low-cost, serverless SQL layer before introducing Redshift.

This is a design document. Glue and Athena resources should be created with Terraform in the next implementation step.

---

## Current AWS State

The project currently has:

```text
Terraform bootstrap state bucket
→ dev Terraform remote backend
→ S3 data lake bucket
→ processed cleaned outputs uploaded to S3
→ S3 upload validation report
```

Current S3 processed layout:

```text
s3://retail-analytics-datalake-nasrin-dev-eu-central-1/
  processed/
    olist_clean/
      run_date=2026-05-26/
    supplier_clean/
      run_date=2026-06-01/
    br_holidays_clean/
      run_date=2026-06-16/
```

---

## Why Glue and Athena

Athena allows SQL queries directly over data stored in S3.

Glue Data Catalog provides table metadata used by Athena.

This creates a lightweight cloud analytics layer without running a database server.

Chosen first cloud query layer:

```text
S3
→ Glue Data Catalog
→ Athena
```

Delayed until later:

```text
Redshift Serverless
```

Reason:

Athena is a good first cloud query layer because there is no always-on warehouse to manage. Redshift is stronger for warehouse-style analytics, but it should come after the S3/Athena layer is validated.

---

## Cost-Control Rules

Athena cost is based on data scanned by queries.

Therefore:

* query only the processed zone first
* avoid repeated broad `SELECT *` queries
* validate with small row-count and sample queries
* use partitioned S3 prefixes with `run_date=YYYY-MM-DD`
* move to Parquet later to reduce scanned data
* keep Athena query results in a dedicated S3 prefix
* use a dedicated Athena workgroup
* configure query limits where practical

---

## Initial Implementation Choice

For the first implementation, use:

```text
Glue database
Athena workgroup
manually defined external tables through Terraform
```

Do not use Glue crawlers yet.

Reason:

* source files are known
* schemas are controlled
* Terraform-defined tables are easier to review
* no crawler runs are needed
* lower operational complexity
* easier to explain in interviews

Glue crawlers may be introduced later as a comparison or automation improvement.

---

## Glue Database

Recommended database name:

```text
retail_analytics_processed_dev
```

Purpose:

Contains external table metadata for cleaned processed data in S3.

---

## Athena Workgroup

Recommended workgroup name:

```text
retail_analytics_dev
```

Purpose:

* separate project queries from default Athena usage
* store Athena query results in the project data lake bucket
* support future query limits and settings
* improve cost visibility

Athena query results location:

```text
s3://retail-analytics-datalake-nasrin-dev-eu-central-1/athena-results/
```

---

## Initial External Tables

Initial Glue/Athena tables should represent the cleaned processed files, not raw source files.

Recommended first tables:

| Table                      | Source prefix                                                                     |
| -------------------------- | --------------------------------------------------------------------------------- |
| `olist_orders`             | `processed/olist_clean/run_date=2026-05-26/orders_clean.csv`                      |
| `olist_order_items`        | `processed/olist_clean/run_date=2026-05-26/order_items_clean.csv`                 |
| `olist_customers`          | `processed/olist_clean/run_date=2026-05-26/customers_clean.csv`                   |
| `olist_products`           | `processed/olist_clean/run_date=2026-05-26/products_clean.csv`                    |
| `supplier_product_updates` | `processed/supplier_clean/run_date=2026-06-01/supplier_product_updates_clean.csv` |
| `br_holidays`              | `processed/br_holidays_clean/run_date=2026-06-16/br_holidays_clean.csv`           |

Not all Olist files need to be added in the first Athena step.

Start with enough tables to validate:

* row counts
* order date logic
* customer geography
* product joins
* holiday enrichment potential
* supplier quality data

---

## CSV First, Parquet Later

Initial table format:

```text
CSV
```

Reason:

* current cleaned outputs are CSV
* easiest first cloud validation step
* avoids changing too many things at once

Later optimized format:

```text
Parquet
```

Reason:

* columnar
* usually smaller
* better for Athena scan cost
* better for analytics query performance
* useful PySpark/Glue learning step

---

## Partition Strategy

Current S3 prefixes already use run-date partition style:

```text
run_date=YYYY-MM-DD
```

For the first implementation, table locations may point directly to one run-date prefix.

Later, we can define partitioned external tables using `run_date` as a partition column.

Recommended progression:

```text
Step 1: one table per current run-date prefix
Step 2: add run_date partition awareness
Step 3: convert selected outputs to Parquet
Step 4: query partitioned Parquet through Athena
```

---

## Validation Queries

After implementation, run small validation queries.

Examples:

```sql
SELECT COUNT(*) FROM retail_analytics_processed_dev.olist_orders;
```

```sql
SELECT COUNT(*) FROM retail_analytics_processed_dev.br_holidays;
```

```sql
SELECT
    order_status,
    COUNT(*) AS order_count
FROM retail_analytics_processed_dev.olist_orders
GROUP BY order_status
ORDER BY order_count DESC;
```

```sql
SELECT
    holiday_type,
    COUNT(*) AS holiday_count
FROM retail_analytics_processed_dev.br_holidays
GROUP BY holiday_type
ORDER BY holiday_count DESC;
```

The first target is not complex analytics.

The first target is:

```text
Can Athena read the cleaned files in S3 correctly?
```

---

## What Not To Do Yet

Do not create yet:

* Redshift Serverless
* Glue Spark jobs
* Glue crawlers
* MWAA
* Airflow AWS DAGs
* dbt on Athena
* dbt on Redshift

Those come after the basic S3/Athena layer is validated.

---

## Future dbt Direction

There are two possible dbt cloud paths later.

### Option A — dbt on Athena

```text
S3 processed/curated data
→ Glue Data Catalog
→ Athena
→ dbt-athena
→ Power BI or query exports
```

Pros:

* low infrastructure overhead
* no always-on warehouse
* good data lake learning

Cons:

* dbt-athena setup is less common than dbt-redshift
* Athena has different performance behavior from a warehouse

### Option B — dbt on Redshift

```text
S3 processed/curated data
→ Redshift Serverless
→ dbt-redshift
→ Power BI
```

Pros:

* stronger analytics-engineering story
* closer to warehouse-style BI
* Power BI connection is straightforward

Cons:

* higher cost risk
* requires stricter destroy workflow

Recommended path:

```text
Validate S3/Athena first
→ optimize with Parquet
→ then introduce Redshift
→ run dbt on Redshift
→ connect Power BI to Redshift marts
```

---

## Definition of Done

Phase 8.11 is complete when:

```text
1. docs/aws_glue_athena_design.md exists
2. Glue database naming is defined
3. Athena workgroup naming is defined
4. Athena query result location is defined
5. first external tables are listed
6. CSV-first strategy is documented
7. Parquet-later strategy is documented
8. Redshift remains intentionally delayed
9. document is committed and pushed
```
