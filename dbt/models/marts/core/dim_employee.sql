-- Gold: chieu nhan vien, SCD loai 2 theo (chi nhanh, vai tro, luong gio).
-- Vi du: nhan vien thang chuc Thu ngan -> Quan ly ca tu 01/07 => 2 phien ban.
with snaps as (
    select
        staff_id, staff_name, branch_id, role, hourly_wage, hire_date, snapshot_date,
        md5(concat_ws('|', staff_name, branch_id, role, hourly_wage)) as row_hash
    from {{ ref('stg_master__staff') }}
),

changes as (
    select *, lag(row_hash) over (partition by staff_id order by snapshot_date) as prev_hash
    from snaps
),

versions as (
    select * from changes where prev_hash is null or prev_hash <> row_hash
)

select
    md5(staff_id || '|' || snapshot_date)                                       as employee_sk,
    staff_id,
    'NV' || lpad(cast(staff_id as varchar), 4, '0')                             as staff_code,
    staff_name,
    branch_id,
    role,
    hourly_wage,
    hire_date,
    case when row_number() over w = 1 then date '1900-01-01' else snapshot_date end as valid_from,
    coalesce(cast(lead(snapshot_date) over w - interval 1 day as date), date '9999-12-31') as valid_to,
    lead(snapshot_date) over w is null                                          as is_current
from versions
window w as (partition by staff_id order by snapshot_date)
