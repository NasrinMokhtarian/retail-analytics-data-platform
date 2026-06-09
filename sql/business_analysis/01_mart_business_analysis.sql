-- ============================================================
-- Retail Analytics Data Platform
-- Business Analysis Queries from Mart Layer
--
-- Purpose:
-- Answer first business questions using validated mart views.
--
-- Important:
-- These queries use mart views, not raw tables.
-- This helps avoid repeating low-level transformation logic.
-- ============================================================

-- ============================================================
-- 1. Monthly order volume
-- Business question:
-- How many orders were placed each month?
-- ============================================================
select DATE_TRUNC('month',order_purchase_date)::date as monthly_order, COUNT(order_id) as order_count
from mart.fct_orders 
group by monthly_order
order BY monthly_order asc

-- ============================================================
-- 2. Monthly item revenue
-- Business question:
-- How much item revenue was generated each month?
--
-- Note:
-- Revenue is calculated from item-level price.
-- This avoids double counting order-level records.
-- ============================================================

select DATE_TRUNC('month',o.order_purchase_date)::date as month,ROUND(sum( oi.price),2) as total_revenue,
ROUND(sum(oi.total_item_value),2) as item_value_freight,
COUNT(o.order_id) as order_count, COUNT(oi.order_item_id) as item_count
from mart.fct_orders as o  join mart.fct_order_items as oi on o.order_id = oi.order_id
group by month
order by month asc

-- ============================================================
-- 3. Top product categories by revenue
-- Business question:
-- Which product categories generate the most item revenue?
-- ============================================================
select COALESCE(p.product_category_name_english,'Unknown')product_category , round(sum(oi.price),2) as item_revenue
from mart.dim_products as p join mart.fct_order_items as oi on p.product_id=oi.product_id
group by 1
order by item_revenue desc

-- ============================================================
-- 4. Customer states by order volume
-- Business question:
-- Which customer states have the highest order volume?
-- ============================================================
SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS order_count
FROM mart.fct_orders AS o
LEFT JOIN mart.dim_customers AS c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY order_count DESC;


-- ============================================================
-- 5. Customer states by item revenue
-- Business question:
-- Which customer states generate the most item revenue?
-- ============================================================

SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS order_count,
    COUNT(*) AS item_count,
    ROUND(SUM(oi.price), 2) AS item_revenue
FROM mart.fct_order_items AS oi
JOIN mart.fct_orders AS o
    ON oi.order_id = o.order_id
LEFT JOIN mart.dim_customers AS c
    ON o.customer_id = c.customer_id
GROUP BY c.customer_state
ORDER BY item_revenue DESC;


-- ============================================================
-- 6. Top sellers by item revenue
-- Business question:
-- Which sellers generate the most item revenue?
-- ============================================================

SELECT
    s.seller_id,
    s.seller_state,
    s.seller_city,
    COUNT(*) AS item_count,
    COUNT(DISTINCT oi.order_id) AS order_count,
    ROUND(SUM(oi.price), 2) AS item_revenue,
    ROUND(SUM(oi.freight_value), 2) AS freight_revenue
FROM mart.fct_order_items AS oi
LEFT JOIN mart.dim_sellers AS s
    ON oi.seller_id = s.seller_id
GROUP BY
    s.seller_id,
    s.seller_state,
    s.seller_city
ORDER BY item_revenue DESC
LIMIT 20;


-- ============================================================
-- 7. Delivery performance summary
-- Business question:
-- How many delivered orders were late, on time, or early?
-- ============================================================

SELECT
    is_late_delivery,
    COUNT(*) AS delivered_order_count,
    ROUND(AVG(delivery_delay_days), 2) AS avg_delivery_delay_days,
    MIN(delivery_delay_days) AS min_delivery_delay_days,
    MAX(delivery_delay_days) AS max_delivery_delay_days
FROM mart.fct_orders
WHERE is_delivered = TRUE
  AND delivery_delay_days IS NOT NULL
GROUP BY is_late_delivery
ORDER BY is_late_delivery;


-- ============================================================
-- 8. Delivery delay and review score
-- Business question:
-- Do late deliveries have lower review scores?
-- ============================================================

SELECT
    o.is_late_delivery,
    COUNT(*) AS review_count,
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM mart.fct_orders AS o
JOIN mart.fct_reviews AS r
    ON o.order_id = r.order_id
