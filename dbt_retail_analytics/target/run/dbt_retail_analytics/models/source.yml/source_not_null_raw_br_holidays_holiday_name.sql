
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select holiday_name
from "retail_analytics"."raw"."br_holidays"
where holiday_name is null



  
  
      
    ) dbt_internal_test