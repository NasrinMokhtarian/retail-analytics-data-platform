with source_order_payments as (select * from {{source('raw','olist_order_payments')}}),
staged_order_payments as (
    select 
        order_id::text as order_id,
        payment_sequential::integer as payment_sequential,
        lower(trim(payment_type::text)) as payment_type,
        payment_installments::integer as payment_installments,
        payment_value::numeric as payment_value,

        source_file_name::text as source_file_name,
        ingested_at::timestamp as ingested_at,
        run_date::date as run_date
        from source_order_payments

)
select * from staged_order_payments