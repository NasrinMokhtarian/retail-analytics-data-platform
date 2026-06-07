Summarize whether the staging layer is ready for fact/dimension modeling.

# Staging Validation Findings

## Purpose

This document summarizes the validation review of the PostgreSQL staging layer for the Retail Analytics Data Platform project.

The goal is to confirm whether the staging views are ready to support the first analytical mart design.

---

## Current Context

The project currently has:

- cleaned and validated local source files
- PostgreSQL raw tables
- PostgreSQL staging views
- staging validation SQL queries

The staging layer is built from the raw PostgreSQL tables and prepares the data for later fact and dimension models.

Validation SQL:

`sql/staging/02_validate_staging_views.sql`

---

## Staging Views Reviewed

The following staging views were reviewed:

| staging view | source table |
|---|---|
| staging.stg_customers | raw.olist_customers |
| staging.stg_geolocation | raw.olist_geolocation |
| staging.stg_orders | raw.olist_orders |
| staging.stg_order_items | raw.olist_order_items |
| staging.stg_order_payments | raw.olist_order_payments |
| staging.stg_order_reviews | raw.olist_order_reviews |
| staging.stg_products | raw.olist_products |
| staging.stg_sellers | raw.olist_sellers |
| staging.stg_product_category_translation | raw.product_category_translation |
| staging.stg_supplier_product_updates | raw.supplier_product_updates |

---

## Row Count Validation

Raw and staging row counts were compared for each source entity.

Result:

- staging views preserve the same row counts as the corresponding raw tables
- no unexpected row loss was identified during staging transformation

This is important because the first staging layer should standardize types and fields without silently filtering records.

---

## Key Column Validation

Important identifier columns were checked for null values.

Examples reviewed:

- orders.order_id
- orders.customer_id
- customers.customer_id
- order_items.order_id
- order_items.product_id
- order_items.seller_id
- products.product_id
- sellers.seller_id

Result:

- key columns are suitable for later relationship checks and modeling
- important join keys are preserved in the staging layer

Future dbt tests should include `not_null` checks for these key columns.

---

## Numeric Field Validation

Important numeric fields were checked for negative values.

Examples reviewed:

- order item price
- freight value
- payment value
- product weight
- product length
- product height
- product width

Result:

- Olist numeric business fields are suitable for first-stage analytical modeling
- numeric fields have been cast in staging views and can be used directly in SQL queries

Future dbt tests should include numeric validity checks where appropriate.

---

## Timestamp Validation

Order timestamp fields were reviewed by order status.

Important fields:

- order_purchase_timestamp
- order_approved_at
- order_delivered_carrier_date
- order_delivered_customer_date
- order_estimated_delivery_date

Observation:

- some lifecycle timestamps may be null depending on order status
- this is expected for canceled, unavailable, or undelivered orders
- delivered orders should be reviewed carefully if delivery timestamps are missing

Modeling implication:

- delivery delay calculations should only be performed where the required delivery timestamps are available
- lifecycle timestamp rules should become business-aware checks later

Example future rule:

```text
If order_status = 'delivered',
then order_delivered_customer_date should not be null.