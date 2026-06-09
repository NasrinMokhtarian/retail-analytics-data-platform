# Mart Validation Findings

## Purpose

This document summarizes the validation review of the PostgreSQL mart layer for the Retail Analytics Data Platform project.

The goal is to confirm whether the mart views are reliable enough for business analysis and later BI reporting.

Validation SQL:

`sql/mart/02_validate_mart_views.sql`

---

## Current Context

The project currently has:

* validated local cleaned files
* PostgreSQL raw tables
* PostgreSQL staging views
* PostgreSQL mart views
* audit logging
* validation queries for raw, staging, and mart layers

The mart layer is the first business-facing analytical layer.

---

## Mart Views Reviewed

| mart view                         | type      | grain                                      |
| --------------------------------- | --------- | ------------------------------------------ |
| mart.dim_customers                | dimension | one row per customer_id                    |
| mart.dim_products                 | dimension | one row per product_id                     |
| mart.dim_sellers                  | dimension | one row per seller_id                      |
| mart.fct_orders                   | fact      | one row per order_id                       |
| mart.fct_order_items              | fact      | one row per order_id + order_item_id       |
| mart.fct_payments                 | fact      | one row per order_id + payment_sequential  |
| mart.fct_reviews                  | fact      | one row per review_id                      |
| mart.fct_supplier_product_updates | fact      | one row per supplier product update record |

---

## Validation Areas

The mart validation covered:

* mart view existence
* row counts
* dimension grain uniqueness
* fact grain uniqueness
* important ID not-null checks
* revenue and payment measure checks
* delivery metric checks
* review sentiment grouping
* supplier review flag logic
* fact-to-dimension join readiness
* first business-ready queries

---

## Grain Validation

Dimension and fact grains were checked to reduce the risk of duplicate records and double counting.

Important grain checks included:

| mart object     | grain check                              |
| --------------- | ---------------------------------------- |
| dim_customers   | customer_id uniqueness                   |
| dim_products    | product_id uniqueness                    |
| dim_sellers     | seller_id uniqueness                     |
| fct_orders      | order_id uniqueness                      |
| fct_order_items | order_id + order_item_id uniqueness      |
| fct_payments    | order_id + payment_sequential uniqueness |
| fct_reviews     | review_id uniqueness                     |

Result:

The mart layer is suitable for first business analysis, assuming all duplicate-count checks returned expected results.

If any duplicate counts appear in future runs, they should be investigated before using the affected mart object for reporting.

---

## Important ID Validation

Important identifiers were checked for null values.

Examples:

* customer_id
* product_id
* seller_id
* order_id
* order_item_id

Result:

Core Olist identifiers are suitable for first analytical use.

These checks should later become dbt tests such as:

* not_null
* unique
* relationships

---

## Business Metric Validation

Important business metrics were reviewed.

Examples:

* item price
* freight value
* total item value
* payment value

Result:

Olist revenue and payment measures are suitable for first business analysis.

The mart layer now exposes useful business fields such as:

* total_item_value
* delivery_delay_days
* is_late_delivery
* review_sentiment_group
* needs_business_review

---

## Delivery Metric Validation

Delivery metrics were reviewed in `mart.fct_orders`.

Important fields:

* days_to_customer_delivery
* delivery_delay_days
* is_late_delivery

Observation:

* `delivery_delay_days` can be negative when an order was delivered earlier than estimated.
* delivery metrics should only be interpreted when relevant timestamps are available.
* delivered orders without delivery timestamps should be investigated if they appear.

Modeling implication:

Delivery performance analysis should filter carefully for delivered orders and available timestamps.

---

## Review Sentiment Validation

Review scores were grouped into sentiment categories:

| review_score | sentiment group |
| ------------ | --------------- |
| 4–5          | positive        |
| 3            | neutral         |
| 1–2          | negative        |

Result:

The review sentiment grouping is useful for first-level business analysis.

Future analysis can connect review sentiment with:

* delivery delay
* seller performance
* product category
* customer geography

---

## Supplier Review Flag Validation

The supplier mart includes a combined flag:

`needs_business_review`

This flag becomes true when any supplier quality issue exists.

Quality flags include:

* has_missing_product_id
* has_missing_currency
* has_invalid_price
* has_negative_price
* has_unknown_stock_status
* has_missing_valid_from
* has_invalid_valid_from
* has_invalid_last_updated_at
* is_duplicate_business_key

Result:

Supplier data quality issues remain visible in the mart layer.

This is important because supplier data should not be blindly used in final analysis without reviewing flagged records.

---

## Fact-to-Dimension Join Readiness

The following joins were reviewed:

| fact                         | dimension     | join key    |
| ---------------------------- | ------------- | ----------- |
| fct_orders                   | dim_customers | customer_id |
| fct_order_items              | dim_products  | product_id  |
| fct_order_items              | dim_sellers   | seller_id   |
| fct_supplier_product_updates | dim_products  | product_id  |

Result:

The core Olist fact-to-dimension relationships are ready for first business analysis.

Supplier-to-product joins should be handled carefully because the supplier file intentionally contains missing or synthetic product IDs.

---

## Business-Ready Queries Confirmed

The mart layer supports first business-ready queries such as:

* revenue by product category
* delivery performance by late-delivery flag
* supplier rows needing business review
* review sentiment distribution
* item-level revenue analysis

This confirms that the mart layer is ready for deeper SQL business analysis.

---

## Modeling Risks to Remember

The following risks should be kept visible:

| risk                    | explanation                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| Double counting         | Joining order-level and item-level facts incorrectly can inflate metrics |
| Multiple payments       | Some orders may have multiple payment records                            |
| Optional timestamps     | Some order lifecycle timestamps are legitimately null                    |
| Supplier quality issues | Supplier rows with quality flags should not be blindly trusted           |
| Product category gaps   | Some products may have missing or untranslated categories                |

---

## What Should Move to dbt Later

The following should become dbt models and tests later:

* staging views
* mart views
* not_null tests
* unique tests
* relationship tests
* accepted value tests
* numeric validity checks
* supplier quality tests
* documentation and lineage

The current PostgreSQL SQL files are the first validated modeling prototype.

dbt will later formalize this logic.

---

## Decision

The mart layer is ready for first business analysis.

The next step is:

`Step 2.17 — Business Analysis Queries from Mart Layer`

The business analysis should focus on practical portfolio questions:

* monthly revenue
* top product categories
* customer geography
* seller performance
* delivery delay
* review scores
* supplier records needing review
