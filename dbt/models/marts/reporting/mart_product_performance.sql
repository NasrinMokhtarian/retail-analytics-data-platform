with product_sales as (

    select
        product_id,
        coalesce(product_category_name_english, 'unknown') as product_category,
        count(*) as units_sold,
        count(distinct order_id) as orders_with_product,
        count(distinct seller_id) as seller_count,

        sum(coalesce(price, 0))::decimal(18,2) as item_revenue,
        sum(coalesce(freight_value, 0))::decimal(18,2) as freight_value,
        sum(coalesce(item_gross_value, 0))::decimal(18,2) as gross_value,

        avg(price)::decimal(18,2) as avg_item_price,
        avg(freight_value)::decimal(18,2) as avg_freight_value

    from {{ ref('fct_order_items') }}

    where product_id is not null

    group by 1, 2

)

select *
from product_sales