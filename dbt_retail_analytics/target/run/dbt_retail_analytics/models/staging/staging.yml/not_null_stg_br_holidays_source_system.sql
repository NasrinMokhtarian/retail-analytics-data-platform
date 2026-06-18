
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select source_system
from "retail_analytics"."dbt_staging"."stg_br_holidays"
where source_system is null



  
  
      
    ) dbt_internal_test