-- ============================================================
-- Retail Analytics Data Platform
-- Raw Layer Sanity Checks
--
-- Purpose:
-- Validate that the raw PostgreSQL tables are available,
-- populated, and ready for exploration.
-- ============================================================


-- 1. List all tables in the raw schema

SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'raw'
ORDER BY table_name;

-- 2. Check row counts for all raw tables
SELECT 'raw.olist_customers' as table_name, COUNT(*) as raw_count FROM raw.olist_customers
UNION ALL
SELECT 'raw.olist_geolocation', COUNT(*) FROM raw.olist_geolocation
UNION ALL
SELECT 'raw.olist_order_items', COUNT(*) FROM raw.olist_order_items
UNION ALL
SELECT 'raw.olist_order_payments', COUNT(*) FROM raw.olist_order_payments
UNION ALL
SELECT 'raw.olist_order_reviews', COUNT(*) FROM raw.olist_order_reviews
UNION ALL
SELECT 'raw.olist_orders', COUNT(*) FROM raw.olist_orders
UNION ALL
SELECT 'raw.olist_products', COUNT(*) FROM raw.olist_products
UNION ALL
SELECT 'raw.olist_sellers', COUNT(*) FROM raw.olist_sellers
UNION ALL
SELECT 'raw.product_category_translation', COUNT(*) FROM raw.product_category_translation
UNION ALL
SELECT 'raw.supplier_product_updates', COUNT(*) FROM raw.supplier_product_updates
ORDER BY table_name;

-- 3. Check latest load audit records

SELECT load_id,run_date,source_name,source_file,target_schema,target_table,source_row_count,
loaded_row_count,status,load_started_at,load_finished_at
FROM audit.load_audit 
ORDER BY load_id DESC

-- 4. Check if any load failed
SELECT  load_id,
    run_date,
    source_name,
    source_file,
    target_table,
    status,
    error_message
FROM audit.load_audit 
WHERE status <> 'SUCCESS'
ORDER BY load_id DESC

-- 5. Check row-count mismatches in audit table
SELECT  load_id,
    source_name,
    source_file,
    target_table,
    source_row_count,
    loaded_row_count,
    status
FROM audit.load_audit
WHERE source_row_count <> loaded_row_count
ORDER BY load_id DESC

-- 6. Inspect orders table sample

SELECT *
FROM raw.olist_orders
LIMIT 10;


-- 7. Inspect order items table sample

SELECT *
FROM raw.olist_order_items
LIMIT 10;


-- 8. Inspect supplier product updates sample

SELECT *
FROM raw.supplier_product_updates
LIMIT 10;
