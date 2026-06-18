
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select run_date
from "retail_analytics"."dbt_staging"."stg_br_holidays"
where run_date is null



  
  
      
    ) dbt_internal_test