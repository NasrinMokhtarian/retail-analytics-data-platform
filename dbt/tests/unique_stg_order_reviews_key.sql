select
    review_id,
    order_id,
    count(*) as row_count
from {{ ref('stg_order_reviews') }}
group by 1, 2
having count(*) > 1
