with source_category_translation as (

    select *
    from {{ source('raw', 'product_category_translation') }}

),

staged_category_translation as (

    select
        product_category_name::text as product_category_name,
        product_category_name_english::text as product_category_name_english,

        source_file_name::text as source_file_name,
        ingested_at::timestamp as ingested_at,
        run_date::date as run_date

    from source_category_translation

)

select *
from staged_category_translation