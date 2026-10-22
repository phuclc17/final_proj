{{ config(schema='silver_work') }}
-- Phieu kiem ke: chi nhanh, ngay, nguoi kiem nam o dong tieu de; nguyen lieu theo ma "NL01".
-- O bo trong ("chua dem") giu la gia tri thieu va gan co, KHONG thay bang 0.
with src as (
    select * from {{ source('bronze', 'stock_counts') }}
)

select
    b.branch_id,
    cast(try_strptime(regexp_extract(src._doc_line_3, '(\d{2}/\d{2}/\d{4})', 1), '%d/%m/%Y') as date) as count_date,
    trim(regexp_extract(src._doc_line_4, 'Người kiểm:\s*(.*)$', 1))  as counted_by,
    i.ingredient_id,
    src.ma_nl                                                        as ingredient_code,
    src.ten_nguyen_lieu                                              as raw_name,
    {{ normalize_name('src.dvt') }}                                  as unit,
    i.unit                                                           as master_unit,
    try_cast(src.ton_thuc_te as double)                              as counted_qty,
    try_cast(src.ton_thuc_te as double) is null                      as is_not_counted,
    src.ghi_chu                                                      as note,
    try_cast(src.stt as integer) is not null                         as is_data_row,
    src._source_file,
    src._row_number,
    src._batch_id,
    case
        when try_cast(src.stt as integer) is null then null
        when b.branch_id is null                  then 'khong_anh_xa_duoc_chi_nhanh'
        when try_strptime(regexp_extract(src._doc_line_3, '(\d{2}/\d{2}/\d{4})', 1), '%d/%m/%Y') is null then 'ngay_kiem_ke_khong_doc_duoc'
        when i.ingredient_id is null              then 'ma_nguyen_lieu_khong_ton_tai'
        when {{ normalize_name('src.dvt') }} != i.unit then 'don_vi_khong_khop_danh_muc'
    end as dq_issue
from src
left join {{ ref('stg_master__branches') }} b
    on trim(regexp_extract(src._doc_line_2, 'Chi nhánh:\s*(.*)$', 1)) = b.branch_name
left join {{ ref('stg_master__ingredients') }} i on src.ma_nl = i.ingredient_code
