
  create view "retail_analytics"."dbt_staging"."stg_order_reviews__dbt_tmp"
    
    
  as (
    with source_order_reviews as (

    select *
    from "retail_analytics"."raw"."olist_order_reviews"

),

staged_order_reviews as (

    select
        review_id::text as review_id,
        order_id::text as order_id,
        review_score::integer as review_score,
        review_comment_title::text as review_comment_title,
        review_comment_message::text as review_comment_message,

        review_creation_date::timestamp as review_creation_date,
        review_answer_timestamp::timestamp as review_answer_timestamp,

        source_file_name::text as source_file_name,
        ingested_at::timestamp as ingested_at,
        run_date::date as run_date

    from source_order_reviews

)

select *
from staged_order_reviews
  );