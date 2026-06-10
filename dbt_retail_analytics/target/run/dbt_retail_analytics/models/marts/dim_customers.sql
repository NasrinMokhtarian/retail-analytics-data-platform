
  create view "retail_analytics"."dbt_mart"."dim_customers__dbt_tmp"
    
    
  as (
    with customers as (select * from "retail_analytics"."dbt_staging"."stg_customers"),
final as (
     select
        customer_id,
        customer_unique_id,
        customer_zip_code_prefix,
        customer_city,
        customer_state,

        source_file_name,
        ingested_at,
        run_date

    from customers 
)
select * from final
  );