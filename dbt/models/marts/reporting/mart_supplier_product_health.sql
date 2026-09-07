select
    s.supplier_id,
    s.supplier_name,
    s.product_id,
    s.supplier_product_code,
    s.updated_price as supplier_price,
    s.currency as supplier_currency,
    s.stock_status,
    s.valid_from,
    s.last_updated_at as supplier_last_updated_at,

    p.units_sold as product_units_sold,
    p.orders_with_product,
    p.seller_count,
    p.marketplace_revenue as product_marketplace_revenue,
    p.avg_marketplace_price,

    case
        when p.avg_marketplace_price is not null
         and s.updated_price is not null
        then (p.avg_marketplace_price - s.updated_price)::decimal(18,2)
    end as avg_marketplace_vs_supplier_price,

    s.has_missing_product_id,
    s.has_missing_currency,
    s.has_invalid_price,
    s.has_negative_price,
    s.has_unknown_stock_status,
    s.has_missing_valid_from,
    s.has_invalid_valid_from,
    s.has_invalid_last_updated_at,
    s.is_duplicate_business_key,

   case
    when s.last_updated_at is null then true
    when datediff(day, s.last_updated_at, getdate()) > 30 then true
    else false
end as is_stale_supplier_update

from {{ ref('int_supplier_product_latest') }} s
left join {{ ref('int_product_sales') }} p
  on s.product_id = p.product_id
