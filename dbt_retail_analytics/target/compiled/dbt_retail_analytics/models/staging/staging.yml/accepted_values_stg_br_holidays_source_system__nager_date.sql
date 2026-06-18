
    
    

with all_values as (

    select
        source_system as value_field,
        count(*) as n_records

    from "retail_analytics"."dbt_staging"."stg_br_holidays"
    group by source_system

)

select *
from all_values
where value_field not in (
    'nager_date'
)


