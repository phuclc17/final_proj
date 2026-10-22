-- Moi anh chup danh muc mon tu tru so (1 dong / mon / ngay chup). Tang Gold dung de dung lich su gia (SCD2).
select
    cast(item_id as integer)                    as item_id,
    item_name,
    {{ normalize_name('item_name') }}           as item_name_norm,
    category,
    cast(price as bigint)                       as price,
    cast(standard_cost as bigint)               as standard_cost,
    {{ snapshot_date_from_file('_source_file') }} as snapshot_date,
    _source_file,
    _row_number
from {{ source('bronze', 'master_menu_items') }}
