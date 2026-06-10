
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    product_category_name as unique_field,
    count(*) as n_records

from "retail_analytics"."dbt_staging"."stg_product_category_translation"
where product_category_name is not null
group by product_category_name
having count(*) > 1



  
  
      
    ) dbt_internal_test