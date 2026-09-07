with bounds as (
    select
        min(cast(order_purchase_timestamp as date)) as min_date,
        max(
            coalesce(
                cast(order_delivered_customer_date as date),
                cast(order_estimated_delivery_date as date),
                cast(order_purchase_timestamp as date)
            )
        ) as max_date
    from {{ ref('stg_orders') }}
),

numbers as (
    select
        row_number() over () - 1 as n
    from {{ ref('stg_geolocation') }}
    limit 2000
),

dates as (
    select
        dateadd(day, n, min_date)::date as date_day
    from bounds
    cross join numbers
    where dateadd(day, n, min_date)::date <= max_date
)

select
    d.date_day,
    extract(year from d.date_day)::integer as year,
    extract(quarter from d.date_day)::integer as quarter,
    extract(month from d.date_day)::integer as month,
    trim(to_char(d.date_day, 'Month')) as month_name,
    extract(week from d.date_day)::integer as week,
    extract(dow from d.date_day)::integer as day_of_week,
    trim(to_char(d.date_day, 'Day')) as day_name,

    case
        when extract(dow from d.date_day) in (0, 6) then true
        else false
    end as is_weekend,

    case
        when h.holiday_date is not null then true
        else false
    end as is_holiday,

    h.holiday_name,
    h.holiday_local_name,
    h.holiday_types as holiday_type

from dates d

left join {{ ref('stg_holidays') }} h
    on d.date_day = h.holiday_date