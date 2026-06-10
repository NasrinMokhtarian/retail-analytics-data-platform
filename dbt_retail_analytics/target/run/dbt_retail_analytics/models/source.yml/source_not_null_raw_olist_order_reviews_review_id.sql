
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select review_id
from "retail_analytics"."raw"."olist_order_reviews"
where review_id is null



  
  
      
    ) dbt_internal_test