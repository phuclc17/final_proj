-- Gold: chieu nguyen lieu. fresh = hang tuoi (han dung ngan) -> nhom theo doi hao hut (P2).
select
    ingredient_id,
    ingredient_code,
    ingredient_name,
    unit,
    ingredient_category,
    ingredient_category = 'fresh' as is_fresh,
    shelf_life_days,
    standard_unit_cost
from {{ ref('stg_master__ingredients') }}
