select
    order_id,
    order_item_id,
    count(*) as row_count
from {{ ref('stg_order_items') }}
group by 1, 2
having count(*) > 1
