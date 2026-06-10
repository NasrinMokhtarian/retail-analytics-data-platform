with source_customers as (select * from "retail_analytics"."raw"."olist_customers"),

staged_customers as (
    select
    customer_id::text as customer_id,
    customer_unique_id::text as customer_unique_id,
    customer_zip_code_prefix::text as customer_zip_code_prefix,
    trim(customer_city::text) as customer_city,
    upper(trim(customer_state::text)) as customer_state,
    source_file_name::text as source_file_name,
    ingested_at::timestamp as ingested_at,
    run_date::date as run_date

    from source_customers

)
select * from staged_customers