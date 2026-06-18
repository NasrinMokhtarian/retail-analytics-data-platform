
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        country_code as value_field,
        count(*) as n_records

    from "retail_analytics"."dbt_mart"."dim_br_holidays"
    group by country_code

)

select *
from all_values
where value_field not in (
    'BR'
)



  
  
      
    ) dbt_internal_test