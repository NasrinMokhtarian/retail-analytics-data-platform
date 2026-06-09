-- ============================================================
-- the first mart views will be:
-- mart.dim.customers
-- mart.dim_products
-- mart.dim.sellers
-- mart.dim.date  we will leave it for a separate step because it needs generated date logic.
-- mart.fact.orders
-- mart.fact.payments
-- mart.fact.reviews
-- mart.fact.order_items
-- mart.fact.suppliers_product_ipdates

-- ============================================================
-- Retail Analytics Data Platform
-- Create First Mart Views
--
-- Purpose:
-- Create business-facing analytical views from staging views.
--
-- Layer:
-- staging = typed and standardized SQL layer
-- mart    = business-friendly analytical layer
-- ============================================================


-- ============================================================
-- Dimension: Customers
-- Grain: one row per customer_id
-- ============================================================
CREATE OR REPLACE VIEW mart.dim_customers AS
SELECT customer_id, customer_unique_id,customer_zip_code_prefix, customer_city, customer_state, source_file_name,ingested_at,run_date
FROM staging.stg_customers;

-- ============================================================
-- Dimension: Products
-- Grain: one row per product_id
-- ============================================================
CREATE OR REPLACE VIEW mart.dim_products AS
SELECT p.product_id,p.product_category_name,COALESCE(t.product_category_name_english,p.product_category_name) AS product_category_name_english,
p.product_name_lenght AS product_name_length, p.product_description_lenght AS product_description_length,
p.product_photos_qty, p.product_weight_g, p.product_length_cm, p.product_height_cm, p.product_width_cm,
p.source_file_name, p.ingested_at, p.run_date
FROM staging.stg_products AS p LEFT JOIN staging.stg_product_category_translation AS t
on p.product_category_name = t.product_category_name;
-- ============================================================
-- Dimension: Sellers
-- Grain: one row per seller_id
-- ============================================================
CREATE OR REPLACE VIEW mart.dim_sellers AS
SELECT seller_id, seller_zip_code_prefix,seller_city,seller_state, source_file_name, ingested_at, run_date
FROM staging.stg_sellers;

-- ============================================================
-- Fact: Orders
-- Grain: one row per order_id
-- ============================================================
CREATE OR REPLACE VIEW mart.fct_orders AS
SELECT order_id, customer_id,order_status, order_purchase_timestamp, order_purchase_timestamp :: date AS order_purchase_date,order_approved_at,
    order_delivered_carrier_date,order_delivered_customer_date,order_estimated_delivery_date,
    CASE WHEN order_status = 'delivered' THEN TRUE ELSE FALSE END AS is_delivered,
    CASE WHEN order_purchase_timestamp IS NOT NULL and order_delivered_customer_date IS NOT NULL THEN DATE_PART('day',order_delivered_customer_date-order_purchase_timestamp)::integer ELSE NULL END AS days_to_customer_delivery,
    CASE WHEN order_delivered_customer_date IS NOT NULL and order_estimated_delivery_date IS NOT NULL and order_delivered_customer_date>order_estimated_delivery_date THEN TRUE
        WHEN order_estimated_delivery_date IS NOT NULL and order_delivered_customer_date IS NOT NULL THEN FALSE ELSE NULL
        END AS is_late_delivery,
   source_file_name,
    ingested_at,
    run_date
FROM staging.stg_orders;   

-- ============================================================
-- Fact: Order Items
-- Grain: one row per order_id + order_item_id
-- ============================================================

CREATE OR REPLACE VIEW mart.fct_order_items AS
SELECT
    order_id,
    order_item_id,
    product_id,
    seller_id,

    shipping_limit_date,
    price,
    freight_value,

    price + freight_value AS total_item_value,

    source_file_name,
    ingested_at,
    run_date
FROM staging.stg_order_items;

-- ============================================================
-- Fact: Payments
-- Grain: one row per order_id + payment_sequential
-- ============================================================

