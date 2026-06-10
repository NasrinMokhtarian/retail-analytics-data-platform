
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select total_item_value
from "retail_analytics"."dbt_mart"."fct_order_items"
where total_item_value is null



  
  
      
    ) dbt_internal_test