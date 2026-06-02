This document should explain what the supplier profile shows before we create supplier quality checks
# Supplier Profile Findings

## Purpose

This document summarizes the first profiling review for the handmade supplier source file.

The goal is to understand the supplier data before writing quality checks, cleaning logic, or loading it into PostgreSQL.

---

## Source Information

| Item | Value |
|---|---|
| Project | Retail Analytics Data Platform |
| Source name | Handmade supplier product updates: `supplier_product_update_2026-05-24.csv` |
| Source type | CSV |
| Source location | `data/raw/suppliers/` |
| Inventory report | `reports/supplier_inventory/run_date=2026-05-28/supplier_file_inventory.csv` |
| Profile report | `reports/supplier_profile/run_date=2026-05-28/supplier_column_profile.csv` |
| Review status | Completed |

---

## Source Purpose

This supplier file is a manually maintained business file received from a supplier or business team.

It is intended to practice realistic data issues such as:

- extra spaces
- mixed casing
- missing identifiers
- price values stored as text
- comma decimal separators
- negative prices
- invalid timestamps
- missing currency values
- unknown stock statuses
- duplicate rows
- free-text comments

---

## Columns Reviewed

The supplier source contains the following columns:

- supplier_id
- supplier_name
- product_id
- supplier_product_code
- updated_price
- currency
- stock_status
- valid_from
- last_updated_at
- comments

---

## Initial Findings

| column_name | expected_type | issue_or_observation | expected_action |
|---|---|---|---|
| supplier_id | string | Required supplier identifier | Trim and validate not null |
| supplier_name | string | May contain extra spaces | Trim text |
| product_id | string | One row has missing product_id | Flag as warning or error depending on business rule |
| supplier_product_code | string | May contain extra spaces | Trim text |
| updated_price | numeric | Contains comma decimal, text value, and negative value | Standardize decimal separator, convert to numeric, flag invalid/negative values |
| currency | string/category | Contains mixed casing and one missing value | Uppercase and validate accepted values |
| stock_status | string/category | Contains mixed casing and unknown value | Standardize casing and validate accepted values |
| valid_from | date | Contains mixed date formats and missing value | Parse to date and flag missing/invalid values |
| last_updated_at | timestamp | Contains mixed timestamp formats and invalid value | Parse to timestamp and flag invalid values |
| comments | string | Free-text notes | Keep as optional text |

---

## Candidate Identifier Columns

| column_name | comment |
|---|---|
| supplier_id | Supplier identifier |
| product_id | Product identifier intended to connect supplier file to product data later |
| supplier_product_code | Supplier-specific product code |

`product_id` is especially important because it may later be used to connect supplier updates to the Olist products table.

---

## Candidate Numeric Columns

| column_name | issue |
|---|---|
| updated_price | Contains normal decimal values, comma decimal format, invalid text, and negative value |

This column requires cleaning before it can be used for analysis.

---

## Candidate Date/Time Columns

| column_name | expected_type | issue |
|---|---|---|
| valid_from | date | Contains mixed formats and one missing value |
| last_updated_at | timestamp | Contains mixed formats and one invalid value |

These columns should be parsed during the cleaning step.

---

## Candidate Categorical Columns

| column_name | expected_values | issue |
|---|---|---|
| currency | EUR, USD | Contains lowercase value and missing value |
| stock_status | IN_STOCK, OUT_OF_STOCK, LIMITED, DISCONTINUED | Contains mixed casing and unknown value |

The cleaning step should standardize categorical values.

---

## Acceptable Nulls

| column_name | reason |
|---|---|
| comments | Optional free-text field |

---

## Suspicious Nulls

| column_name | reason |
|---|---|
| supplier_id | Required supplier identifier |
| product_id | Required for linking supplier data to product data |
| supplier_product_code | Required supplier-side product reference |
| updated_price | Required for price update analysis |
| currency | Required to interpret price |
| valid_from | Required to know when price/update becomes valid |
| last_updated_at | Required for audit/update tracking |

---

## Candidate Data Quality Rules

| rule_id | column_name | rule_type | severity | description |
|---|---|---|---|---|
| SUP_DQ001 | supplier_id | not_null | error | Supplier ID should not be null |
| SUP_DQ002 | supplier_name | not_null | error | Supplier name should not be null |
| SUP_DQ003 | product_id | not_null | warning | Product ID should exist to connect supplier updates to products |
| SUP_DQ004 | supplier_product_code | not_null | error | Supplier product code should not be null |
| SUP_DQ005 | updated_price | parseable_numeric | error | Updated price should be convertible to numeric |
| SUP_DQ006 | updated_price | non_negative | error | Updated price should not be negative |
| SUP_DQ007 | currency | accepted_values | error | Currency should be within accepted values |
| SUP_DQ008 | stock_status | accepted_values | warning | Stock status should be within expected values |
| SUP_DQ009 | valid_from | parseable_date | warning | valid_from should be parseable as a date |
| SUP_DQ010 | last_updated_at | parseable_timestamp | warning | last_updated_at should be parseable as a timestamp |
| SUP_DQ011 | full_row | duplicate_row | warning | Duplicate rows should be detected and reviewed |

---

## Data Engineering Decision

The supplier source should not be loaded directly into PostgreSQL yet.

It first needs:

1. supplier quality checks
2. supplier cleaning rules
3. supplier cleaning job
4. supplier cleaned output validation

The source is a messy business file and should be cleaned separately from the Olist source.

---

## Next Actions

- Build automated supplier quality checks
- Document supplier cleaning rules
- Build supplier cleaning job
- Validate supplier cleaned output
- Later join supplier data to product data in PostgreSQL or staging models


### Commands: 
- python -m retail_analytics.cli.supplier_quality --run-date 2026-05-24
- python -c "import pandas as pd; df=pd.read_csv(r'.\reports\supplier_quality\run_date=2026-05-29\supplier_quality_checks.csv'); print(df['status'].value_counts()); print(df[df['status']=='FAIL'][['rule_id','column_name','rule_type','severity','failed_count','total_count','message']].to_string(index=False))"