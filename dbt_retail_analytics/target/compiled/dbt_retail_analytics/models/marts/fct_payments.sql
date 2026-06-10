with payments as (

    select *
    from "retail_analytics"."dbt_staging"."stg_order_payments"

),

final as (

    select
        order_id,
        payment_sequential,
        payment_type,
        payment_installments,
        payment_value,

        source_file_name,
        ingested_at,
        run_date

    from payments

)

select *
from final