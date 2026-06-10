
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select needs_business_review
from "retail_analytics"."dbt_mart"."fct_supplier_product_updates"
where needs_business_review is null



  
  
      
    ) dbt_internal_test