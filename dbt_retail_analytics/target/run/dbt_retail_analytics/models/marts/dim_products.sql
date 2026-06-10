
  create view "retail_analytics"."dbt_mart"."dim_products__dbt_tmp"
    
    
  as (
    with products as (select * from "retail_analytics"."dbt_staging"."stg_products"),
category_translation as (select * from "retail_analytics"."dbt_staging"."stg_product_category_translation"),
final as (
    select p.product_id,p.product_category_name,
        coalesce(
            t.product_category_name_english,
            p.product_category_name
        ) as product_category_name_english,

        p.product_name_lenght as product_name_length,
        p.product_description_lenght as product_description_length,
        p.product_photos_qty,
        p.product_weight_g,
        p.product_length_cm,
        p.product_height_cm,
        p.product_width_cm,

        p.source_file_name,
        p.ingested_at,
        p.run_date

    from products as p
    left join category_translation as t
        on p.product_category_name = t.product_category_name
)
select * from final
  );