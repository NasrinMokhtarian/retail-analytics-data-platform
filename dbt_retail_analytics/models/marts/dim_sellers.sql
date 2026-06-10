with sellers as (

    select *
    from {{ ref('stg_sellers') }}

),

final as (

    select
        seller_id,
        seller_zip_code_prefix,
        seller_city,
        seller_state,

        source_file_name,
        ingested_at,
        run_date

    from sellers

)

select *
from final