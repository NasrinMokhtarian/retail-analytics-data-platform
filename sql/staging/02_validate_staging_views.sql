-- ============================================================
-- Retail Analytics Data Platform
-- Validate PostgreSQL Staging Views
--
-- Purpose:
-- Validate that staging views are complete, typed, and ready
-- for later mart/fact/dimension modeling.
-- ============================================================


-- ============================================================
-- 1. Check staging views exist
-- ============================================================

SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'staging'
ORDER BY table_name;


-- ============================================================
-- 2. Compare raw and staging row counts
-- ============================================================

SELECT
    'customers' AS entity,
    (SELECT COUNT(*) FROM raw.olist_customers) AS raw_row_count,
    (SELECT COUNT(*) FROM staging.stg_customers) AS staging_row_count
UNION ALL
SELECT
    'geolocation',
    (SELECT COUNT(*) FROM raw.olist_geolocation),
    (SELECT COUNT(*) FROM staging.stg_geolocation)
UNION ALL
SELECT
    'order_items',
    (SELECT COUNT(*) FROM raw.olist_order_items),
    (SELECT COUNT(*) FROM staging.stg_order_items)
UNION ALL
SELECT
    'order_payments',
    (SELECT COUNT(*) FROM raw.olist_order_payments),
    (SELECT COUNT(*) FROM staging.stg_order_payments)
UNION ALL
SELECT
    'order_reviews',
    (SELECT COUNT(*) FROM raw.olist_order_reviews),
    (SELECT COUNT(*) FROM staging.stg_order_reviews)
UNION ALL
SELECT
    'orders',
    (SELECT COUNT(*) FROM raw.olist_orders),
    (SELECT COUNT(*) FROM staging.stg_orders)
UNION ALL
SELECT
    'products',
    (SELECT COUNT(*) FROM raw.olist_products),
    (SELECT COUNT(*) FROM staging.stg_products)
UNION ALL
SELECT
    'sellers',
    (SELECT COUNT(*) FROM raw.olist_sellers),
    (SELECT COUNT(*) FROM staging.stg_sellers)
UNION ALL
SELECT
    'product_category_translation',
    (SELECT COUNT(*) FROM raw.product_category_translation),
    (SELECT COUNT(*) FROM staging.stg_product_category_translation)
UNION ALL
SELECT
    'supplier_product_updates',
    (SELECT COUNT(*) FROM raw.supplier_product_updates),
    (SELECT COUNT(*) FROM staging.stg_supplier_product_updates)
ORDER BY entity;


-- ============================================================
-- 3. Identify row-count mismatches
-- Expected result: zero rows
-- ============================================================

WITH row_count_check AS (
    SELECT
        'customers' AS entity,
        (SELECT COUNT(*) FROM raw.olist_customers) AS raw_row_count,
        (SELECT COUNT(*) FROM staging.stg_customers) AS staging_row_count
    UNION ALL
    SELECT
        'geolocation',
        (SELECT COUNT(*) FROM raw.olist_geolocation),
        (SELECT COUNT(*) FROM staging.stg_geolocation)
    UNION ALL
    SELECT
        'order_items',
        (SELECT COUNT(*) FROM raw.olist_order_items),
        (SELECT COUNT(*) FROM staging.stg_order_items)
    UNION ALL
    SELECT
        'order_payments',
        (SELECT COUNT(*) FROM raw.olist_order_payments),
        (SELECT COUNT(*) FROM staging.stg_order_payments)
    UNION ALL
    SELECT
        'order_reviews',
        (SELECT COUNT(*) FROM raw.olist_order_reviews),
        (SELECT COUNT(*) FROM staging.stg_order_reviews)
    UNION ALL
    SELECT
        'orders',
        (SELECT COUNT(*) FROM raw.olist_orders),
        (SELECT COUNT(*) FROM staging.stg_orders)
    UNION ALL
    SELECT
        'products',
        (SELECT COUNT(*) FROM raw.olist_products),
        (SELECT COUNT(*) FROM staging.stg_products)
    UNION ALL
    SELECT
        'sellers',
        (SELECT COUNT(*) FROM raw.olist_sellers),
        (SELECT COUNT(*) FROM staging.stg_sellers)
    UNION ALL
    SELECT
        'product_category_translation',
        (SELECT COUNT(*) FROM raw.product_category_translation),
        (SELECT COUNT(*) FROM staging.stg_product_category_translation)
    UNION ALL
    SELECT
        'supplier_product_updates',
        (SELECT COUNT(*) FROM raw.supplier_product_updates),
        (SELECT COUNT(*) FROM staging.stg_supplier_product_updates)
)
SELECT *
FROM row_count_check
WHERE raw_row_count <> staging_row_count;


