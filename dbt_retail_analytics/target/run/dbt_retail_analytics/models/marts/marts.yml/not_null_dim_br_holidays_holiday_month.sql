
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select holiday_month
from "retail_analytics"."dbt_mart"."dim_br_holidays"
where holiday_month is null



  
  
      
    ) dbt_internal_test