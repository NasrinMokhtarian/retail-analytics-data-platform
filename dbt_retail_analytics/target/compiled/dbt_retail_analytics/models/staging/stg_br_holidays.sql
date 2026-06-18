with source_holidays as (select * from "retail_analytics"."raw"."br_holidays"),
staged_holidays as (
    select
    holiday_date::date as holiday_date,
    holiday_name::text as holiday_name,
    holiday_local_name::text as holiday_local_name,
    upper(trim(country_code::text)) as country_code,

    is_fixed::boolean as is_fixed,
    is_global::boolean as is_global,

    counties::text as counties,
    launch_year::integer as launch_year,
    holiday_types::text as holiday_types,
    source_system::text as source_system,
    source_file_name::text as source_file_name,
    extracted_at::timestamp as extracted_at,
    run_date::date as run_date
    from source_holidays
)
select * from staged_holidays