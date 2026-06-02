# Supplier Quality Findings

## Purpose

This document summarizes the automated quality check results for the handmade supplier source file.
The goal is to interpret the supplier quality failures before writing cleaning logic or loading the data into PostgreSQL.
This file represents a realistic messy business source and is intentionally expected to contain data quality issues.
---
## Source Information
| Item | Value |
|---|---|
| Project | Retail Analytics Data Platform |
| Source name | Handmade supplier product updates |
| Source type | CSV |
| Source location | `data/raw/suppliers/` |
| Quality report | `reports/supplier_quality/run_date=2026-05-24/supplier_quality_checks.csv` |
| Review status | Completed |
---
## Quality Check Summary
The supplier quality job completed successfully and detected several expected issues.
The failures are related to:
- missing product identifiers
- missing currency values
- missing validity dates
- invalid numeric price values
- negative price values
- unexpected stock status values
- invalid date/timestamp values
- duplicate business keys
These failures are useful because they define what the supplier cleaning rules need to handle.
---
## Failed Checks
| rule_id | column_name | rule_type | severity | failed_count | total_count | interpretation |
|---|---|---|---|---:|---:|---|
| SUP_DQ_NOT_NULL_DQ003 | product_id | not_null | warning | 1 | 10 | One supplier row cannot be linked to an Olist product because product_id is missing |
| SUP_DQ_NOT_NULL_DQ007 | currency | not_null | error | 2 | 10 | Two rows have missing currency, so price meaning is incomplete |
| SUP_DQ_NOT_NULL_DQ008 | valid_from | not_null | warning | 2 | 10 | Two rows are missing the date from which the supplier update is valid |
| SUP_DQ_PRICE_NUMERIC_001 | updated_price | parseable_numeric | error | 1 | 10 | One price value cannot be converted to a number |
| SUP_DQ_PRICE_NON_NEGATIVE_001 | updated_price | non_negative | error | 1 | 9 | One numeric price value is negative |
| SUP_DQ_STOCK_STATUS_ACCEPTED_001 | stock_status | accepted_values | warning | 1 | 10 | One stock status is outside the accepted set |
| SUP_DQ_VALID_FROM_DATE_001 | valid_from | parseable_date | warning | 1 | 8 | One non-null valid_from value could not be parsed as a date |
| SUP_DQ_LAST_UPDATED_TIMESTAMP_001 | last_updated_at | parseable_timestamp | warning | 2 | 10 | Two last_updated_at values could not be parsed as timestamps |
| SUP_DQ_DUPLICATE_KEY_001 | supplier_id, product_id, supplier_product_code | duplicate_business_key | warning | 2 | 10 | Two rows share the same supplier business key and should be reviewed |
---
## Error-Level Issues
The following issues should block loading into a trusted cleaned/staging layer unless handled:
| issue | reason |
|---|---|
| Missing currency | Price cannot be safely interpreted |
| Non-parseable updated_price | Price cannot be used for analysis |
| Negative updated_price | Negative supplier price is not valid for this business context |
These should be cleaned, flagged, or rejected from trusted downstream use.
---
## Warning-Level Issues
The following issues may not block raw ingestion, but should be flagged and documented:
| issue | reason |
|---|---|
| Missing product_id | Row cannot be joined to Olist product data |
| Missing valid_from | Update validity period is unclear |
| Unknown stock_status | Value needs mapping or review |
| Invalid valid_from | Date cannot be used for effective-date logic |
| Invalid last_updated_at | Update audit timestamp is unreliable |
| Duplicate business key | Duplicate supplier update needs review |
Warnings should remain visible in the cleaned output or quality report.
---
## Cleaning Implications
The supplier cleaning job should:
- trim whitespace from text fields
- standardize currency to uppercase
- standardize stock_status values to uppercase snake case
- convert comma decimal prices such as `120,50` to `120.50`
- convert valid numeric prices to numeric values
- set non-parseable prices to null
- flag negative prices
- parse `valid_from` as a date
- parse `last_updated_at` as a timestamp
- add metadata columns
- preserve rows instead of deleting them automatically
- flag records with quality issues for later review
---
## Recommended Cleaning Flags
The cleaned supplier output should include quality flags.
| flag_name | meaning |
|---|---|
| has_missing_product_id | product_id is missing |
| has_missing_currency | currency is missing |
| has_invalid_price | updated_price could not be converted to numeric |
| has_negative_price | updated_price is below zero |
| has_unknown_stock_status | stock_status is outside accepted values |
| has_invalid_valid_from | valid_from could not be parsed |
| has_invalid_last_updated_at | last_updated_at could not be parsed |
| is_duplicate_business_key | duplicate supplier_id + product_id + supplier_product_code |
These flags allow the pipeline to preserve the row while making the issue visible.
---
## Data Engineering Decision
The supplier source should not be loaded directly into PostgreSQL in its raw business-file form.
Before loading, it should go through:
1. supplier cleaning rules
2. supplier cleaning job
3. supplier cleaned output validation
The cleaning job should preserve all rows, add standardized fields, and add quality flags rather than silently dropping problematic records.
---
## Next Actions
- Create `docs/supplier_cleaning_rules.md`
- Build supplier cleaning job
- Create cleaned supplier output under `data/processed/suppliers_clean/run_date=YYYY-MM-DD/`
- Validate cleaned supplier output
- Later load supplier data into PostgreSQL for joining with product data