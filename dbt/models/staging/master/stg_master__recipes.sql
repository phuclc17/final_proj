-- Cong thuc mon: dinh muc nguyen lieu cho 1 phan (ban chup moi nhat). Combo duoc trien khai o tang Gold.
select
    cast(item_id as integer)         as item_id,
    cast(ingredient_id as integer)   as ingredient_id,
    cast(qty_per_unit as double)     as qty_per_unit
from {{ source('bronze', 'master_recipes') }}
qualify {{ snapshot_date_from_file('_source_file') }} = max({{ snapshot_date_from_file('_source_file') }}) over ()
