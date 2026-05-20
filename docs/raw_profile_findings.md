# Raw Profile Findings

## Purpose

This document summarizes the first raw data profiling review for the Olist source files.

The goal is to understand column-level data quality before loading the data into PostgreSQL.

## Source

Source name: Olist Brazilian E-Commerce Dataset  
Source type: CSV  
Profile report: `reports/raw_profile/run_date=2026-05-18/raw_column_profile.csv`

---

## 1. Files Profiled

Total files profiled: 9

Main source tables:

- customers
- orders
- order items
- payments
- reviews
- products
- sellers
- geolocation
- product category translation

---

## 2. Initial Observations

### High-null columns

| file_name | column_name | null_percentage | comment |
|---|---:|---:|---|
|  |  |  |  |

### Possible primary keys or unique identifiers

| file_name | column_name | row_count | distinct_count | comment |
|---|---|---:|---:|---|
|  |  |  |  |  |

### Date/time columns

| file_name | column_name | current_dtype | expected_type | comment |
|---|---|---|---|---|
|  |  |  | timestamp |  |

### Numeric columns

| file_name | column_name | current_dtype | expected_type | comment |
|---|---|---|---|---|
|  |  |  | numeric |  |

### Categorical columns

| file_name | column_name | distinct_count | sample_values | comment |
|---|---|---:|---|---|
|  |  |  |  |  |

---

## 3. Business-Acceptable Nulls

Some nulls may be normal.

Examples:

- `review_comment_title` can be null because customers may leave only a score.
- `review_comment_message` can be null because customers may not write a text review.
- some delivery timestamp fields may be null if an order was canceled or unavailable.

---

## 4. Suspicious Nulls

These columns should be investigated if nulls exist:

- order identifiers
- customer identifiers
- seller identifiers
- product identifiers
- payment values
- order purchase timestamps

---

## 5. Candidate Data Quality Rules

Initial rules to automate later:

| rule_id | table_name | column_name | rule_type | severity | description |
|---|---|---|---|---|---|
| DQ001 | orders | order_id | not_null | error | Every order should have an order_id |
| DQ002 | customers | customer_id | not_null | error | Every customer row should have a customer_id |
| DQ003 | order_items | price | non_negative | error | Item price should not be negative |
| DQ004 | payments | payment_value | non_negative | error | Payment value should not be negative |
| DQ005 | orders | order_status | accepted_values | warning | Order status should be within expected values |

---

## 6. Next Actions

- Build automated raw data quality checks.
- Create a raw data quality report.
- Use the profile findings to support PostgreSQL table design later.


<!-- Get-Content ".\reports\raw_profile\run_date = 2026-05-20\raw_column_profile.csv" -TotalCount 20 -->