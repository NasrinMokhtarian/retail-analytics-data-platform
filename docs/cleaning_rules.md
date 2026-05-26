# Cleaning Rules

## Purpose

This document defines the first raw-to-cleaned transformation rules for the Olist source files in the Retail Analytics Data Platform project.

The goal is to avoid random or hidden cleaning logic. Cleaning decisions should be documented before they are implemented in code.

The raw data must remain unchanged. Cleaned outputs will be written separately under:

`data/processed/olist_clean/run_date=YYYY-MM-DD/`

This supports traceability and repeatable data engineering work.

---

## Current Pipeline Context

Completed steps:

1. Raw file inventory
2. Raw column profiling
3. Raw profile findings
4. Automated raw data quality checks

Current step:

5. Define raw-to-cleaned transformation rules

Next step:

6. Build local cleaning job

---

## Cleaning Principles

The first cleaning version should be simple, safe, and transparent.

Core principles:

- preserve raw data unchanged
- create separate cleaned outputs
- do not delete records aggressively
- convert data types explicitly
- standardize column formats where useful
- add ingestion metadata
- flag suspicious records where needed
- document assumptions
- keep transformations easy to review

This is not the final modeling layer. The cleaned layer prepares data for PostgreSQL loading and later staging/modeling.

---

## Output Format

For the first version, cleaned files will be written as CSV because they are easy to inspect manually.

Initial output location:

`data/processed/olist_clean/run_date=YYYY-MM-DD/`

Later, after the workflow is stable, outputs may be written as Parquet for more production-style file handling.

Future output option:

`data/processed/olist_clean_parquet/run_date=YYYY-MM-DD/`

---

## Standard Metadata Columns

Each cleaned output file should include the following metadata columns:

| column_name | description |
|---|---|
| source_file_name | Original source CSV file name |
| ingested_at | UTC timestamp when the cleaned file was created |
| run_date | Logical pipeline run date |

These columns help with traceability and auditability.

---

## General Cleaning Rules

These rules apply to all Olist CSV files where relevant.

| rule_id | rule | action |
|---|---|---|
| CLEAN_GEN_001 | Preserve raw data | Never modify files under `data/raw/` |
| CLEAN_GEN_002 | Output separately | Write cleaned files under `data/processed/olist_clean/run_date=YYYY-MM-DD/` |
| CLEAN_GEN_003 | Column names | Keep original Olist column names for now to avoid breaking source traceability |
| CLEAN_GEN_004 | Text values | Trim leading and trailing spaces for text columns |
| CLEAN_GEN_005 | Empty strings | Convert empty strings to null values |
| CLEAN_GEN_006 | Metadata | Add `source_file_name`, `ingested_at`, and `run_date` |
| CLEAN_GEN_007 | Records | Do not delete records in the first cleaning version unless they are fully duplicated and clearly safe to remove |
| CLEAN_GEN_008 | Duplicates | Detect duplicate rows and document them before deciding removal |
| CLEAN_GEN_009 | Types | Convert known timestamp and numeric columns explicitly |
| CLEAN_GEN_010 | Errors | Invalid type conversions should be flagged, not silently ignored |

---

## Timestamp Columns

The following columns should be parsed as timestamps.

| source_file | column_name | target_type | nullable_expected | comment |
|---|---|---|---|---|
| olist_orders_dataset.csv | order_purchase_timestamp | timestamp | no | Main order creation timestamp |
| olist_orders_dataset.csv | order_approved_at | timestamp | yes | May be missing for canceled/unavailable orders |
| olist_orders_dataset.csv | order_delivered_carrier_date | timestamp | yes | May be missing if not shipped |
| olist_orders_dataset.csv | order_delivered_customer_date | timestamp | yes | May be missing if not delivered |
| olist_orders_dataset.csv | order_estimated_delivery_date | timestamp | no | Expected delivery date |
| olist_order_items_dataset.csv | shipping_limit_date | timestamp | no | Seller shipping deadline |
| olist_order_reviews_dataset.csv | review_creation_date | timestamp | no | Review creation date |
| olist_order_reviews_dataset.csv | review_answer_timestamp | timestamp | no | Review answer timestamp |

Cleaning action:

- parse using pandas `to_datetime`
- invalid parsing should produce null
- invalid timestamp counts should be logged or reported
- original raw files remain unchanged

---

## Numeric Columns

The following columns should be treated as numeric.

