with orders as (
    select 
    order_id,
    customer_id,
    order_status,
    order_purchase_date,
    is_delivered,
    days_to_customer_delivery,
    delivery_delay_days,
    is_late_delivery
    from {{ref('fct_orders')}}
),
reviews_aggregated as (
    select order_id,count(*) as review_count,avg(review_score) as average_review_score
    from {{ref('fct_reviews')}}
    group by order_id
),
order_items_aggregated as (
    select 
    order_id,
    count(*) as order_item_count,
    sum(price) as order_item_revenue,
    sum(freight_value) as order_freight_value,
    sum(total_item_value) as order_total_value

    from {{ ref('fct_order_items') }}
    group by order_id
),
 holiday_candidates as (
    select 
    orders.order_id,
    holidays.holiday_date,
    holidays.holiday_name,
    holidays.holiday_local_name,
    holidays.holiday_group,
    holidays.is_retail_relevant,
    holidays.holiday_date - orders.order_purchase_date as days_to_holiday,
    abs(holidays.holiday_date - orders.order_purchase_date) as absolute_days_to_holiday,
    row_number() over (
        partition by orders.order_id order by  abs(holidays.holiday_date - orders.order_purchase_date),holidays.holiday_date
    ) as holiday_rank

    from orders 
    inner join {{ref('dim_br_holidays')}} as holidays
    on holidays.holiday_date between orders.order_purchase_date - interval '7 days'
    and orders.order_purchase_date + interval '7 days'

 ),
nearest_holiday as (
 select
        order_id,
        holiday_date as nearest_holiday_date,
        holiday_name as nearest_holiday_name,
        holiday_local_name as nearest_holiday_local_name,
        holiday_group as nearest_holiday_group,
        is_retail_relevant as nearest_holiday_is_retail_relevant,
        days_to_holiday,
        absolute_days_to_holiday

    from holiday_candidates
    where holiday_rank = 1

),
final as (
    select orders.order_id,
    orders.customer_id,
    orders.order_status,
    orders.order_purchase_date,
    extract(year from orders.order_purchase_date)::integer as order_year,
    extract(month from orders.order_purchase_date)::integer as order_month,
    extract(day from orders.order_purchase_date)::integer as order_day,
    coalesce(order_items_aggregated.order_item_count, 0) as order_item_count,
    coalesce(order_items_aggregated.order_item_revenue, 0) as order_item_revenue,
    coalesce(order_items_aggregated.order_freight_value, 0) as order_freight_value,
    coalesce(order_items_aggregated.order_total_value, 0) as order_total_value,
    orders.is_delivered,
    orders.days_to_customer_delivery,
    orders.delivery_delay_days,
    orders.is_late_delivery,
    reviews_aggregated.review_count,
    reviews_aggregated.average_review_score,
    nearest_holiday.nearest_holiday_date,
    nearest_holiday.nearest_holiday_name,
    nearest_holiday.nearest_holiday_local_name,
    nearest_holiday.nearest_holiday_group,
    nearest_holiday.nearest_holiday_is_retail_relevant,
    nearest_holiday.days_to_holiday,
    nearest_holiday.absolute_days_to_holiday,
    case when nearest_holiday.nearest_holiday_date is null then false else true end as is_near_holiday,
    case when nearest_holiday.days_to_holiday = 0 then true else false end as is_holiday_date,
    case when nearest_holiday.nearest_holiday_date is null then 'Non-holiday period' 
        when nearest_holiday.days_to_holiday = 0 then 'Holiday date'
        when nearest_holiday.days_to_holiday > 0 then 'Before holiday'
        when nearest_holiday.days_to_holiday < 0 then 'After holiday'
        end as holiday_window_type
    from orders

    left join order_items_aggregated
        on orders.order_id = order_items_aggregated.order_id

    left join reviews_aggregated
        on orders.order_id = reviews_aggregated.order_id

    left join nearest_holiday
        on orders.order_id = nearest_holiday.order_id

)

select *
from final
