-- Gold: bang su kien CA LAM, 1 dong / nhan vien / ngay / ca (ghep tu cham cong o Silver).
-- Ca thieu gio ra (quen quet): KHONG am tham gan 8 gio. Gio cong de tinh chi phi duoc noi suy
-- bang trung vi cung ca + cung vai tro, va danh dau is_hours_imputed de bao cao minh bach.
with shifts as (
    select
        s.*,
        e.employee_sk,
        e.role,
        e.hourly_wage
    from {{ ref('stg_timekeeping__shifts') }} s
    left join {{ ref('dim_employee') }} e
        on e.staff_id = s.staff_id
       and s.work_date between e.valid_from and e.valid_to
),

typical as (
    select shift_name, role, median(hours_worked) as median_hours
    from shifts
    where hours_worked is not null
    group by all
)

select
    s.shift_key,
    s.staff_id,
    s.employee_sk,
    s.branch_id,
    s.work_date                                                      as date_day,
    s.shift_name,
    s.role,
    s.check_in_at,
    s.check_out_at,
    s.is_missing_checkout,
    s.hours_worked,
    s.hours_worked is null                                           as is_hours_imputed,
    coalesce(s.hours_worked, t.median_hours)                         as hours_paid,
    s.hourly_wage,
    round(coalesce(s.hours_worked, t.median_hours) * s.hourly_wage)  as labor_cost
from shifts s
left join typical t using (shift_name, role)
