
  create view "retail_analytics"."dbt_mart"."dim_br_holidays__dbt_tmp"
    
    
  as (
    with holidays as (
    select * from "retail_analytics"."dbt_staging"."stg_br_holidays"
),
final as (
    select
     holiday_date,
     extract(year from holiday_date)::integer as holiday_year,
     extract(month from holiday_date)::integer as holiday_month,
     extract(day from holiday_date)::integer as holiday_day,
     holiday_name,
     holiday_local_name,
     country_code,

     is_fixed,
     is_global,

     counties,
     launch_year,
     holiday_types,

     case 
     when lower(holiday_name) like '%christmas%' then 'Christmas'
     when lower(holiday_name) like '%new year%' then 'New Year'
     when lower(holiday_name) like '%good friday%' then 'Easter period'
     when lower(holiday_name) like '%easter%' then 'Easter period'
     when lower(holiday_name) like '%carnival%' then 'Carnival'
     when lower(holiday_name) like '%independence%' then 'National'
     else 'Other'
     end as holiday_group,

     case when lower(holiday_name) in (
                'christmas day',
                'new year''s day',
                'good friday',
                'independence day'
            )
            then true
            else false
        end as is_retail_relevant,
            
    source_system,
        source_file_name,
        extracted_at,
        run_date

    from holidays   
)

select * from final
  );