# Raw Profile Findings

# Raw Profile Findings

## Purpose

This document summarizes the first column-level profiling review for the Olist raw CSV source files.

The goal is to understand the raw data before loading it into PostgreSQL, designing schemas, or writing transformation logic.

This review supports the next step: defining automated raw data quality checks.

---

## Source Information

| Item | Value |
|---|---|
| Project | Retail Analytics Data Platform |
| Source name | Olist Brazilian E-Commerce Dataset |
| Source type | CSV |
| Source location | `data/raw/olist/` |
| Profile report | `reports/raw_profile/run_date=2026-05-18/raw_column_profile.csv` |
| Review status | In progress |

---

## 1. Files Profiled

The profiling job reviewed all available Olist CSV files and generated one profile row per column.

Main source entities:

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

## 2. What the Raw Profile Report Contains

The raw column profile contains:

- source file name
- column name
- pandas inferred data type
- row count
- null count
- null percentage
- non-null count
- distinct count
- sample values
- profiling timestamp

This helps identify data quality risks before loading the data into PostgreSQL.

---

## 3. High-Null Columns

These columns have noticeable missing values and should be reviewed before cleaning or modeling.

| file_name | column_name | null_percentage | null_count | initial_comment |
|olist_order_reviews_dataset.csv|review_comment_title|88.34|87656|99224|
|olist_order_reviews_dataset.csv | review_comment_message  | 58.70 |  58247 | 99224 |
|olist_products_dataset.csv | product_name_lenght |1.85 |610|    
|32951 olist_products_dataset.csv|product_photos_qty |1.85 | 610 |32951|
|olist_products_dataset.csv  | product_category_name|1.85| 610 |32951|
|olist_products_dataset.csv  |  product_description_lenght  |1.85|610|32951|
|olist_orders_dataset.csv | order_delivered_carrier_date |1.79|1783| 99441|
|olist_orders_dataset.csv |order_approved_at| 0.16|160|99441|

### Initial interpretation

Some null values may be business-acceptable. For example, review comments may be empty because customers can leave a score without writing a text review.

Other nulls may indicate data quality risks, especially if they appear in identifiers, payment values, timestamps, or required relationship fields.

---

## 4. Candidate Identifier Columns

These columns look like IDs or relationship keys.

| file_name | column_name | row_count | distinct_count | initial_comment |
 |olist_customers_dataset.csv  |customer_id |99441 |99441 |1.000000|
  |olist_customers_dataset.csv|customer_unique_id|99441|96096|0.966362|
|olist_customers_dataset.csv|ustomer_zip_code_prefix|99441|14994| 0.150783|
|olist_geolocation_dataset.csv| geolocation_zip_code_prefix|1000163 |19015|0.019012|
|olist_order_items_dataset.csv| order_id|112650|98666| 0.875863|
|olist_order_items_dataset.csv| order_item_id| 112650| 21 | 0.000186|
|olist_order_items_dataset.csv|product_id| 112650| 32951| 0.292508|
|olist_order_items_dataset.csv |seller_id| 112650 | 3095|0.027474|
|olist_order_payments_dataset.csv|order_id|103886| 99440 | 0.957203|
|olist_order_reviews_dataset.csv | order_id |99224| 98673| 0.994447|
|olist_order_reviews_dataset.csv |review_id |99224 |98410 | 0.991796|
|olist_orders_dataset.csv|customer_id|99441|99441| 1.000000|
|olist_orders_dataset.csv |order_id|99441|99441|1.000000|
|olist_products_dataset.csv |product_id|32951|32951|1.000000|
|olist_products_dataset.csv |product_width_cm|32951 | 95|0.002883|
|olist_sellers_dataset.csv| seller_id| 3095 |3095|1.000000|
|olist_sellers_dataset.csv|seller_zip_code_prefix |3095  |2246| 0.725687|

### Initial interpretation

Identifier columns will be important later for:

- PostgreSQL table design
- joins between tables
- uniqueness checks
- relationship checks
- dbt tests

Not every ID column must be unique. For example, `order_id` may repeat in an order items table because one order can contain multiple items.

---

## 5. Candidate Date/Time Columns

These columns appear to represent dates or timestamps.

