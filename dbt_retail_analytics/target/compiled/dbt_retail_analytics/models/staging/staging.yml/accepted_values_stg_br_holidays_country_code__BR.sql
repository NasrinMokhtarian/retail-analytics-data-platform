
    
    

with all_values as (

    select
        country_code as value_field,
        count(*) as n_records

    from "retail_analytics"."dbt_staging"."stg_br_holidays"
    group by country_code

)

select *
from all_values
where value_field not in (
    'BR'
)


