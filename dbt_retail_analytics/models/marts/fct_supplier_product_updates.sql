with supplier_updates as (

    select *
    from {{ ref('stg_supplier_product_updates') }}

),

final as (

    select
        supplier_id,
        supplier_name,
        product_id,
        supplier_product_code,

        updated_price,
        currency,
        stock_status,
        valid_from,
        last_updated_at,

        comments,

        has_missing_product_id,
        has_missing_currency,
        has_invalid_price,
        has_negative_price,
        has_unknown_stock_status,
        has_missing_valid_from,
        has_invalid_valid_from,
        has_invalid_last_updated_at,
        is_duplicate_business_key,

        case
            when has_missing_product_id
              or has_missing_currency
              or has_invalid_price
              or has_negative_price
              or has_unknown_stock_status
              or has_missing_valid_from
              or has_invalid_valid_from
              or has_invalid_last_updated_at
              or is_duplicate_business_key
            then true
            else false
        end as needs_business_review,

        source_file_name,
        ingested_at,
        run_date

    from supplier_updates

)

select *
from final