| file_name | column_name | current_dtype | expected_type | initial_comment |
|olist_order_items_dataset.csv| shipping_limit_date| str|0.00|["2017-09-19 09:45:35", "2017-05-03 11:05:13", "2018-01-18 14:48:30", "2018-08-15 10:10:18", "2017-02-13 13:57:51"]|
|olist_order_reviews_dataset.csv|review_creation_date|str|0.00 ["2018-01-18 00:00:00", "2018-03-10 00:00:00", "2018-02-17 00:00:00", "2017-04-21 00:00:00", "2018-03-01 00:00:00"]|
|olist_order_reviews_dataset.csv|review_answer_timestamp|str|0.00 ["2018-01-18 21:46:59", "2018-03-11 03:05:13", "2018-02-18 14:36:24", "2017-04-21 22:02:06", "2018-03-02 10:26:53"]|
|olist_orders_dataset.csv|order_purchase_timestamp|str|0.00 |["2017-10-02 10:56:33", "2018-07-24 20:41:37", "2018-08-08 08:38:49", "2017-11-18 19:28:06", "2018-02-13 21:18:39"]|
|olist_orders_dataset.csv|order_approved_at|str|0.16|["2017-10-02 11:07:15", "2018-07-26 03:24:27", "2018-08-08 08:55:23", "2017-11-18 19:45:59", "2018-02-13 22:20:29"]
|olist_orders_dataset.csv|order_delivered_carrier_date|str|1.79|["2017-10-04 19:55:00", "2018-07-26 14:31:00", "2018-08-08 13:50:00", "2017-11-22 13:39:59", "2018-02-14 19:46:34"]
|olist_orders_dataset.csv| order_delivered_customer_date|str|2.98| ["2017-10-10 21:25:13", "2018-08-07 15:27:45", "2018-08-17 18:06:29", "2017-12-02 00:28:42", "2018-02-16 18:17:02"]
|olist_orders_dataset.csv| order_estimated_delivery_date|str|0.00| ["2017-10-18 00:00:00", "2018-08-13 00:00:00", "2018-09-04 00:00:00", "2017-12-15 00:00:00", "2018-02-26 00:00:00"]

### Initial interpretation

Many date/time columns may currently appear as `object` in pandas because they were read from CSV as strings.

These columns will likely need parsing during the cleaning or staging step.

---

## 6. Candidate Numeric Columns

These columns appear to represent numeric business measures.

| file_name | column_name | current_dtype | expected_type | initial_comment |
|olist_order_items_dataset.csv |price|float64|0.00|["58.9", "239.9", "199.0", "12.99", "199.9"]|
|olist_order_items_dataset.csv|freight_value|float64|0.00|["13.29", "19.93", "17.87", "12.79", "18.14"]|
|olist_order_payments_dataset.csv|payment_value|float64|0.00 ["99.33", "24.39", "65.71", "107.78", "128.45"]|
|olist_order_reviews_dataset.csv|review_score|int64|0.00|["4", "5", "1", "3", "2"]|
|olist_products_dataset.csv|product_photos_qty|float64|1.85|["1.0", "4.0", "2.0", "3.0", "5.0"]|
|olist_products_dataset.csv|product_weight_g|float64|0.01|["225.0", "1000.0", "154.0", "371.0", "625.0"]|
|olist_products_dataset.csv|product_length_cm|float64|0.01|["16.0", "30.0", "18.0", "26.0", "20.0"]|
|olist_products_dataset.csv|product_height_cm|float64|0.01|["10.0", "18.0", "9.0", "4.0", "17.0"]|
|olist_products_dataset.csv|product_width_cm|float64|0.01|["14.0", "20.0", "15.0", "26.0", "13.0"]|

Examples may include:

- price
- freight value
- payment value
- product weight
- product length
- product height
- product width

These columns may need checks for negative values, missing values, and unrealistic values.

---

## 7. Candidate Categorical Columns

These columns appear to contain a limited set of categories.

| file_name | column_name | column_dtype | distinct_count | sample_values |
|olist_customers_dataset.csv|customer_state|str|27|["SP", "SC", "MG", "PR", "RJ"]|
|olist_geolocation_dataset.csv|geolocation_state|str|27|["SP", "RN", "AC", "RJ", "ES"]|
|olist_order_items_dataset.csv|order_item_id|int64|21|["1", "2", "3", "4", "5"]|
|olist_order_payments_dataset.csv|payment_type|str|5 |["credit_card", "boleto", "voucher", "debit_card", "not_defined"]|
|olist_order_payments_dataset.csv| payment_installments|int64|24|["8", "1", "2", "3", "6"]|
|olist_order_payments_dataset.csv|payment_sequential|int64|29|["1", "2", "4", "5", "3"]|
|olist_order_reviews_dataset.csv|review_score|int64|5|["4", "5", "1", "3", "2"]|
|olist_orders_dataset.csv|order_status|str|8 ["delivered", "invoiced", "shipped", "processing", "unavailable"]|
|olist_products_dataset.csv|product_photos_qty|float64|19 v["1.0", "4.0", "2.0", "3.0", "5.0"]|
|olist_sellers_dataset.csv|seller_state|str|23|["SP", "RJ", "PE", "PR", "GO"]|
Examples may include:

- order status
- payment type
- customer state
- seller state
- product category

Categorical columns may be used later for accepted-value checks and business reporting.

