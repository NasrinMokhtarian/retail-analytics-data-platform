# PostgreSQL Staging Layer Design

## Purpose

This document defines the design for the PostgreSQL staging layer in the Retail Analytics Data Platform project.

The staging layer prepares raw loaded database tables for analytical modeling.

It is not the final business reporting layer.  
It is the SQL transformation layer where raw data becomes cleaner, typed, standardized, and easier to join.

---

## Current Context

The project currently has cleaned and validated local files loaded into PostgreSQL under the `raw` schema.

Current raw sources:

- Olist e-commerce data
- Handmade supplier product updates

Current database schemas:

| schema | purpose |
|---|---|
| raw | Source-like loaded tables |
| staging | Cleaned and standardized SQL transformation layer |
| mart | Business-ready analytical tables later |
| audit | Load tracking and pipeline metadata |

---

## Staging Layer Goals

The staging layer should:

- keep one staging object per important raw source table
- cast date/time fields to proper timestamp/date types
- cast numeric fields to numeric types
- standardize important text fields where needed
- preserve business keys used for joins
- keep useful metadata columns
- avoid complex business metrics too early
- prepare data for later fact and dimension models

---

## Design Decision: Use Views First

The first version of the staging layer will use PostgreSQL views.

Reason:

- views are easy to inspect
- views avoid unnecessary data duplication
- views are easy to change during learning
- views prepare the project for dbt models later

Later, staging views can be migrated to dbt models.

---

## Naming Convention

Staging objects should use the prefix `stg_`.

Examples:

| raw table | staging view |
|---|---|
| raw.olist_orders | staging.stg_orders |
| raw.olist_customers | staging.stg_customers |
| raw.olist_order_items | staging.stg_order_items |
| raw.olist_products | staging.stg_products |
| raw.supplier_product_updates | staging.stg_supplier_product_updates |

---

## Planned Staging Views

### Olist staging views

| staging view | source table | purpose |
|---|---|---|
| staging.stg_customers | raw.olist_customers | Customer identifiers and geography |
| staging.stg_geolocation | raw.olist_geolocation | Zip-code geolocation reference |
| staging.stg_orders | raw.olist_orders | Order lifecycle and timestamps |
| staging.stg_order_items | raw.olist_order_items | Item-level order, product, seller, price data |
| staging.stg_order_payments | raw.olist_order_payments | Payment records |
| staging.stg_order_reviews | raw.olist_order_reviews | Review scores and comments |
| staging.stg_products | raw.olist_products | Product attributes and category |
| staging.stg_sellers | raw.olist_sellers | Seller identifiers and geography |
| staging.stg_product_category_translation | raw.product_category_translation | Product category English translation |

### Supplier staging view

| staging view | source table | purpose |
|---|---|---|
| staging.stg_supplier_product_updates | raw.supplier_product_updates | Standardized supplier price/status update data with quality flags |

---

## General Staging Rules

| rule_id | rule | description |
|---|---|---|
| STG001 | Keep business keys | Preserve IDs used for joins |
| STG002 | Cast timestamps | Convert timestamp fields to timestamp type |
| STG003 | Cast numeric fields | Convert price, freight, payment, weight, and size fields to numeric |
| STG004 | Standardize simple text | Trim and standardize important categorical fields where useful |
| STG005 | Preserve metadata | Keep `source_file_name`, `ingested_at`, and `run_date` |
| STG006 | Avoid heavy business logic | Keep complex metrics for mart layer |
| STG007 | Do not remove records silently | Filtering should be explicit and documented |

---

## Orders Staging Design

Source:

`raw.olist_orders`

Target:

`staging.stg_orders`

Important columns:

| column | target treatment |
|---|---|
| order_id | text |
| customer_id | text |
| order_status | text |
| order_purchase_timestamp | timestamp |
| order_approved_at | timestamp |
| order_delivered_carrier_date | timestamp |
| order_delivered_customer_date | timestamp |
| order_estimated_delivery_date | timestamp |
| source_file_name | text |
| ingested_at | timestamp |
| run_date | date |

Business purpose:

Orders are central to the project.  
This table will support order volume, delivery, customer, and revenue analysis.

---

## Order Items Staging Design

Source:

`raw.olist_order_items`

Target:

`staging.stg_order_items`

Important columns:

