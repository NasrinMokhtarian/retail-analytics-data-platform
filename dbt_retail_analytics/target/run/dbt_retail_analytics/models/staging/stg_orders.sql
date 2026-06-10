
  create view "retail_analytics"."dbt_staging"."stg_orders__dbt_tmp"
    
    
  as (
    with source_orders as ( select * from "retail_analytics"."raw"."olist_orders"),

staged_orders as (
    select 
    order_id::text as order_id,
    customer_id::text as customer_id,
    lower( trim(order_status::text)) as order_status,
    order_purchase_timestamp::timestamp as order_purchase_timestamp,
    order_approved_at::timestamp as order_approved_at,
    order_delivered_carrier_date::timestamp as order_delivered_carrier_date,
    order_delivered_customer_date::timestamp as order_delivered_customer_date,
    order_estimated_delivery_date::timestamp as order_estimated_delivery_date,
    source_file_name::text as source_file_name,
    ingested_at::timestamp as ingested_at,
    run_date::date as run_date

    from source_orders
)

select * from staged_orders
  );