---

## 8. Business-Acceptable Nulls

Initial examples of nulls that may be acceptable:

| file_name | column_name | reason |
|---|---|---|
| reviews | review_comment_title | Customers may leave a review score without a title |
| reviews | review_comment_message | Customers may leave a review score without a written message |

This section should be updated after reviewing the actual profile report.

---

## 9. Suspicious Nulls

Nulls in these types of columns should be treated as suspicious:

- order identifiers
- customer identifiers
- product identifiers
- seller identifiers
- payment values
- order purchase timestamps
- required join keys

These should become candidate data quality checks.

---

## 10. Initial Candidate Data Quality Rules

| rule_id | source_file | column_name | rule_type | severity | description |
|---|---|---|---|---|---|
| DQ001 | olist_orders_dataset.csv | order_id | not_null | error | Every order should have an order_id |
| DQ002 | olist_orders_dataset.csv | customer_id | not_null | error | Every order should be linked to a customer |
| DQ003 | olist_order_items_dataset.csv | price | non_negative | error | Item price should not be negative |
| DQ004 | olist_order_payments_dataset.csv | payment_value | non_negative | error | Payment value should not be negative |
| DQ005 | olist_orders_dataset.csv | order_status | accepted_values | warning | Order status should be within expected known values |
| DQ006 | olist_orders_dataset.csv | order_purchase_timestamp | parseable_timestamp | error | Purchase timestamp should be parseable as a timestamp |

---

## 11. Next Actions

The next engineering step is to build an automated raw data quality check job that creates:

`reports/data_quality/run_date=YYYY-MM-DD/raw_quality_checks.csv`

The first version should check:

- expected files exist
- required columns exist
- important ID columns are not null
- important numeric columns are not negative
- important timestamp columns are parseable
- selected categorical columns contain expected values

---

## Review Notes

This document is intentionally based on the raw profiling output.  
The goal is not to clean the data yet, but to understand the data well enough to define practical quality rules.

- Get-ChildItem ".\reports\raw_profile" -Recurse   #to check profile exists
- Get-Content ".\reports\raw_profile\run_date = 2026-05-20\raw_column_profile.csv" -TotalCount 20
# A. Show highest-null columns 
- python -c "import pandas as pd; df=pd.read_csv(r'.\reports\raw_profile\run_date=2026-05-20\raw_column_profile.csv'); print(df.sort_values('null_percentage', ascending=False)[['file_name','column_name','null_percentage','null_count','row_count']].head(20).to_string(index=False))"
# B. Find possible identifier columns
- python -c "import pandas as pd; df=pd.read_csv(r'.\reports\raw_profile\run_date=2026-05-20\raw_column_profile.csv'); df['distinct_ratio']=df['distinct_count']/df['row_count']; print(df[df['column_name'].str.contains('id|code|prefix', case=False, na=False)][['file_name','column_name','row_count','distinct_count','distinct_ratio']].sort_values(['file_name','column_name']).to_string(index=False))"
# C. Find date/time columns
- python -c "import pandas as pd; df=pd.read_csv(r'.\reports\raw_profile\run_date=2026-05-20\raw_column_profile.csv'); print(df[df['column_name'].str.contains('date|timestamp|approved|delivered|estimated|shipping|limit', case=False, na=False)][['file_name','column_name','column_dtype','null_percentage','sample_values']].to_string(index=False))"
# D. Find numeric business columns
- python -c "import pandas as pd; df=pd.read_csv(r'.\reports\raw_profile\run_date=2026-05-20\raw_column_profile.csv'); print(df[df['column_name'].str.contains('price|value|freight|weight|length|height|width|score|qty|quantity', case=False, na=False)][['file_name','column_name','column_dtype','null_percentage','sample_values']].to_string(index=False))"

# E. Find categorical columns
- python -c "import pandas as pd; df=pd.read_csv(r'.\reports\raw_profile\run_date = 2026-05-20\raw_column_profile.csv'); print(df[(df['distinct_count'] <= 30) & (df['row_count'] > 0)][['file_name','column_name','column_dtype','distinct_count','sample_values']].sort_values(['file_name','distinct_count']).to_string(index=False))"

# find failed quality check
- Get-Content ".\reports\data_quality\run_date=2026-05-18\raw_quality_checks.csv" -TotalCount 30
- python -c "import pandas as pd; df=pd.read_csv(r'.\reports\data_quality\run_date=2026-05-23\raw_quality_checks.csv'); print(df['status'].value_counts()); print(df[df['status']=='FAIL'][['rule_id','source_file','column_name','rule_type','severity','failed_count','total_count','message']].to_string(index=False))"