| column | target treatment |
|---|---|
| order_id | text |
| order_item_id | integer |
| product_id | text |
| seller_id | text |
| shipping_limit_date | timestamp |
| price | numeric |
| freight_value | numeric |
| source_file_name | text |
| ingested_at | timestamp |
| run_date | date |

Business purpose:

Order items are item-level transaction records.  
This table will support revenue, product, and seller analysis.

---

## Customers Staging Design

Source:

`raw.olist_customers`

Target:

`staging.stg_customers`

Important columns:

| column | target treatment |
|---|---|
| customer_id | text |
| customer_unique_id | text |
| customer_zip_code_prefix | text |
| customer_city | text |
| customer_state | text |
| source_file_name | text |
| ingested_at | timestamp |
| run_date | date |

Business purpose:

Customers support geographic and customer-level analysis.

---

## Products Staging Design

Source:

`raw.olist_products`

Target:

`staging.stg_products`

Important columns:

| column | target treatment |
|---|---|
| product_id | text |
| product_category_name | text |
| product_name_lenght | integer/numeric |
| product_description_lenght | integer/numeric |
| product_photos_qty | integer/numeric |
| product_weight_g | numeric |
| product_length_cm | numeric |
| product_height_cm | numeric |
| product_width_cm | numeric |
| source_file_name | text |
| ingested_at | timestamp |
| run_date | date |

Note:

The source column names `product_name_lenght` and `product_description_lenght` contain spelling mistakes from the original dataset.

First staging version will keep original names for traceability.  
Later mart models may rename them to business-friendly names.

---

## Payments Staging Design

Source:

`raw.olist_order_payments`

Target:

`staging.stg_order_payments`

Important columns:

| column | target treatment |
|---|---|
| order_id | text |
| payment_sequential | integer |
| payment_type | text |
| payment_installments | integer |
| payment_value | numeric |
| source_file_name | text |
| ingested_at | timestamp |
| run_date | date |

Business purpose:

Payments support payment behavior and total payment value analysis.

---

## Reviews Staging Design

Source:

`raw.olist_order_reviews`

Target:

`staging.stg_order_reviews`

Important columns:

| column | target treatment |
|---|---|
| review_id | text |
| order_id | text |
| review_score | integer |
| review_comment_title | text |
| review_comment_message | text |
| review_creation_date | timestamp |
| review_answer_timestamp | timestamp |
| source_file_name | text |
| ingested_at | timestamp |
| run_date | date |

Business purpose:

Reviews support customer satisfaction and delivery-performance analysis.

---

## Sellers Staging Design

Source:

`raw.olist_sellers`

Target:

`staging.stg_sellers`

Important columns:

| column | target treatment |
|---|---|
| seller_id | text |
| seller_zip_code_prefix | text |
| seller_city | text |
| seller_state | text |
| source_file_name | text |
| ingested_at | timestamp |
| run_date | date |

Business purpose:

Sellers support seller performance and geography analysis.

---

## Product Category Translation Staging Design

Source:

`raw.product_category_translation`

Target:

`staging.stg_product_category_translation`

Important columns:

| column | target treatment |
|---|---|
| product_category_name | text |
| product_category_name_english | text |
| source_file_name | text |
| ingested_at | timestamp |
| run_date | date |

Business purpose:

This table supports English product category reporting.

---

## Supplier Product Updates Staging Design

Source:

`raw.supplier_product_updates`

Target:

`staging.stg_supplier_product_updates`

Important columns:

| column | target treatment |
|---|---|
| supplier_id | text |
| supplier_name | text |
| product_id | text |
| supplier_product_code | text |
| updated_price_clean | numeric |
| currency_clean | text |
| stock_status_clean | text |
| valid_from_clean | date |
| last_updated_at_clean | timestamp |
| quality flag columns | boolean |
| source_file_name | text |
| ingested_at | timestamp |
| run_date | date |

Business purpose:

Supplier updates simulate a real messy business source.  
This staging view should expose standardized price, currency, stock status, dates, and quality flags.

---

## What Should Not Happen in Staging Yet

The staging layer should not yet:

- calculate final revenue metrics
- build customer dimensions
- build product dimensions
- aggregate payments
- calculate delivery delay metrics
- remove records without documentation
- hide supplier quality issues

Those belong later in mart or business models.

---

## Future dbt Direction

Later, these PostgreSQL staging views can become dbt models such as:

```text
models/staging/stg_orders.sql
models/staging/stg_order_items.sql
models/staging/stg_customers.sql
models/staging/stg_supplier_product_updates.sql