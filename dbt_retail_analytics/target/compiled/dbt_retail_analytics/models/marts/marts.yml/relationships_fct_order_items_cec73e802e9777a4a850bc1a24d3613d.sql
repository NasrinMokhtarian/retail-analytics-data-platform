
    
    

with child as (
    select seller_id as from_field
    from "retail_analytics"."dbt_mart"."fct_order_items"
    where seller_id is not null
),

parent as (
    select seller_id as to_field
    from "retail_analytics"."dbt_mart"."dim_sellers"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null


