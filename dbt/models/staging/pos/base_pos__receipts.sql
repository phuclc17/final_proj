{{ config(schema='silver_work') }}
-- Doc toan bo hoa don POS tu Bronze, hop nhat 2 phien ban phan mem, gan nhan loi (dq_issue) cho tung dong.
-- KHONG bo dong nao: dong hop le -> stg_pos__receipts, dong loi -> silver_quarantine.
--   v3.2.1: txn_time "12/04/2024 07:11:22", tien la so, cot tong tien "total_paid"
--   v2.8.0: txn_time "2024-04-12T07:10:59", tien la chuoi "89.000", cot tong tien "grand_total"

with parsed as (
    select * exclude (_ingested_at) from {{ ref('parsed_pos__receipts') }}
),

checked as (
    select
        p.*,
        m.branch_id,
        cast(p.txn_at as date)                                         as business_date,
        date_diff('second', p.txn_at, p.void_at) / 60.0                as minutes_to_void,
        row_number() over (partition by p.receipt_no order by p._source_file, p._row_number) as dup_rank
    from parsed p
    left join {{ ref('branch_code_map') }} m using (pos_terminal_prefix)
)

select
    * exclude (dup_rank, n_items_json),
    case
        when receipt_no is null                then 'thieu_so_hoa_don'
        when dup_rank > 1                      then 'trung_so_hoa_don'
        when txn_at is null                    then 'thoi_gian_khong_doc_duoc'
        when branch_id is null                 then 'khong_anh_xa_duoc_chi_nhanh'
        when total_paid is null                then 'tong_tien_khong_doc_duoc'
        when total_paid < 0                    then 'tong_tien_am'
        when n_items_json = 0 then 'hoa_don_khong_co_mon'
    end as dq_issue
from checked