| source_file | column_name | target_type | nullable_expected | comment |
|---|---|---|---|---|
| olist_order_items_dataset.csv | price | decimal/float | no | Item price |
| olist_order_items_dataset.csv | freight_value | decimal/float | no | Shipping cost |
| olist_order_payments_dataset.csv | payment_value | decimal/float | no | Payment amount |
| olist_order_reviews_dataset.csv | review_score | integer | no | Review score |
| olist_products_dataset.csv | product_name_lenght | integer | yes | Source column name contains typo; keep original for now |
| olist_products_dataset.csv | product_description_lenght | integer | yes | Source column name contains typo; keep original for now |
| olist_products_dataset.csv | product_photos_qty | integer | yes | Number of product photos |
| olist_products_dataset.csv | product_weight_g | integer/float | yes | Product weight |
| olist_products_dataset.csv | product_length_cm | integer/float | yes | Product length |
| olist_products_dataset.csv | product_height_cm | integer/float | yes | Product height |
| olist_products_dataset.csv | product_width_cm | integer/float | yes | Product width |
| olist_geolocation_dataset.csv | geolocation_lat | float | no | Latitude |
| olist_geolocation_dataset.csv | geolocation_lng | float | no | Longitude |

Cleaning action:

- convert using pandas numeric conversion
- invalid numeric values should become null and be counted
- negative values should be flagged where not expected
- do not delete rows automatically

---

## Identifier and Key-Like Columns

The following columns should remain string-like.

| source_file | column_name | comment |
|---|---|---|
| olist_orders_dataset.csv | order_id | Main order identifier |
| olist_orders_dataset.csv | customer_id | Links orders to customers |
| olist_customers_dataset.csv | customer_id | Customer identifier used in orders |
| olist_customers_dataset.csv | customer_unique_id | Unique customer identity |
| olist_order_items_dataset.csv | order_id | Can repeat because one order can have multiple items |
| olist_order_items_dataset.csv | product_id | Product identifier |
| olist_order_items_dataset.csv | seller_id | Seller identifier |
| olist_order_payments_dataset.csv | order_id | Payment linked to order |
| olist_order_reviews_dataset.csv | review_id | Review identifier |
| olist_order_reviews_dataset.csv | order_id | Review linked to order |
| olist_products_dataset.csv | product_id | Product identifier |
| olist_sellers_dataset.csv | seller_id | Seller identifier |

Cleaning action:

- keep as string
- trim whitespace
- do not convert IDs to numeric
- check important IDs for nulls
- relationship checks will be added later

---

## Categorical Columns

The following columns should be treated as categorical/text fields.

| source_file | column_name | comment |
|---|---|---|
| olist_orders_dataset.csv | order_status | Order lifecycle status |
| olist_order_payments_dataset.csv | payment_type | Payment method |
| olist_customers_dataset.csv | customer_city | Customer city |
| olist_customers_dataset.csv | customer_state | Customer state |
| olist_sellers_dataset.csv | seller_city | Seller city |
| olist_sellers_dataset.csv | seller_state | Seller state |
| olist_products_dataset.csv | product_category_name | Product category |
| product_category_name_translation.csv | product_category_name | Original product category |
| product_category_name_translation.csv | product_category_name_english | English product category |

Cleaning action:

- trim whitespace
- keep as string
- do not force lowercase yet unless needed for joins or standardization
- monitor unexpected new values later

---

## Optional Nulls

The following nulls are considered acceptable in the raw/cleaned layer.

| source_file | column_name | reason |
|---|---|---|
| olist_order_reviews_dataset.csv | review_comment_title | Customer may leave only a score |
| olist_order_reviews_dataset.csv | review_comment_message | Customer may leave no written comment |
| olist_orders_dataset.csv | order_approved_at | May be missing for canceled or unavailable orders |
| olist_orders_dataset.csv | order_delivered_carrier_date | May be missing if order was not shipped |
| olist_orders_dataset.csv | order_delivered_customer_date | May be missing if order was not delivered |
| olist_products_dataset.csv | product_category_name | Some products may not have category data |
| olist_products_dataset.csv | product_name_lenght | Product descriptive metadata may be missing |
| olist_products_dataset.csv | product_description_lenght | Product descriptive metadata may be missing |
| olist_products_dataset.csv | product_photos_qty | Product descriptive metadata may be missing |
| olist_products_dataset.csv | product_weight_g | Product physical metadata may be missing |
| olist_products_dataset.csv | product_length_cm | Product physical metadata may be missing |
| olist_products_dataset.csv | product_height_cm | Product physical metadata may be missing |
| olist_products_dataset.csv | product_width_cm | Product physical metadata may be missing |

These nulls should be documented and handled carefully, not automatically treated as pipeline failures.

---

## Suspicious Nulls

Nulls in the following columns should be treated as suspicious.

| source_file | column_name | reason |
|---|---|---|
| olist_orders_dataset.csv | order_id | Required order identifier |
| olist_orders_dataset.csv | customer_id | Required customer relationship |
| olist_customers_dataset.csv | customer_id | Required customer identifier |
| olist_order_items_dataset.csv | order_id | Required order relationship |
| olist_order_items_dataset.csv | product_id | Required product relationship |
| olist_order_items_dataset.csv | seller_id | Required seller relationship |
| olist_order_items_dataset.csv | price | Required item price |
| olist_order_items_dataset.csv | freight_value | Required freight value |
| olist_order_payments_dataset.csv | order_id | Required order payment relationship |
| olist_order_payments_dataset.csv | payment_value | Required payment amount |
| olist_products_dataset.csv | product_id | Required product identifier |
| olist_sellers_dataset.csv | seller_id | Required seller identifier |

