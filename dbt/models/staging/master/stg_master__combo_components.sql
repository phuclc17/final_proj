-- Thanh phan cua combo (ban chup moi nhat).
select
    cast(combo_item_id as integer)       as combo_item_id,
    cast(component_item_id as integer)   as component_item_id,
    cast(quantity as double)             as quantity
from {{ source('bronze', 'master_combo_components') }}
qualify {{ snapshot_date_from_file('_source_file') }} = max({{ snapshot_date_from_file('_source_file') }}) over ()
