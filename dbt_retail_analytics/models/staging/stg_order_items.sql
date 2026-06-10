with source_order_items as (

    select *
    from {{ source('raw', 'olist_order_items') }}

),

staged_order_items as (

    select
        order_id::text as order_id,
        order_item_id::integer as order_item_id,
        product_id::text as product_id,
        seller_id::text as seller_id,

        shipping_limit_date::timestamp as shipping_limit_date,
        price::numeric as price,
        freight_value::numeric as freight_value,

        source_file_name::text as source_file_name,
        ingested_at::timestamp as ingested_at,
        run_date::date as run_date

    from source_order_items

)

select *
from staged_order_items