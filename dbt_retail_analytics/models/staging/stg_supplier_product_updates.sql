with source_supplier_updates as (

    select *
    from {{ source('raw', 'supplier_product_updates') }}

),

staged_supplier_updates as (

    select
        supplier_id::text as supplier_id,
        supplier_name::text as supplier_name,
        product_id::text as product_id,
        supplier_product_code::text as supplier_product_code,

        updated_price::text as updated_price_raw,
        updated_price_clean::numeric as updated_price,

        currency::text as currency_raw,
        currency_clean::text as currency,

        stock_status::text as stock_status_raw,
        stock_status_clean::text as stock_status,

        valid_from::text as valid_from_raw,
        valid_from_clean::date as valid_from,

        last_updated_at::text as last_updated_at_raw,
        last_updated_at_clean::timestamp as last_updated_at,

        comments::text as comments,

        has_missing_product_id::boolean as has_missing_product_id,
        has_missing_currency::boolean as has_missing_currency,
        has_invalid_price::boolean as has_invalid_price,
        has_negative_price::boolean as has_negative_price,
        has_unknown_stock_status::boolean as has_unknown_stock_status,
        has_missing_valid_from::boolean as has_missing_valid_from,
        has_invalid_valid_from::boolean as has_invalid_valid_from,
        has_invalid_last_updated_at::boolean as has_invalid_last_updated_at,
        is_duplicate_business_key::boolean as is_duplicate_business_key,

        source_file_name::text as source_file_name,
        ingested_at::timestamp as ingested_at,
        run_date::date as run_date

    from source_supplier_updates

)

select *
from staged_supplier_updates