-- ============================================================
-- Retail Analytics Data Platform
-- Business Overview Queries
--
-- Purpose:
-- Explore the loaded raw PostgreSQL tables and understand
-- the main business patterns before building staging/mart models.
-- ============================================================


-- 1. Order count by status

SELECT
    order_status,
    COUNT(*) AS order_count
FROM raw.olist_orders
GROUP BY order_status
ORDER BY order_count DESC;


-- 2. Monthly order volume

SELECT
    DATE_TRUNC('month', order_purchase_timestamp::timestamp) AS order_month,
    COUNT(*) AS order_count
FROM raw.olist_orders
GROUP BY order_month
ORDER BY order_month;


-- 3. Total item revenue

SELECT
    ROUND(SUM(price::numeric), 2) AS total_item_revenue
FROM raw.olist_order_items;


-- 4. Monthly item revenue

SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp::timestamp) AS order_month,
    ROUND(SUM(oi.price::numeric), 2) AS monthly_item_revenue
FROM raw.olist_orders AS o
JOIN raw.olist_order_items AS oi
    ON o.order_id = oi.order_id
GROUP BY order_month
ORDER BY order_month;


-- 5. Orders by customer state

SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS order_count
FROM raw.olist_orders AS o
JOIN raw.olist_customers AS c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY order_count DESC;


-- 6. Top product categories by item revenue

SELECT
    COALESCE(t.product_category_name_english, p.product_category_name) AS product_category,
    COUNT(*) AS item_count,
    ROUND(SUM(oi.price::numeric), 2) AS item_revenue
FROM raw.olist_order_items AS oi
JOIN raw.olist_products AS p
    ON oi.product_id = p.product_id
LEFT JOIN raw.product_category_translation AS t
    ON p.product_category_name = t.product_category_name
GROUP BY COALESCE(t.product_category_name_english, p.product_category_name)
ORDER BY item_revenue DESC
LIMIT 20;


-- 7. Payment type distribution

SELECT
    payment_type,
    COUNT(*) AS payment_record_count,
    ROUND(SUM(payment_value::numeric), 2) AS total_payment_value
FROM raw.olist_order_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;


-- 8. Average review score by order status

SELECT
    o.order_status,
    ROUND(AVG(r.review_score::numeric), 2) AS avg_review_score,
    COUNT(*) AS review_count
FROM raw.olist_orders AS o
JOIN raw.olist_order_reviews AS r
    ON o.order_id = r.order_id
GROUP BY o.order_status
ORDER BY avg_review_score DESC;


-- 9. Supplier quality flag summary

SELECT
    COUNT(*) AS total_supplier_rows,
    SUM(CASE WHEN has_missing_product_id::boolean THEN 1 ELSE 0 END) AS missing_product_id_rows,
    SUM(CASE WHEN has_missing_currency::boolean THEN 1 ELSE 0 END) AS missing_currency_rows,
    SUM(CASE WHEN has_invalid_price::boolean THEN 1 ELSE 0 END) AS invalid_price_rows,
    SUM(CASE WHEN has_negative_price::boolean THEN 1 ELSE 0 END) AS negative_price_rows,
    SUM(CASE WHEN has_unknown_stock_status::boolean THEN 1 ELSE 0 END) AS unknown_stock_status_rows,
    SUM(CASE WHEN is_duplicate_business_key::boolean THEN 1 ELSE 0 END) AS duplicate_business_key_rows
FROM raw.supplier_product_updates;


-- 10. Supplier rows needing review

SELECT
    supplier_id,
    supplier_name,
    product_id,
    supplier_product_code,
    updated_price,
    updated_price_clean,
    currency,
    currency_clean,
    stock_status,
    stock_status_clean,
    has_missing_product_id,
    has_missing_currency,
    has_invalid_price,
    has_negative_price,
    has_unknown_stock_status,
    is_duplicate_business_key
FROM raw.supplier_product_updates
WHERE
    has_missing_product_id::boolean
    OR has_missing_currency::boolean
    OR has_invalid_price::boolean
    OR has_negative_price::boolean
    OR has_unknown_stock_status::boolean
    OR is_duplicate_business_key::boolean
ORDER BY supplier_id;