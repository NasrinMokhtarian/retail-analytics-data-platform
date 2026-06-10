
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with all_values as (

    select
        review_sentiment_group as value_field,
        count(*) as n_records

    from "retail_analytics"."dbt_mart"."fct_reviews"
    group by review_sentiment_group

)

select *
from all_values
where value_field not in (
    'positive','neutral','negative','unknown'
)



  
  
      
    ) dbt_internal_test