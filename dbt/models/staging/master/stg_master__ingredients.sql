-- Danh muc nguyen lieu, ban chup moi nhat.
select
    cast(ingredient_id as integer)          as ingredient_id,
    ingredient_code,
    ingredient_name,
    {{ normalize_name('ingredient_name') }} as ingredient_name_norm,
    unit,
    category                                as ingredient_category,
    cast(shelf_life_days as integer)        as shelf_life_days,
    cast(standard_unit_cost as bigint)      as standard_unit_cost
from {{ source('bronze', 'master_ingredients') }}
qualify {{ snapshot_date_from_file('_source_file') }} = max({{ snapshot_date_from_file('_source_file') }}) over ()
