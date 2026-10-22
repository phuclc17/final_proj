-- Gold: bang su kien KIEM KE (anh chup dinh ky, 2 tuan/lan), 1 dong / chi nhanh / nguyen lieu / lan dem.
-- O bo trong (khong dem) giu lai voi is_not_counted = true, KHONG coi la ton = 0.
select
    c.count_key,
    c.branch_id,
    c.count_date                                  as date_day,
    c.ingredient_id,
    c.counted_qty,
    c.is_not_counted,
    c.counted_by,
    i.standard_unit_cost,
    round(c.counted_qty * i.standard_unit_cost)   as counted_value
from {{ ref('stg_stock__counts') }} c
left join {{ ref('dim_ingredient') }} i using (ingredient_id)
