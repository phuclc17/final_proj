-- SCD2: cac phien ban cua cung 1 mon / 1 nhan vien khong duoc chong lan va khong de ho thoi gian.
with v as (
    select 'menu' as dim, item_id as nk, valid_from, valid_to from {{ ref('dim_menu_item') }}
    union all
    select 'employee', staff_id, valid_from, valid_to from {{ ref('dim_employee') }}
),

ordered as (
    select *, lead(valid_from) over (partition by dim, nk order by valid_from) as next_from
    from v
)

select *
from ordered
where valid_to < valid_from
   or (next_from is not null and next_from <> valid_to + interval 1 day)
   or (next_from is null and valid_to <> date '9999-12-31')
