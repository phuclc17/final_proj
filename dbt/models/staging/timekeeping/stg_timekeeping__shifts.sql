-- Silver: ghep luot vao - ra thanh ca lam viec (1 nhan vien x 1 ngay).
-- Ca thieu luot ra: GIU LAI, gan co is_missing_checkout, so gio de trong (khong tu gan 8 gio).
-- Tang Gold quyet dinh cach uoc luong khi tinh gio cong, va bao cao ty le ca thieu luot ra.
with ins as (
    select staff_id, branch_id, cast(event_at as date) as work_date, min(event_at) as check_in_at
    from {{ ref('stg_timekeeping__punches') }}
    where event_type = 'CHECK_IN'
    group by all
),

outs as (
    select staff_id, cast(event_at as date) as work_date, max(event_at) as check_out_at
    from {{ ref('stg_timekeeping__punches') }}
    where event_type = 'CHECK_OUT'
    group by all
)

select
    i.staff_id || '-' || i.work_date                              as shift_key,
    i.staff_id,
    i.branch_id,
    i.work_date,
    case when hour(i.check_in_at) < 12 then 'SANG' else 'TOI' end as shift_name,
    i.check_in_at,
    o.check_out_at,
    o.check_out_at is null                                       as is_missing_checkout,
    case when o.check_out_at > i.check_in_at
         then date_diff('minute', i.check_in_at, o.check_out_at) / 60.0 end as hours_worked
from ins i
left join outs o using (staff_id, work_date)
