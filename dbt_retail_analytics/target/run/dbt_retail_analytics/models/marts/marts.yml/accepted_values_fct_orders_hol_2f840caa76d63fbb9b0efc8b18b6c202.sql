
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        holiday_window_type as value_field,
        count(*) as n_records

    from "retail_analytics"."dbt_mart"."fct_orders_holiday_context"
    group by holiday_window_type

)

select *
from all_values
where value_field not in (
    'Non-holiday period','Holiday date','Before holiday','After holiday'
)



  
  
      
    ) dbt_internal_test