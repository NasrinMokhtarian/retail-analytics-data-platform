-- ============================================================
-- Retail Analytics Data Platform
-- Validate Mart Views
--
-- Purpose:
-- Validate that mart views are reliable for business analysis.
-- ============================================================


-- ============================================================
-- 1. Check mart views exist
-- ============================================================
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'mart'
ORDER BY table_name;

-- ============================================================
-- 2. Check mart row counts
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
-- 3. Validate dimension grain uniqueness
-- Expected duplicate_count = 0
-- ============================================================
SELECT
    'dim_customers.customer_id' AS check_name,
    COUNT(*) - COUNT(DISTINCT customer_id) AS duplicate_count
FROM mart.dim_customers

UNION ALL

SELECT
    'dim_products.product_id',
    COUNT(*) - COUNT(DISTINCT product_id)
FROM mart.dim_products

UNION ALL

SELECT
    'dim_sellers.seller_id',
    COUNT(*) - COUNT(DISTINCT seller_id)
FROM mart.dim_sellers
ORDER BY check_name;

-- ============================================================
-- 4. Validate fact grain uniqueness
-- Expected duplicate_count = 0
-- ============================================================
SELECT
    'fct_orders.order_id' AS check_name,
    COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_count
FROM mart.fct_orders

UNION ALL

SELECT
    'fct_order_items.order_id + order_item_id',
    COUNT(*) - COUNT(DISTINCT order_id || '-' || order_item_id::text)
FROM mart.fct_order_items

UNION ALL

SELECT
    'fct_payments.order_id + payment_sequential',
    COUNT(*) - COUNT(DISTINCT order_id || '-' || payment_sequential::text)
FROM mart.fct_payments

UNION ALL

SELECT
    'fct_reviews.review_id',
    COUNT(*) - COUNT(DISTINCT review_id)
FROM mart.fct_reviews
ORDER BY check_name;

-- ============================================================
-- 5. Check important not-null IDs
-- Expected null_count = 0 for core Olist fields
-- ============================================================
SELECT
    'dim_customers.customer_id' AS check_name,
    COUNT(*) AS null_count
FROM mart.dim_customers
WHERE customer_id IS NULL

UNION ALL

SELECT
    'dim_products.product_id',
    COUNT(*)
FROM mart.dim_products
WHERE product_id IS NULL

UNION ALL

SELECT
    'dim_sellers.seller_id',
    COUNT(*)
FROM mart.dim_sellers
WHERE seller_id IS NULL

UNION ALL

SELECT
    'fct_orders.order_id',
    COUNT(*)
FROM mart.fct_orders
WHERE order_id IS NULL

UNION ALL

SELECT
    'fct_orders.customer_id',
    COUNT(*)
FROM mart.fct_orders
WHERE customer_id IS NULL

UNION ALL

SELECT
    'fct_order_items.order_id',
    COUNT(*)
FROM mart.fct_order_items
WHERE order_id IS NULL

UNION ALL

SELECT
    'fct_order_items.product_id',
    COUNT(*)
FROM mart.fct_order_items
WHERE product_id IS NULL

UNION ALL

SELECT
    'fct_order_items.seller_id',
    COUNT(*)
FROM mart.fct_order_items
WHERE seller_id IS NULL
ORDER BY check_name;

-- ============================================================
-- 6. Validate revenue and payment measures
-- Expected negative_count = 0 for Olist revenue/payment fields
-- ============================================================
SELECT
    'fct_order_items.price' AS check_name,
    COUNT(*) AS negative_count
FROM mart.fct_order_items
WHERE price < 0

UNION ALL

SELECT
    'fct_order_items.freight_value',
    COUNT(*)
FROM mart.fct_order_items
WHERE freight_value < 0

UNION ALL

SELECT
    'fct_order_items.total_item_value',
    COUNT(*)
FROM mart.fct_order_items
WHERE total_item_value < 0

UNION ALL

SELECT
    'fct_payments.payment_value',
    COUNT(*)
