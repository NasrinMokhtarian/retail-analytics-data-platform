select
    order_id,
    avg(review_score::decimal(18,4)) as average_review_score,
    count(*) as review_count,
    true as has_review,
    case
        when max(
            case
                when review_comment_title is not null
                  or review_comment_message is not null
                then 1 else 0
            end
        ) = 1 then true else false
    end as has_comment,
    max(review_creation_date) as latest_review_date
from {{ ref('stg_order_reviews') }}
group by 1
