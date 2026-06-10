with reviews as (

    select *
    from "retail_analytics"."dbt_staging"."stg_order_reviews"

),

final as (

    select
        review_id,
        order_id,
        review_score,
        review_comment_title,
        review_comment_message,

        review_creation_date,
        review_answer_timestamp,

        review_creation_date::date as review_creation_day,

        case
            when review_score >= 4 then 'positive'
            when review_score = 3 then 'neutral'
            when review_score <= 2 then 'negative'
            else 'unknown'
        end as review_sentiment_group,

        source_file_name,
        ingested_at,
        run_date

    from reviews

)

select *
from final