- python -c "import pandas as pd; df=pd.read_csv(r'.\reports\data_quality\run_date=2026-05-23\raw_quality_checks.csv'); print(df[df['failed_count'] > 0][['status','rule_id','source_file','failed_count','total_count','message']].to_string(index=False))"
Empty DataFrame

# which checks passed
which checks failed
which failures are acceptable
which failures need cleaning
which rules may need adjustment

# Raw Data Quality Findings

## Purpose

This document summarizes the first automated raw data quality check results for the Olist source files in the Retail Analytics Data Platform project.

The goal of this review is to understand whether the raw data passes the first version of automated quality checks before moving into cleaning, standardization, PostgreSQL loading, and later modeling.

This is part of the production-style workflow for the project:

1. inspect raw files
2. profile raw columns
3. review profiling findings
4. run automated quality checks
5. define cleaning and standardization rules
6. load and model the data

---

## Source

| Item | Value |
|---|---|
| Project | Retail Analytics Data Platform |
| Source | Olist Brazilian E-Commerce Dataset |
| Source type | CSV |
| Raw data location | `data/raw/olist/` |
| Quality report | `reports/data_quality/run_date=2026-05-23/raw_quality_checks.csv` |
| Review date | 2026-05-23 |
| Review status | Completed |

---

## Quality Check Summary

The automated raw data quality job was executed successfully.

Result summary:

| status | check_count |
|---|---:|
| PASS | 81 |
| FAIL | 0 |

Total checks executed: **81**  
Total passed checks: **81**  
Total failed checks: **0**

No failed checks were returned by the current version of the raw quality rules.

---

## Checks Covered

The first version of the raw quality job checks the following areas:

- expected Olist source files exist
- required columns exist in each source file
- important identifier columns are not null
- selected numeric columns are non-negative
- selected timestamp columns are parseable
- selected categorical fields contain expected values

These checks are intentionally practical and focused on early pipeline safety.

They are not a complete enterprise data quality framework yet. They are the first useful version of automated checks for the local pipeline.

---

## Checks Passed

All implemented checks passed.

This means:

- all expected Olist CSV files were found
- required columns were present in the source files
- important identifier columns passed the not-null checks
- selected numeric fields did not contain negative or invalid values
- selected timestamp fields were parseable
- selected categorical values matched the expected values
- no critical issue was detected by the current rule set

This gives enough confidence to continue to the next project step: defining cleaning and standardization rules.

---

## Failed Checks

No failed checks were found.

The failed-check query returned an empty result:

| rule_id | source_file | column_name | rule_type | severity | failed_count | total_count | message |
|---|---|---|---|---|---:|---:|---|
| No failed checks |  |  |  |  | 0 | 81 | All current checks passed |

---

## Important Interpretation

The result does **not** mean the raw data is perfect.

It means the raw data passed the first version of automated quality rules.

There may still be data issues that are not covered yet, such as:

- business-specific inconsistencies
- optional null values that need documentation
- duplicate business records
- unrealistic numeric values
- lifecycle inconsistencies between order status and timestamps
- relationship issues between files
- city or category name standardization issues
- future schema drift from source changes

The current rule set is useful, but it should grow as the project becomes more mature.

---

## Acceptable Failures

There are no failed checks in the current run.

However, based on the earlier profiling review, some nulls may still be business-acceptable and should remain documented, especially:

- missing review comment titles
- missing review comment messages
- missing lifecycle timestamps for canceled or unavailable orders
- optional product descriptive fields

These are not treated as failures in the current quality check version unless they affect critical pipeline logic.

---

## Failures That Need Cleaning

No failures were detected by the current automated rules.

However, cleaning and standardization are still required because passing raw quality checks does not replace transformation work.

The next cleaning step should still handle:

- parsing timestamp columns into proper datetime fields
- standardizing numeric columns
- trimming and standardizing text fields where needed
- preserving raw data unchanged
- adding ingestion metadata
- preparing data for PostgreSQL loading
- documenting business assumptions

---

## Rules That May Need Future Improvement

The first version of the quality rules is intentionally simple. Later versions should become more business-aware.

Future rule improvements may include:

| area | future improvement |
|---|---|
| order lifecycle | Check that delivered orders have delivery timestamps |
| order lifecycle | Allow missing delivery timestamps for canceled or unavailable orders |
| relationships | Check that `orders.customer_id` exists in the customers file |
| relationships | Check that `order_items.product_id` exists in the products file |
| relationships | Check that `order_items.seller_id` exists in the sellers file |
| uniqueness | Check uniqueness of primary-key-like columns where appropriate |
| duplicates | Detect fully duplicated rows |
| numeric values | Check unrealistic values, not only negative values |
| dates | Check whether delivery dates happen after purchase dates |
| categories | Monitor unexpected new order statuses or payment types |

Example of a better future rule:

```text
If order_status = 'delivered',
then order_delivered_customer_date should not be null.