Suspicious nulls should be flagged and reviewed before the data is used in final analytical models.

---

## Source Column Name Issues

Some source column names contain spelling issues.

Examples:

| source_file | source_column | note |
|---|---|---|
| olist_products_dataset.csv | product_name_lenght | Source uses `lenght` instead of `length` |
| olist_products_dataset.csv | product_description_lenght | Source uses `lenght` instead of `length` |

Decision for first version:

- keep original source column names in cleaned CSV outputs
- document the issue
- rename columns later in staging/dbt models where business-friendly naming is more appropriate

Reason:

Keeping original names in the cleaned layer preserves traceability to the raw source.

---

## Duplicate Handling

First-version decision:

- detect fully duplicated rows
- do not remove duplicates automatically unless clearly safe
- document duplicate counts in a later data quality enhancement

Reason:

Automatic duplicate removal can hide source issues. It is better to first report duplicates, then decide based on business context.

---

## Record Exclusion Policy

First-version decision:

- do not delete records during initial cleaning
- preserve all source rows where possible
- add flags or quality reports instead of dropping data

Potential future flags:

| flag_name | meaning |
|---|---|
| has_invalid_timestamp | One or more timestamp fields could not be parsed |
| has_invalid_numeric_value | One or more numeric fields could not be converted |
| has_missing_required_id | A required identifier is missing |
| has_negative_business_value | A numeric value is negative where not expected |

These flags may be added later if needed.

---

## Planned Cleaned Output Files

For each raw Olist CSV file, create one cleaned output file.

| raw_file | cleaned_file |
|---|---|
| olist_customers_dataset.csv | customers_clean.csv |
| olist_geolocation_dataset.csv | geolocation_clean.csv |
| olist_order_items_dataset.csv | order_items_clean.csv |
| olist_order_payments_dataset.csv | order_payments_clean.csv |
| olist_order_reviews_dataset.csv | order_reviews_clean.csv |
| olist_orders_dataset.csv | orders_clean.csv |
| olist_products_dataset.csv | products_clean.csv |
| olist_sellers_dataset.csv | sellers_clean.csv |
| product_category_name_translation.csv | product_category_translation_clean.csv |

Output folder:

`data/processed/olist_clean/run_date=YYYY-MM-DD/`

---

## Later Improvements

After the first cleaning version is stable, the project can add:

- Parquet outputs
- schema contracts
- relationship checks
- duplicate checks
- PostgreSQL loading
- dbt staging models
- dbt tests
- API ingestion
- messy Excel supplier ingestion
- semi-structured JSON ingestion
- Docker
- Airflow orchestration
- cloud storage
- Terraform
- CI/CD

These are intentionally not added before the local workflow is stable.

---

## Current Decision

The raw Olist data passed the first automated quality check run.

The next engineering step is to implement the first raw-to-cleaned local transformation job using the rules in this document.

The first cleaning job should be simple, reviewable, and traceable.


### command to check and test result of cleaning process
- Get-ChildItem ".\data\processed\olist_clean" -Recurse
- Get-Content ".\reports\cleaning\run_date=2026-05-23\cleaning_summary.csv" -TotalCount 20
- Get-Content ".\data\processed\olist_clean\run_date=2026-05-23\orders_clean.csv" -TotalCount 5

so far:
raw data → inspected → profiled → quality checked → documented → cleaned outputs

### checking manually output
1. Are there 9 cleaned files?
2. Does cleaning_summary.csv show 9 source files?
3. Are invalid_timestamp_count and invalid_numeric_count zero or not?
4. Do cleaned files contain source_file_name, ingested_at, and run_date?
5. Do row counts look the same as the raw inventory report? 
 - python -c "import pandas as pd; raw=pd.read_csv(r'.\data\raw\olist\olist_order_reviews_dataset.csv'); clean=pd.read_csv(r'.\data\processed\olist_clean\run_date=2026-05-23\order_reviews_clean.csv'); print('raw rows:', len(raw)); print('clean rows:', len(clean)); print('difference:', len(raw)-len(clean)); print('clean columns:', clean.columns.tolist())"

### Check where your cleaned files actually are
### Cleaned output validation
- Get-ChildItem ".\data\processed\olist_clean" -Recurse
-  python -c "import pandas as pd; df=pd.read_csv(r'.\reports\cleaning_validation\run_date=2026-05-24\cleaning_validation_report.csv');print(df['status'].value_counts()); print(df[df['status']=='FAIL'][['check_id','source_file','cleaned_file','check_type','message']].to_string(index=False))"