-- ============================================================
-- 4. Check important not-null keys
-- ============================================================

SELECT
    'stg_orders.order_id' AS check_name,
    COUNT(*) AS null_count
FROM staging.stg_orders
WHERE order_id IS NULL

UNION ALL

SELECT
    'stg_orders.customer_id',
    COUNT(*)
FROM staging.stg_orders
WHERE customer_id IS NULL

UNION ALL

SELECT
    'stg_customers.customer_id',
    COUNT(*)
FROM staging.stg_customers
WHERE customer_id IS NULL

UNION ALL

SELECT
    'stg_order_items.order_id',
    COUNT(*)
FROM staging.stg_order_items
WHERE order_id IS NULL

UNION ALL

SELECT
    'stg_order_items.product_id',
    COUNT(*)
FROM staging.stg_order_items
WHERE product_id IS NULL

UNION ALL

SELECT
    'stg_order_items.seller_id',
    COUNT(*)
FROM staging.stg_order_items
WHERE seller_id IS NULL

UNION ALL

SELECT
    'stg_products.product_id',
    COUNT(*)
FROM staging.stg_products
WHERE product_id IS NULL

UNION ALL

SELECT
    'stg_sellers.seller_id',
    COUNT(*)
FROM staging.stg_sellers
WHERE seller_id IS NULL

ORDER BY check_name;


-- ============================================================
-- 5. Check numeric fields for negative values
-- Expected result: zero for Olist business measures
-- ============================================================

SELECT
    'stg_order_items.price' AS check_name,
    COUNT(*) AS negative_count
FROM staging.stg_order_items
WHERE price < 0

UNION ALL

SELECT
    'stg_order_items.freight_value',
    COUNT(*)
FROM staging.stg_order_items
WHERE freight_value < 0

UNION ALL

SELECT
    'stg_order_payments.payment_value',
    COUNT(*)
FROM staging.stg_order_payments
WHERE payment_value < 0

UNION ALL

SELECT
    'stg_products.product_weight_g',
    COUNT(*)
FROM staging.stg_products
WHERE product_weight_g < 0

UNION ALL

SELECT
    'stg_products.product_length_cm',
    COUNT(*)
FROM staging.stg_products
WHERE product_length_cm < 0

UNION ALL

SELECT
    'stg_products.product_height_cm',
    COUNT(*)
FROM staging.stg_products
WHERE product_height_cm < 0

UNION ALL

SELECT
    'stg_products.product_width_cm',
    COUNT(*)
FROM staging.stg_products
WHERE product_width_cm < 0

ORDER BY check_name;


-- ============================================================
-- 6. Check order timestamp availability
-- Some lifecycle timestamps can be null depending on order status.
-- ============================================================

SELECT
    order_status,
    COUNT(*) AS order_count,
    COUNT(order_purchase_timestamp) AS purchase_ts_count,
    COUNT(order_approved_at) AS approved_ts_count,
    COUNT(order_delivered_carrier_date) AS delivered_carrier_ts_count,
    COUNT(order_delivered_customer_date) AS delivered_customer_ts_count,
    COUNT(order_estimated_delivery_date) AS estimated_delivery_ts_count
FROM staging.stg_orders
GROUP BY order_status
ORDER BY order_count DESC;


-- ============================================================
-- 7. Check delivered orders missing delivered customer timestamp
-- Expected: ideally zero, but review if any exist.
-- ============================================================

SELECT
    COUNT(*) AS delivered_orders_missing_customer_delivery_date
