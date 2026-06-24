SELECT
    holiday_window_type,
    COUNT(*) AS order_count,
    ROUND(SUM(order_item_revenue)::numeric, 2) AS total_revenue,
    ROUND(AVG(order_item_revenue)::numeric, 2) AS avg_order_revenue,
    ROUND(AVG(average_review_score)::numeric, 2) AS avg_review_score,
    ROUND(AVG(days_to_customer_delivery)::numeric, 2) AS avg_delivery_days,
    ROUND(
        AVG(
            CASE
                WHEN is_late_delivery = true THEN 1.0
                WHEN is_late_delivery = false THEN 0.0
                ELSE NULL
            END
        )::numeric * 100,
        2
    ) AS late_delivery_rate_pct
FROM dbt_mart.fct_orders_holiday_context
GROUP BY holiday_window_type
ORDER BY order_count DESC;


SELECT
    order_id,
    order_purchase_date,
    nearest_holiday_date,
    nearest_holiday_name,
    holiday_window_type,
    days_to_holiday,
    order_item_revenue,
    average_review_score,
    is_late_delivery
FROM dbt_mart.fct_orders_holiday_context
WHERE is_near_holiday = true
ORDER BY order_purchase_date
LIMIT 50;