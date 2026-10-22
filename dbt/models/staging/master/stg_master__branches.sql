-- Danh muc chi nhanh, ban chup moi nhat.
select
    cast(branch_id as integer)      as branch_id,
    branch_name,
    district,
    store_class,
    cast(latitude as double)        as latitude,
    cast(longitude as double)       as longitude,
    cast(open_date as date)         as open_date,
    {{ snapshot_date_from_file('_source_file') }} as snapshot_date
from {{ source('bronze', 'master_branches') }}
qualify {{ snapshot_date_from_file('_source_file') }} = max({{ snapshot_date_from_file('_source_file') }}) over ()