WHERE o.is_delivered = TRUE
  AND o.is_late_delivery IS NOT NULL
GROUP BY o.is_late_delivery
ORDER BY o.is_late_delivery;


-- ============================================================
-- 9. Review sentiment distribution
-- Business question:
-- What is the distribution of positive, neutral, and negative reviews?
-- ============================================================

SELECT
    review_sentiment_group,
    COUNT(*) AS review_count,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (),
        2
    ) AS review_percentage
FROM mart.fct_reviews
GROUP BY review_sentiment_group
ORDER BY review_count DESC;


-- ============================================================
-- 10. Payment type distribution
-- Business question:
-- Which payment methods are most used and represent most payment value?
-- ============================================================

SELECT
    payment_type,
    COUNT(*) AS payment_record_count,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(payment_value), 2) AS total_payment_value,
    ROUND(AVG(payment_value), 2) AS avg_payment_value
FROM mart.fct_payments
GROUP BY payment_type
ORDER BY total_payment_value DESC;


-- ============================================================
-- 11. Product category review score
-- Business question:
-- Which product categories have the best or worst average review scores?
-- ============================================================

SELECT
    COALESCE(p.product_category_name_english, 'unknown') AS product_category,
    COUNT(*) AS review_count,
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM mart.fct_reviews AS r
JOIN mart.fct_order_items AS oi
    ON r.order_id = oi.order_id
LEFT JOIN mart.dim_products AS p
    ON oi.product_id = p.product_id
GROUP BY COALESCE(p.product_category_name_english, 'unknown')
HAVING COUNT(*) >= 50
ORDER BY avg_review_score DESC
LIMIT 20;


-- ============================================================
-- 12. Worst product categories by review score
-- Business question:
-- Which product categories may need business attention?
-- ============================================================

SELECT
    COALESCE(p.product_category_name_english, 'unknown') AS product_category,
    COUNT(*) AS review_count,
    ROUND(AVG(r.review_score), 2) AS avg_review_score
FROM mart.fct_reviews AS r
JOIN mart.fct_order_items AS oi
    ON r.order_id = oi.order_id
LEFT JOIN mart.dim_products AS p
    ON oi.product_id = p.product_id
GROUP BY COALESCE(p.product_category_name_english, 'unknown')
HAVING COUNT(*) >= 50
ORDER BY avg_review_score ASC
LIMIT 20;


-- ============================================================
-- 13. Supplier rows needing business review
-- Business question:
-- Which supplier records should be reviewed before being trusted?
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
    is_duplicate_business_key,
    needs_business_review
FROM mart.fct_supplier_product_updates
WHERE needs_business_review = TRUE
ORDER BY supplier_id;


-- ============================================================
-- 14. Supplier issue summary
-- Business question:
-- What types of supplier data quality issues exist?
-- ============================================================

SELECT
    COUNT(*) AS total_supplier_rows,
    SUM(CASE WHEN needs_business_review THEN 1 ELSE 0 END) AS rows_needing_business_review,
    SUM(CASE WHEN has_missing_product_id THEN 1 ELSE 0 END) AS missing_product_id_rows,
    SUM(CASE WHEN has_missing_currency THEN 1 ELSE 0 END) AS missing_currency_rows,
    SUM(CASE WHEN has_invalid_price THEN 1 ELSE 0 END) AS invalid_price_rows,
    SUM(CASE WHEN has_negative_price THEN 1 ELSE 0 END) AS negative_price_rows,
    SUM(CASE WHEN has_unknown_stock_status THEN 1 ELSE 0 END) AS unknown_stock_status_rows,
    SUM(CASE WHEN is_duplicate_business_key THEN 1 ELSE 0 END) AS duplicate_business_key_rows
FROM mart.fct_supplier_product_updates;


-- ============================================================
-- 15. Supplier product updates joined to product dimension
-- Business question:
-- Which supplier updates can be connected to known products?
-- ============================================================

SELECT
    sup.supplier_id,
    sup.supplier_name,
    sup.product_id,
    p.product_category_name_english,
    sup.updated_price,
    sup.currency,
    sup.stock_status,
    sup.needs_business_review
FROM mart.fct_supplier_product_updates AS sup
LEFT JOIN mart.dim_products AS p
    ON sup.product_id = p.product_id
ORDER BY
    sup.needs_business_review DESC,
    sup.supplier_id;