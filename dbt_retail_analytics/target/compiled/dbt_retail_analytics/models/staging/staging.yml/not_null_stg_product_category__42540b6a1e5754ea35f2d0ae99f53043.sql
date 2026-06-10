
    
    



select product_category_name_english
from "retail_analytics"."dbt_staging"."stg_product_category_translation"
where product_category_name_english is null


