
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select holiday_window_type
from "retail_analytics"."dbt_mart"."fct_orders_holiday_context"
where holiday_window_type is null



  
  
      
    ) dbt_internal_test