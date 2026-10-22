{{ config(schema='silver_work') }}
-- Giai quyet dinh danh mon: ma san pham cua ung dung ("PID-5979DD", "Gà Giòn Miếng Đơn")
-- -> ma mon cua tru so (1, "Ga Gion Mieng Don"), khop theo ten da chuan hoa.
with catalog as (
    select product_ref, any_value(product_name) as product_name, any_value(product_name_norm) as product_name_norm
    from {{ ref('stg_master__app_catalog') }}
    group by product_ref
),

menu as (
    select distinct item_id, item_name_norm from {{ ref('stg_master__menu_items') }}
)

select
    c.product_ref,
    c.product_name,
    m.item_id,
    case when m.item_id is not null then 'khop_ten_chuan_hoa' end as match_method
from catalog c
left join menu m on c.product_name_norm = m.item_name_norm
