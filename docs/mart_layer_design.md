# Mart Layer Design

## Purpose

This document defines the first analytical mart layer for the Retail Analytics Data Platform project.

The mart layer turns cleaned and staged data into business-friendly analytical structures.

The goal is to support practical business questions such as:

* What is monthly revenue?
* Which product categories generate the most revenue?
* Which customer states have the highest order volume?
* Which sellers generate the most sales?
* How do delivery delays relate to review scores?
* Which supplier product updates need business review?

The mart layer should be simple, understandable, and useful for SQL analysis, BI reporting, and later dbt modeling.

---

## Current Context

The project currently has:

* local raw and processed file zones
* Olist source onboarding
* supplier source onboarding
* PostgreSQL raw tables
* PostgreSQL staging views
* staging validation queries

Current database layers:

| schema  | purpose                                 |
| ------- | --------------------------------------- |
| raw     | Loaded source-like PostgreSQL tables    |
| staging | Typed and standardized SQL views        |
| mart    | Business-facing analytical tables/views |
| audit   | Load tracking and pipeline metadata     |

The next step is to design the first mart objects.

---

## Mart Layer Principles

The first mart version should follow these principles:

* use staging views as input
* keep business logic readable
* define clear table grain
* avoid overengineering
* start with practical business questions
* preserve important identifiers for traceability
* separate facts from dimensions
* document assumptions
* build incrementally

The mart layer should not try to solve every possible business question at once.

---

## Key Concept: Fact and Dimension Tables

### Fact Tables

Fact tables represent business events or measurable activities.

Examples:

* an order
* an order item
* a payment
* a review
* a supplier product update

Fact tables usually contain:

* foreign keys
* dates
* measurable values
* status fields
* business metrics

### Dimension Tables

Dimension tables describe business entities.

Examples:

* customer
* product
* seller
* date

Dimension tables usually contain:

* descriptive attributes
* geography
* category
* names or classifications

---

## Planned First Mart Objects

The first mart layer will contain:

| mart object                       | type      | purpose                                          |
| --------------------------------- | --------- | ------------------------------------------------ |
| mart.dim_customers                | dimension | Customer identity and geography                  |
| mart.dim_products                 | dimension | Product attributes and translated category       |
| mart.dim_sellers                  | dimension | Seller identity and geography                    |
| mart.dim_dates                    | dimension | Calendar/date analysis                           |
| mart.fct_orders                   | fact      | Order-level lifecycle and customer relationship  |
| mart.fct_order_items              | fact      | Item-level revenue, product, and seller analysis |
| mart.fct_payments                 | fact      | Payment behavior and payment value               |
| mart.fct_reviews                  | fact      | Review scores and review timing                  |
| mart.fct_supplier_product_updates | fact      | Supplier update records with quality flags       |

---

## Grain Definition

Grain means: **what one row represents**.

This is one of the most important mart design decisions.

| mart object                       | grain                                      |
| --------------------------------- | ------------------------------------------ |
| mart.dim_customers                | one row per customer_id                    |
| mart.dim_products                 | one row per product_id                     |
| mart.dim_sellers                  | one row per seller_id                      |
| mart.dim_dates                    | one row per calendar date                  |
| mart.fct_orders                   | one row per order_id                       |
| mart.fct_order_items              | one row per order_id + order_item_id       |
| mart.fct_payments                 | one row per order_id + payment_sequential  |
| mart.fct_reviews                  | one row per review_id                      |
| mart.fct_supplier_product_updates | one row per supplier product update record |

The grain must stay clear to avoid double counting.

---

## Dimension Design

## mart.dim_customers

Source:

`staging.stg_customers`

Grain:

One row per `customer_id`.

Purpose:

Support customer geography and order analysis.

Planned columns:

| column                   | description                        |
| ------------------------ | ---------------------------------- |
| customer_id              | Customer identifier used in orders |
| customer_unique_id       | Unique customer identity           |
| customer_zip_code_prefix | Customer zip code prefix           |
| customer_city            | Customer city                      |
| customer_state           | Customer state                     |
| source_file_name         | Source traceability                |
| ingested_at              | Ingestion timestamp                |
| run_date                 | Pipeline run date                  |

Business use cases:

* orders by customer state
* customers by city
* geographic sales analysis

---

## mart.dim_products

Sources:

* `staging.stg_products`
* `staging.stg_product_category_translation`

Grain:

One row per `product_id`.

Purpose:

Support product and category analysis.

Planned columns:

| column                        | description                             |
| ----------------------------- | --------------------------------------- |
| product_id                    | Product identifier                      |
| product_category_name         | Original product category               |
| product_category_name_english | English product category                |
| product_name_lenght           | Source product name length field        |
| product_description_lenght    | Source product description length field |
| product_photos_qty            | Number of product photos                |
| product_weight_g              | Product weight                          |
| product_length_cm             | Product length                          |
| product_height_cm             | Product height                          |
| product_width_cm              | Product width                           |
| source_file_name              | Source traceability                     |
| ingested_at                   | Ingestion timestamp                     |
| run_date                      | Pipeline run date                       |

Business use cases:

* revenue by product category
* product catalog quality analysis
* category-level performance

Note:

The source column names `product_name_lenght` and `product_description_lenght` contain spelling mistakes.
The first mart version may keep them for traceability or later rename them to:

* product_name_length
* product_description_length

This decision can be made during implementation.

---

## mart.dim_sellers

Source:

`staging.stg_sellers`

Grain:

One row per `seller_id`.

Purpose:

Support seller performance and geography analysis.

Planned columns:

| column                 | description            |
| ---------------------- | ---------------------- |
| seller_id              | Seller identifier      |
| seller_zip_code_prefix | Seller zip code prefix |
| seller_city            | Seller city            |
| seller_state           | Seller state           |
| source_file_name       | Source traceability    |
| ingested_at            | Ingestion timestamp    |
| run_date               | Pipeline run date      |

Business use cases:

* revenue by seller
* seller performance by state
* seller delivery analysis

---

## mart.dim_dates

Source:

Generated from important business dates, mainly order purchase dates.

Grain:

One row per calendar date.

Purpose:

Support time-based reporting.

Planned columns:

| column        | description                    |
| ------------- | ------------------------------ |
| date_id       | Date key, for example YYYYMMDD |
| calendar_date | Actual date                    |
| year          | Calendar year                  |
| quarter       | Calendar quarter               |
| month         | Month number                   |
| month_name    | Month name                     |
| day           | Day of month                   |
| day_of_week   | Day of week number             |
| day_name      | Day name                       |
| is_weekend    | Weekend flag                   |

Business use cases:

* monthly revenue
* yearly order trends
* weekday/weekend analysis
* date filtering in BI tools

---

## Fact Table Design

## mart.fct_orders

Source:

`staging.stg_orders`

Grain:

One row per `order_id`.

Purpose:

Represent order-level lifecycle and customer relationship.

Planned columns:

| column                        | description                                      |
| ----------------------------- | ------------------------------------------------ |
| order_id                      | Order identifier                                 |
| customer_id                   | Customer identifier                              |
| order_status                  | Order lifecycle status                           |
| order_purchase_timestamp      | Purchase timestamp                               |
| order_purchase_date           | Purchase date                                    |
| order_approved_at             | Approval timestamp                               |
| order_delivered_carrier_date  | Carrier delivery timestamp                       |
| order_delivered_customer_date | Customer delivery timestamp                      |
| order_estimated_delivery_date | Estimated delivery timestamp                     |
| days_to_customer_delivery     | Days between purchase and customer delivery      |
| delivery_delay_days           | Difference between actual and estimated delivery |
| is_delivered                  | Whether order status is delivered                |
| is_late_delivery              | Whether delivered after estimated date           |
| source_file_name              | Source traceability                              |
| ingested_at                   | Ingestion timestamp                              |
| run_date                      | Pipeline run date                                |

Business use cases:

* order volume by month
* delivery performance
* late delivery analysis
* customer order lifecycle analysis

Important rule:

Delivery metrics should only be calculated when the required timestamps are available.

---

## mart.fct_order_items

Source:

`staging.stg_order_items`

Grain:

One row per `order_id + order_item_id`.

Purpose:

Represent item-level sales activity.

Planned columns:

| column              | description                |
| ------------------- | -------------------------- |
| order_id            | Order identifier           |
| order_item_id       | Item sequence within order |
| product_id          | Product identifier         |
| seller_id           | Seller identifier          |
| shipping_limit_date | Seller shipping limit      |
| price               | Item price                 |
| freight_value       | Freight value              |
| total_item_value    | price + freight_value      |
| source_file_name    | Source traceability        |
| ingested_at         | Ingestion timestamp        |
| run_date            | Pipeline run date          |

Business use cases:

* item revenue
* revenue by product
* revenue by seller
* freight cost analysis

Important warning:

Order item facts can cause double counting if joined incorrectly with order-level facts.
The grain must be respected.

