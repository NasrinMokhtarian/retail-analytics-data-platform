select
    product_id,
    count(*) as units_sold,
    count(distinct order_id) as orders_with_product,
    count(distinct seller_id) as seller_count,
    sum(coalesce(price, 0))::decimal(18,2) as marketplace_revenue,
    sum(coalesce(freight_value, 0))::decimal(18,2) as freight_value,
    avg(price)::decimal(18,2) as avg_marketplace_price
from {{ ref('stg_order_items') }}
where product_id is not null
group by 1
