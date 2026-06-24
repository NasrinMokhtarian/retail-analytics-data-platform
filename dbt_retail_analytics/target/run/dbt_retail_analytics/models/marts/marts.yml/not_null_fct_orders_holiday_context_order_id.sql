
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select order_id
from "retail_analytics"."dbt_mart"."fct_orders_holiday_context"
where order_id is null



  
  
      
    ) dbt_internal_test