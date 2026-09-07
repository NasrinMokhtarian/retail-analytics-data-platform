select
    customer_unique_id,
    min(order_purchase_timestamp) as first_order_at,
    max(order_purchase_timestamp) as last_order_at,
    count(distinct order_id) as orders,
    sum(coalesce(payment_total, 0))::decimal(18,2) as customer_spend,
    avg(payment_total)::decimal(18,2) as avg_order_value,
    avg(average_review_score)::decimal(18,2) as avg_review_score,
    max(primary_payment_type) as representative_payment_type,
    max(customer_city) as customer_city,
    max(customer_state) as customer_state,
    case when count(distinct order_id) > 1 then true else false end as is_repeat_customer
from {{ ref('fct_orders') }}
where customer_unique_id is not null
group by 1