CREATE OR REPLACE VIEW mart.fct_payments AS
SELECT
    order_id,
    payment_sequential,
    payment_type,
    payment_installments,
    payment_value,

    source_file_name,
    ingested_at,
    run_date
FROM staging.stg_order_payments;

-- ============================================================
-- Fact: Reviews
-- Grain: one row per review_id
-- ============================================================

CREATE OR REPLACE VIEW mart.fct_reviews AS
SELECT
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,

    review_creation_date,
    review_answer_timestamp,

    review_creation_date::date AS review_creation_day,

    CASE
        WHEN review_score >= 4 THEN 'positive'
        WHEN review_score = 3 THEN 'neutral'
        WHEN review_score <= 2 THEN 'negative'
        ELSE 'unknown'
    END AS review_sentiment_group,

    source_file_name,
    ingested_at,
    run_date
FROM staging.stg_order_reviews;

-- ============================================================
-- Fact: Supplier Product Updates
-- Grain: one row per supplier product update record
-- ============================================================

CREATE OR REPLACE VIEW mart.fct_supplier_product_updates AS
SELECT
    supplier_id,
    supplier_name,
    product_id,
    supplier_product_code,

    updated_price,
    currency,
    stock_status,
    valid_from,
    last_updated_at,

    comments,

    has_missing_product_id,
    has_missing_currency,
    has_invalid_price,
    has_negative_price,
    has_unknown_stock_status,
    has_missing_valid_from,
    has_invalid_valid_from,
    has_invalid_last_updated_at,
    is_duplicate_business_key,

    CASE
        WHEN has_missing_product_id
          OR has_missing_currency
          OR has_invalid_price
          OR has_negative_price
          OR has_unknown_stock_status
          OR has_missing_valid_from
          OR has_invalid_valid_from
          OR has_invalid_last_updated_at
          OR is_duplicate_business_key
        THEN TRUE
        ELSE FALSE
    END AS needs_business_review,

    source_file_name,
    ingested_at,
    run_date
FROM staging.stg_supplier_product_updates;



-- ============================================================
-- Verify mart views exist
-- ============================================================

SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'mart'
ORDER BY table_name;
-- ============================================================
--Check row counts
-- ============================================================
SELECT 'mart.dim_customers' AS view_name, COUNT(*) AS row_count FROM mart.dim_customers
UNION ALL
SELECT 'mart.dim_products', COUNT(*) FROM mart.dim_products
UNION ALL
SELECT 'mart.dim_sellers', COUNT(*) FROM mart.dim_sellers
UNION ALL
SELECT 'mart.fct_orders', COUNT(*) FROM mart.fct_orders
UNION ALL
SELECT 'mart.fct_order_items', COUNT(*) FROM mart.fct_order_items
UNION ALL
SELECT 'mart.fct_payments', COUNT(*) FROM mart.fct_payments
UNION ALL
SELECT 'mart.fct_reviews', COUNT(*) FROM mart.fct_reviews
UNION ALL
SELECT 'mart.fct_supplier_product_updates', COUNT(*) FROM mart.fct_supplier_product_updates
ORDER BY view_name;

-- ============================================================
-- Test business-ready fields
-- ============================================================

SELECT
    order_id,
    order_status,
    order_purchase_date,
    is_delivered,
    days_to_customer_delivery,
    delivery_delay_days,
    is_late_delivery
FROM mart.fct_orders
LIMIT 20;

SELECT
    order_id,
    order_item_id,
    price,
    freight_value,
    total_item_value
FROM mart.fct_order_items
LIMIT 20;

SELECT
    review_score,
    review_sentiment_group,
    COUNT(*) AS review_count
FROM mart.fct_reviews
GROUP BY review_score, review_sentiment_group
ORDER BY review_score;

SELECT
    supplier_id,
    supplier_name,
    product_id,
    updated_price,
    currency,
    stock_status,
    needs_business_review
FROM mart.fct_supplier_product_updates
WHERE needs_business_review = TRUE
ORDER BY supplier_id;