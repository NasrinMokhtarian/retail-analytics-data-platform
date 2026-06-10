
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select seller_state
from "retail_analytics"."dbt_staging"."stg_sellers"
where seller_state is null



  
  
      
    ) dbt_internal_test