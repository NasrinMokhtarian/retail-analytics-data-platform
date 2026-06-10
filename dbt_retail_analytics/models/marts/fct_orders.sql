with orders as (

    select *
    from {{ ref('stg_orders') }}

),

final as (

    select
        order_id,
        customer_id,
        order_status,

        order_purchase_timestamp,
        order_purchase_timestamp::date as order_purchase_date,

        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,

        case
            when order_status = 'delivered' then true
            else false
        end as is_delivered,

        case
            when order_purchase_timestamp is not null
             and order_delivered_customer_date is not null
            then date_part(
                'day',
                order_delivered_customer_date - order_purchase_timestamp
            )::integer
            else null
        end as days_to_customer_delivery,

        case
            when order_delivered_customer_date is not null
             and order_estimated_delivery_date is not null
            then date_part(
                'day',
                order_delivered_customer_date - order_estimated_delivery_date
            )::integer
            else null
        end as delivery_delay_days,

        case
            when order_delivered_customer_date is not null
             and order_estimated_delivery_date is not null
             and order_delivered_customer_date > order_estimated_delivery_date
            then true
            when order_delivered_customer_date is not null
             and order_estimated_delivery_date is not null
            then false
            else null
        end as is_late_delivery,

        source_file_name,
        ingested_at,
        run_date

    from orders

)

select *
from final