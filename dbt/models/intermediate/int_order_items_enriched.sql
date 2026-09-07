select
    oi.order_id,
    oi.order_item_id,
    oi.product_id,
    oi.seller_id,
    oi.shipping_limit_date,
    oi.price,
    oi.freight_value,
    (coalesce(oi.price, 0) + coalesce(oi.freight_value, 0))::decimal(18,2) as item_gross_value,
    p.product_category_name,
    p.product_category_name_english,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state
from {{ ref('stg_order_items') }} oi
left join {{ ref('int_products_enriched') }} p
  on oi.product_id = p.product_id
left join {{ ref('stg_sellers') }} s
  on oi.seller_id = s.seller_id