FROM mart.fct_payments
WHERE payment_value < 0
ORDER BY check_name;

-- ============================================================
-- 7. Validate delivery metrics
-- Negative days_to_customer_delivery should be investigated.
-- delivery_delay_days can be negative when delivered earlier than estimated.
-- ============================================================
SELECT
    COUNT(*) AS negative_days_to_customer_delivery_count
FROM mart.fct_orders
WHERE days_to_customer_delivery < 0;


SELECT
    COUNT(*) AS delivered_orders_without_delivery_days
FROM mart.fct_orders
WHERE is_delivered = TRUE
  AND days_to_customer_delivery IS NULL;


SELECT
    is_late_delivery,
    COUNT(*) AS order_count
FROM mart.fct_orders
WHERE is_delivered = TRUE
GROUP BY is_late_delivery
ORDER BY is_late_delivery;

-- ============================================================
-- 8. Validate review sentiment grouping
-- ============================================================

SELECT
    review_score,
    review_sentiment_group,
    COUNT(*) AS review_count
FROM mart.fct_reviews
GROUP BY review_score, review_sentiment_group
ORDER BY review_score, review_sentiment_group;


-- ============================================================
-- 9. Validate supplier review flag
-- Expected: rows with any quality issue should have needs_business_review = TRUE
-- ============================================================

SELECT
    COUNT(*) AS supplier_rows_needing_review
FROM mart.fct_supplier_product_updates
WHERE needs_business_review = TRUE;


SELECT
    COUNT(*) AS supplier_flag_mismatch_count
FROM mart.fct_supplier_product_updates
WHERE
    (
        has_missing_product_id
        OR has_missing_currency
        OR has_invalid_price
        OR has_negative_price
        OR has_unknown_stock_status
        OR has_missing_valid_from
        OR has_invalid_valid_from
        OR has_invalid_last_updated_at
        OR is_duplicate_business_key
    )
    AND needs_business_review = FALSE;


-- ============================================================
-- 10. Validate fact-to-dimension join readiness
-- ============================================================

-- Orders should join to customers

SELECT
    COUNT(*) AS orders_without_matching_customer
FROM mart.fct_orders AS o
LEFT JOIN mart.dim_customers AS c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- Order items should join to products

SELECT
    COUNT(*) AS order_items_without_matching_product
FROM mart.fct_order_items AS oi
LEFT JOIN mart.dim_products AS p
    ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;


-- Order items should join to sellers

SELECT
    COUNT(*) AS order_items_without_matching_seller
FROM mart.fct_order_items AS oi
LEFT JOIN mart.dim_sellers AS s
    ON oi.seller_id = s.seller_id
WHERE s.seller_id IS NULL;


-- Supplier updates that have product_id should join to products where possible

SELECT
    COUNT(*) AS supplier_updates_with_product_id_without_matching_product
FROM mart.fct_supplier_product_updates AS sup
LEFT JOIN mart.dim_products AS p
    ON sup.product_id = p.product_id
WHERE sup.product_id IS NOT NULL
  AND p.product_id IS NULL;


-- ============================================================
-- 11. First business-ready query from mart layer
-- Revenue by product category
-- ============================================================

SELECT
    p.product_category_name_english,
    COUNT(*) AS item_count,
    ROUND(SUM(oi.price), 2) AS item_revenue,
    ROUND(SUM(oi.total_item_value), 2) AS item_value_including_freight
FROM mart.fct_order_items AS oi
LEFT JOIN mart.dim_products AS p
    ON oi.product_id = p.product_id
GROUP BY p.product_category_name_english
ORDER BY item_revenue DESC
LIMIT 20;


-- ============================================================
-- 12. First delivery-performance query from mart layer
-- ============================================================

SELECT
    is_late_delivery,
    COUNT(*) AS delivered_order_count,
    ROUND(AVG(delivery_delay_days), 2) AS avg_delivery_delay_days
FROM mart.fct_orders
WHERE is_delivered = TRUE
GROUP BY is_late_delivery
ORDER BY is_late_delivery;