---

## mart.fct_payments

Source:

`staging.stg_order_payments`

Grain:

One row per `order_id + payment_sequential`.

Purpose:

Represent payment records.

Planned columns:

| column               | description            |
| -------------------- | ---------------------- |
| order_id             | Order identifier       |
| payment_sequential   | Payment sequence       |
| payment_type         | Payment method         |
| payment_installments | Number of installments |
| payment_value        | Payment value          |
| source_file_name     | Source traceability    |
| ingested_at          | Ingestion timestamp    |
| run_date             | Pipeline run date      |

Business use cases:

* payment type distribution
* payment value by method
* installment behavior

Important warning:

Some orders may have multiple payment records.
Payment metrics should be aggregated carefully at order level when needed.

---

## mart.fct_reviews

Source:

`staging.stg_order_reviews`

Grain:

One row per `review_id`.

Purpose:

Represent customer review activity.

Planned columns:

| column                  | description               |
| ----------------------- | ------------------------- |
| review_id               | Review identifier         |
| order_id                | Order identifier          |
| review_score            | Review score              |
| review_comment_title    | Review title              |
| review_comment_message  | Review message            |
| review_creation_date    | Review creation timestamp |
| review_answer_timestamp | Review answer timestamp   |
| source_file_name        | Source traceability       |
| ingested_at             | Ingestion timestamp       |
| run_date                | Pipeline run date         |

Business use cases:

* average review score
* review score by delivery delay
* review score by product category
* review score by seller

---

## mart.fct_supplier_product_updates

Source:

`staging.stg_supplier_product_updates`

Grain:

One row per supplier product update record.

Purpose:

Represent supplier-provided product update information.

Planned columns:

| column                      | description               |
| --------------------------- | ------------------------- |
| supplier_id                 | Supplier identifier       |
| supplier_name               | Supplier name             |
| product_id                  | Product identifier        |
| supplier_product_code       | Supplier product code     |
| updated_price               | Cleaned supplier price    |
| currency                    | Cleaned currency          |
| stock_status                | Cleaned stock status      |
| valid_from                  | Validity start date       |
| last_updated_at             | Supplier update timestamp |
| has_missing_product_id      | Quality flag              |
| has_missing_currency        | Quality flag              |
| has_invalid_price           | Quality flag              |
| has_negative_price          | Quality flag              |
| has_unknown_stock_status    | Quality flag              |
| has_missing_valid_from      | Quality flag              |
| has_invalid_valid_from      | Quality flag              |
| has_invalid_last_updated_at | Quality flag              |
| is_duplicate_business_key   | Quality flag              |
| needs_business_review       | Combined review flag      |
| source_file_name            | Source traceability       |
| ingested_at                 | Ingestion timestamp       |
| run_date                    | Pipeline run date         |

Business use cases:

* identify supplier rows needing review
* compare supplier updates with product catalog
* monitor supplier data quality
* prepare for future supplier/product integration

Important rule:

Supplier rows with critical flags should not be blindly used for final analytics.

---

## First Mart Implementation Order

The first implementation should be incremental.

Recommended order:

1. `mart.dim_customers`
2. `mart.dim_products`
3. `mart.dim_sellers`
4. `mart.fct_orders`
5. `mart.fct_order_items`
6. `mart.fct_payments`
7. `mart.fct_reviews`
8. `mart.fct_supplier_product_updates`
9. `mart.dim_dates`

Reason:

Start with direct staging-to-mart views before adding generated date logic.

---

## Mart Validation Expectations

After building marts, validate:

* mart objects exist
* row counts are reasonable
* primary key grain is respected
* important IDs are not null
* revenue values are non-negative
* delivery metrics are calculated only where valid
* supplier review flags are preserved
* joins between facts and dimensions work

---

## Future dbt Direction

Later, these mart views can become dbt models:

```text
models/marts/dim_customers.sql
models/marts/dim_products.sql
models/marts/dim_sellers.sql
models/marts/fct_orders.sql
models/marts/fct_order_items.sql
models/marts/fct_payments.sql
models/marts/fct_reviews.sql
models/marts/fct_supplier_product_updates.sql
```

dbt will later add:

* model documentation
* column documentation
* tests
* lineage
* dependency management
* materialization control

For now, PostgreSQL views are enough.

---

## Decision

The first mart layer will use PostgreSQL views.

This keeps the project simple, transparent, and easy to change while practicing analytical modeling.

The next step is:

`Step 2.14 — Create first mart views`
