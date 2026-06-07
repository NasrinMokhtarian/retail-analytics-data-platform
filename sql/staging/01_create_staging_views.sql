--  raw tables → staging views
-- cast dates/timestamps
-- cast numeric fields
-- cast booleans
-- standardize selected text fields
-- keep metadata columns
-- prepare data for later marts/dbt 

-- ============================================================
-- Retail Analytics Data Platform
-- Create PostgreSQL Staging Views
--
-- Purpose:
-- Create typed and standardized staging views from raw loaded tables.
--
-- Layer:
-- raw      = loaded source-like tables
-- staging  = typed, cleaned SQL transformation layer
-- mart     = business-ready models later
-- ============================================================


-- ============================================================
-- Customers
-- ============================================================
CREATE OR REPLACE VIEW staging.stg_customers AS
SELECT 
    customer_id::text AS customer_id,
    customer_unique_id::text AS customer_unique_id,
    customer_zip_code_prefix::text AS customer_zip_code_prefix,
    TRIM(customer_city::text) AS customer_city,
    UPPER(TRIM(customer_state::text)) AS customer_state,
    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.olist_customers;

-- ============================================================
-- Geolocation
-- ============================================================

CREATE OR REPLACE VIEW staging.stg_geolocation AS
SELECT
    geolocation_zip_code_prefix::text AS geolocation_zip_code_prefix,
    geolocation_lat::numeric AS geolocation_lat,
    geolocation_lng::numeric AS geolocation_lng,
    TRIM(geolocation_city::text) AS geolocation_city,
    UPPER(TRIM(geolocation_state::text)) AS geolocation_state,

    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.olist_geolocation;

-- ============================================================
-- Orders
-- ============================================================

CREATE OR REPLACE VIEW staging.stg_orders AS
SELECT
    order_id::text AS order_id,
    customer_id::text AS customer_id,
    LOWER(TRIM(order_status::text)) AS order_status,

    order_purchase_timestamp::timestamp AS order_purchase_timestamp,
    order_approved_at::timestamp AS order_approved_at,
    order_delivered_carrier_date::timestamp AS order_delivered_carrier_date,
    order_delivered_customer_date::timestamp AS order_delivered_customer_date,
    order_estimated_delivery_date::timestamp AS order_estimated_delivery_date,

    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.olist_orders;


-- ============================================================
-- Order Items
-- ============================================================

CREATE OR REPLACE VIEW staging.stg_order_items AS
SELECT
    order_id::text AS order_id,
    order_item_id::integer AS order_item_id,
    product_id::text AS product_id,
    seller_id::text AS seller_id,

    shipping_limit_date::timestamp AS shipping_limit_date,
    price::numeric AS price,
    freight_value::numeric AS freight_value,

    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.olist_order_items;


-- ============================================================
-- Order Payments
-- ============================================================

CREATE OR REPLACE VIEW staging.stg_order_payments AS
SELECT
    order_id::text AS order_id,
    payment_sequential::integer AS payment_sequential,
    LOWER(TRIM(payment_type::text)) AS payment_type,
    payment_installments::integer AS payment_installments,
    payment_value::numeric AS payment_value,

    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.olist_order_payments;


-- ============================================================
-- Order Reviews
-- ============================================================

CREATE OR REPLACE VIEW staging.stg_order_reviews AS
SELECT
    review_id::text AS review_id,
    order_id::text AS order_id,
    review_score::integer AS review_score,
    review_comment_title::text AS review_comment_title,
    review_comment_message::text AS review_comment_message,

    review_creation_date::timestamp AS review_creation_date,
    review_answer_timestamp::timestamp AS review_answer_timestamp,

    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.olist_order_reviews;


-- ============================================================
-- Products
-- ============================================================

CREATE OR REPLACE VIEW staging.stg_products AS
SELECT
    product_id::text AS product_id,
    product_category_name::text AS product_category_name,

    product_name_lenght::integer AS product_name_lenght,
    product_description_lenght::integer AS product_description_lenght,
    product_photos_qty::integer AS product_photos_qty,

    product_weight_g::numeric AS product_weight_g,
    product_length_cm::numeric AS product_length_cm,
    product_height_cm::numeric AS product_height_cm,
    product_width_cm::numeric AS product_width_cm,

    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.olist_products;


