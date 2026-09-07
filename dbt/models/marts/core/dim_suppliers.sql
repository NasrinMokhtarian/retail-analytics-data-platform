with ranked as (
    select
        supplier_id,
        supplier_name,
        last_updated_at,
        row_number() over (
            partition by supplier_id
            order by last_updated_at desc nulls last, supplier_name
        ) as rn
    from {{ ref('int_supplier_product_latest') }}
    where supplier_id is not null
)
select
    supplier_id,
    supplier_name
from ranked
where rn = 1
