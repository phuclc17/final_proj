-- Moi anh chup danh sach nhan vien (1 dong / nhan vien / ngay chup). Tang Gold dung de dung lich su vai tro, luong (SCD2).
select
    cast(staff_id as integer)                   as staff_id,
    staff_name,
    cast(branch_id as integer)                  as branch_id,
    role,
    cast(hourly_wage as bigint)                 as hourly_wage,
    cast(hire_date as date)                     as hire_date,
    {{ snapshot_date_from_file('_source_file') }} as snapshot_date,
    _source_file,
    _row_number
from {{ source('bronze', 'master_staff') }}
