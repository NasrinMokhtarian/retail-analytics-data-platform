OLIST_OUTPUT_FILE_NAMES: dict[str, str] = {
    "olist_customers_dataset.csv": "customers_clean.csv",
    "olist_geolocation_dataset.csv": "geolocation_clean.csv",
    "olist_order_items_dataset.csv": "order_items_clean.csv",
    "olist_order_payments_dataset.csv": "order_payments_clean.csv",
    "olist_order_reviews_dataset.csv": "order_reviews_clean.csv",
    "olist_orders_dataset.csv": "orders_clean.csv",
    "olist_products_dataset.csv": "products_clean.csv",
    "olist_sellers_dataset.csv": "sellers_clean.csv",
    "product_category_name_translation.csv": "product_category_translation_clean.csv",
}


TIMESTAMP_COLUMNS: dict[str, list[str]] = {
    "olist_orders_dataset.csv": [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
    "olist_order_items_dataset.csv": [
        "shipping_limit_date",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_creation_date",
        "review_answer_timestamp",
    ],
}


NUMERIC_COLUMNS: dict[str, list[str]] = {
    "olist_geolocation_dataset.csv": [
        "geolocation_lat",
        "geolocation_lng",
    ],
    "olist_order_items_dataset.csv": [
        "price",
        "freight_value",
    ],
    "olist_order_payments_dataset.csv": [
        "payment_sequential",
        "payment_installments",
        "payment_value",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_score",
    ],
    "olist_products_dataset.csv": [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm",
    ],
}


STRING_COLUMNS: dict[str, list[str]] = {
    "olist_customers_dataset.csv": [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state",
    ],
    "olist_geolocation_dataset.csv": [
        "geolocation_zip_code_prefix",
        "geolocation_city",
        "geolocation_state",
    ],
    "olist_order_items_dataset.csv": [
        "order_id",
        "product_id",
        "seller_id",
    ],
    "olist_order_payments_dataset.csv": [
        "order_id",
        "payment_type",
    ],
    "olist_order_reviews_dataset.csv": [
        "review_id",
        "order_id",
        "review_comment_title",
        "review_comment_message",
    ],
    "olist_orders_dataset.csv": [
        "order_id",
        "customer_id",
        "order_status",
    ],
    "olist_products_dataset.csv": [
        "product_id",
        "product_category_name",
    ],
    "olist_sellers_dataset.csv": [
        "seller_id",
        "seller_zip_code_prefix",
        "seller_city",
        "seller_state",
    ],
    "product_category_name_translation.csv": [
        "product_category_name",
        "product_category_name_english",
    ],
}