
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select source_file_name
from "retail_analytics"."dbt_staging"."stg_br_holidays"
where source_file_name is null



  
  
      
    ) dbt_internal_test