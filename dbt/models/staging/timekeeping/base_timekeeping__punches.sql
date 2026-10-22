{{ config(schema='silver_work') }}
-- Doc log may cham cong, gan nhan loi. Luot quet trung (cung nhan vien, cung loai, cach nhau < 5 phut)
-- la loi ky thuat cua may -> cach ly. Thieu luot quet ra KHONG phai loi ky thuat -> xu ly o bang ca lam viec.
with src as (
    select * from {{ source('bronze', 'timekeeping_punches') }}
),

parsed as (
    select
        try_cast(employee_code as integer)                        as staff_id,
        branch_code,
        event_type,
        try_strptime(event_time, '%Y-%m-%d %H:%M:%S')             as event_at,
        device_id,
        verification_method,
        _source_file, _row_number, _batch_id
    from src
)

select
    p.*,
    m.branch_id,
    case
        when p.staff_id is null                                   then 'thieu_ma_nhan_vien'
        when p.event_at is null                                   then 'thoi_gian_khong_doc_duoc'
        when m.branch_id is null                                  then 'khong_anh_xa_duoc_chi_nhanh'
        when p.event_type not in ('CHECK_IN', 'CHECK_OUT')        then 'loai_su_kien_khong_hop_le'
        when date_diff('second',
                       lag(p.event_at) over (partition by p.staff_id, p.event_type order by p.event_at),
                       p.event_at) < 300                          then 'quet_trung'
    end as dq_issue
from parsed p
left join {{ ref('branch_code_map') }} m on p.branch_code = m.timekeeping_branch_code
