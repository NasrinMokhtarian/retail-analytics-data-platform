with source_sellers as (

    select *
    from {{ source('raw', 'olist_sellers') }}

),

staged_sellers as (

    select
        seller_id::text as seller_id,
        seller_zip_code_prefix::text as seller_zip_code_prefix,
        trim(seller_city::text) as seller_city,
        upper(trim(seller_state::text)) as seller_state,

        source_file_name::text as source_file_name,
        ingested_at::timestamp as ingested_at,
        run_date::date as run_date

    from source_sellers

)

select *
from staged_sellers