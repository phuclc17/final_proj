{{ config(schema='silver_work') }}
-- Doc toan bo don ung dung tu Bronze, doi gio UTC -> gio Viet Nam (UTC+7), gan nhan loi dq_issue.
with parsed as (
    select * exclude (_ingested_at) from {{ ref('parsed_app__orders') }}
),

checked as (
    select
        p.*,
        m.branch_id,
        p.created_at_utc + interval 7 hour                          as created_at_local,
        p.ready_at_utc + interval 7 hour                            as ready_at_local,
        cast(p.created_at_utc + interval 7 hour as date)            as business_date,
        date_diff('second', p.created_at_utc, p.ready_at_utc) / 60.0 as prep_minutes,
        row_number() over (partition by p.order_id order by p._source_file, p._row_number) as dup_rank
    from parsed p
    left join {{ ref('branch_code_map') }} m using (app_branch_code)
)

select
    * exclude (dup_rank, n_items_json),
    case
        when order_id is null                  then 'thieu_ma_don'
        when dup_rank > 1                      then 'trung_ma_don'
        when created_at_utc is null            then 'thoi_gian_khong_doc_duoc'
        when branch_id is null                 then 'khong_anh_xa_duoc_chi_nhanh'
        when total_amount is null              then 'tong_tien_khong_doc_duoc'
        when n_items_json = 0 then 'don_khong_co_mon'
    end as dq_issue
from checked