-- ============================================================
-- Sellers
-- ============================================================

CREATE OR REPLACE VIEW staging.stg_sellers AS
SELECT
    seller_id::text AS seller_id,
    seller_zip_code_prefix::text AS seller_zip_code_prefix,
    TRIM(seller_city::text) AS seller_city,
    UPPER(TRIM(seller_state::text)) AS seller_state,

    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.olist_sellers;


-- ============================================================
-- Product Category Translation
-- ============================================================

CREATE OR REPLACE VIEW staging.stg_product_category_translation AS
SELECT
    product_category_name::text AS product_category_name,
    product_category_name_english::text AS product_category_name_english,

    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.product_category_translation;


-- ============================================================
-- Supplier Product Updates
-- ============================================================

CREATE OR REPLACE VIEW staging.stg_supplier_product_updates AS
SELECT
    supplier_id::text AS supplier_id,
    supplier_name::text AS supplier_name,
    product_id::text AS product_id,
    supplier_product_code::text AS supplier_product_code,

    updated_price::text AS updated_price_raw,
    updated_price_clean::numeric AS updated_price,

    currency::text AS currency_raw,
    currency_clean::text AS currency,

    stock_status::text AS stock_status_raw,
    stock_status_clean::text AS stock_status,

    valid_from::text AS valid_from_raw,
    valid_from_clean::date AS valid_from,

    last_updated_at::text AS last_updated_at_raw,
    last_updated_at_clean::timestamp AS last_updated_at,

    comments::text AS comments,

    has_missing_product_id::boolean AS has_missing_product_id,
    has_missing_currency::boolean AS has_missing_currency,
    has_invalid_price::boolean AS has_invalid_price,
    has_negative_price::boolean AS has_negative_price,
    has_unknown_stock_status::boolean AS has_unknown_stock_status,
    has_missing_valid_from::boolean AS has_missing_valid_from,
    has_invalid_valid_from::boolean AS has_invalid_valid_from,
    has_invalid_last_updated_at::boolean AS has_invalid_last_updated_at,
    is_duplicate_business_key::boolean AS is_duplicate_business_key,

    source_file_name::text AS source_file_name,
    ingested_at::timestamp AS ingested_at,
    run_date::date AS run_date
FROM raw.supplier_product_updates;



-- Verify staging views exist
SELECT
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'staging'
ORDER BY table_name;

-- Test row counts
SELECT 'staging.stg_customers' AS view_name, COUNT(*) AS row_count FROM staging.stg_customers
UNION ALL
SELECT 'staging.stg_geolocation', COUNT(*) FROM staging.stg_geolocation
UNION ALL
SELECT 'staging.stg_order_items', COUNT(*) FROM staging.stg_order_items
UNION ALL
SELECT 'staging.stg_order_payments', COUNT(*) FROM staging.stg_order_payments
UNION ALL
SELECT 'staging.stg_order_reviews', COUNT(*) FROM staging.stg_order_reviews
UNION ALL
SELECT 'staging.stg_orders', COUNT(*) FROM staging.stg_orders
UNION ALL
SELECT 'staging.stg_products', COUNT(*) FROM staging.stg_products
UNION ALL
SELECT 'staging.stg_sellers', COUNT(*) FROM staging.stg_sellers
UNION ALL
SELECT 'staging.stg_product_category_translation', COUNT(*) FROM staging.stg_product_category_translation
UNION ALL
SELECT 'staging.stg_supplier_product_updates', COUNT(*) FROM staging.stg_supplier_product_updates
ORDER BY view_name;

-- Test a few typed fields
SELECT
    order_id,
    order_status,
    order_purchase_timestamp,
    pg_typeof(order_purchase_timestamp) AS purchase_ts_type,
    run_date,
    pg_typeof(run_date) AS run_date_type
FROM staging.stg_orders
LIMIT 10;

SELECT
    order_id,
    price,
    pg_typeof(price) AS price_type,
    freight_value,
    pg_typeof(freight_value) AS freight_type
FROM staging.stg_order_items
LIMIT 10;

SELECT
    supplier_id,
    updated_price,
    pg_typeof(updated_price) AS updated_price_type,
    has_invalid_price,
    pg_typeof(has_invalid_price) AS invalid_price_flag_type
FROM staging.stg_supplier_product_updates
LIMIT 10;