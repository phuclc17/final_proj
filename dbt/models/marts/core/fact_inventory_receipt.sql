-- Gold: bang su kien NHAP KHO, 1 dong / dong phieu nhap (da khop ma nguyen lieu o Silver).
select
    receipt_line_id,
    branch_id,
    receipt_date                                  as date_day,
    cast(ingredient_id as integer)                as ingredient_id,
    ingredient_match_method,
    quantity,
    unit,
    unit_price,
    line_amount,
    expiry_date,
    supplier
from {{ ref('stg_inventory__receipt_lines') }}
