select
    date_trunc('month', o.order_purchase_timestamp)::date as month_start,
    coalesce(i.product_category_name_english, 'unknown') as product_category,
    coalesce(i.seller_state, 'unknown') as seller_state,
    count(distinct o.order_id) as orders,
    count(*) as items_sold,
    sum(coalesce(i.price, 0))::decimal(18,2) as item_revenue,
    sum(coalesce(i.freight_value, 0))::decimal(18,2) as freight_value,
    sum(coalesce(i.item_gross_value, 0))::decimal(18,2) as gross_value,
    avg(i.price)::decimal(18,2) as avg_item_price
from {{ ref('fct_orders') }} o
join {{ ref('fct_order_items') }} i
  on o.order_id = i.order_id
group by 1, 2, 3
