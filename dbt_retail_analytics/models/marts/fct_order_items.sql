with order_items as (

    select *
    from {{ ref('stg_order_items') }}

),

final as (

    select
        order_id,
        order_item_id,
        product_id,
        seller_id,

        shipping_limit_date,
        price,
        freight_value,

        price + freight_value as total_item_value,

        source_file_name,
        ingested_at,
        run_date

    from order_items

)

select *
from final