FROM staging.stg_orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NULL;


-- ============================================================
-- 8. Check order date range
-- ============================================================

SELECT
    MIN(order_purchase_timestamp) AS first_order_purchase_timestamp,
    MAX(order_purchase_timestamp) AS last_order_purchase_timestamp
FROM staging.stg_orders;


-- ============================================================
-- 9. Check payment type distribution
-- ============================================================

SELECT
    payment_type,
    COUNT(*) AS payment_record_count,
    ROUND(SUM(payment_value), 2) AS total_payment_value
FROM staging.stg_order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;


-- ============================================================
-- 10. Check supplier quality flags
-- These should remain visible after staging.
-- ============================================================

SELECT
    COUNT(*) AS total_supplier_rows,
    SUM(CASE WHEN has_missing_product_id THEN 1 ELSE 0 END) AS missing_product_id_rows,
    SUM(CASE WHEN has_missing_currency THEN 1 ELSE 0 END) AS missing_currency_rows,
    SUM(CASE WHEN has_invalid_price THEN 1 ELSE 0 END) AS invalid_price_rows,
    SUM(CASE WHEN has_negative_price THEN 1 ELSE 0 END) AS negative_price_rows,
    SUM(CASE WHEN has_unknown_stock_status THEN 1 ELSE 0 END) AS unknown_stock_status_rows,
    SUM(CASE WHEN has_missing_valid_from THEN 1 ELSE 0 END) AS missing_valid_from_rows,
    SUM(CASE WHEN has_invalid_valid_from THEN 1 ELSE 0 END) AS invalid_valid_from_rows,
    SUM(CASE WHEN has_invalid_last_updated_at THEN 1 ELSE 0 END) AS invalid_last_updated_at_rows,
    SUM(CASE WHEN is_duplicate_business_key THEN 1 ELSE 0 END) AS duplicate_business_key_rows
FROM staging.stg_supplier_product_updates;


-- ============================================================
-- 11. Show supplier rows requiring review
-- ============================================================

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
    has_missing_product_id,
    has_missing_currency,
    has_invalid_price,
    has_negative_price,
    has_unknown_stock_status,
    has_missing_valid_from,
    has_invalid_valid_from,
    has_invalid_last_updated_at,
    is_duplicate_business_key
FROM staging.stg_supplier_product_updates
WHERE
    has_missing_product_id
    OR has_missing_currency
    OR has_invalid_price
    OR has_negative_price
    OR has_unknown_stock_status
    OR has_missing_valid_from
    OR has_invalid_valid_from
    OR has_invalid_last_updated_at
    OR is_duplicate_business_key
ORDER BY supplier_id;


-- ============================================================
-- 12. Check product category translation join readiness
-- This checks how many products can be translated into English.
-- ============================================================

SELECT
    COUNT(*) AS product_count,
    COUNT(t.product_category_name_english) AS translated_category_count,
    COUNT(*) - COUNT(t.product_category_name_english) AS untranslated_or_missing_category_count
FROM staging.stg_products AS p
LEFT JOIN staging.stg_product_category_translation AS t
    ON p.product_category_name = t.product_category_name;


-- ============================================================
-- 13. Check basic join readiness between core tables
-- ============================================================

SELECT
    COUNT(DISTINCT o.order_id) AS orders_count,
    COUNT(DISTINCT oi.order_id) AS orders_with_items_count
FROM staging.stg_orders AS o
LEFT JOIN staging.stg_order_items AS oi
    ON o.order_id = oi.order_id;


SELECT
    COUNT(DISTINCT oi.product_id) AS products_in_order_items,
    COUNT(DISTINCT p.product_id) AS matching_products
FROM staging.stg_order_items AS oi
LEFT JOIN staging.stg_products AS p
    ON oi.product_id = p.product_id;


SELECT
    COUNT(DISTINCT oi.seller_id) AS sellers_in_order_items,
    COUNT(DISTINCT s.seller_id) AS matching_sellers
FROM staging.stg_order_items AS oi
LEFT JOIN staging.stg_sellers AS s
    ON oi.seller_id = s.seller_id;