{{ config(schema='silver_work') }}
-- Hop nhat 2 mau so nhap kho ve 1 cau truc, phan loai dong va gan nhan loi.
--   Mau A (phieu tieng Viet): dong tieu de -> _doc_line_k; co dong "Tong cong" va dong chu ky o cuoi
--   Mau B (bang tieng Anh, CN3/6/9): so luong dinh don vi "53.6kg"; chi nhanh lay tu thu muc tep
with form_a as (
    select
        'A'                                                                       as template,
        case
            when try_cast(stt as integer) is not null then 'data'
            when ten_nguyen_lieu = 'Tổng cộng'        then 'dong_tong_cong'
            else 'dong_chu_ky'
        end                                                                       as row_kind,
        ten_nguyen_lieu                                                           as raw_name,
        dvt                                                                       as raw_unit,
        so_luong                                                                  as raw_qty,
        don_gia                                                                   as raw_unit_price,
        han_su_dung                                                               as raw_expiry,
        nha_cung_cap                                                              as supplier,
        trim(regexp_extract(_doc_line_2, 'Chi nhánh:\s*(.*)$', 1))                as branch_name_on_doc,
        try_strptime(regexp_extract(_doc_line_3, '(\d{2}/\d{2}/\d{4})', 1), '%d/%m/%Y') as receipt_ts,
        regexp_extract(_source_file, '/(CN\d+)/', 1)                              as folder,
        _source_file, _row_number, _batch_id
    from {{ source('bronze', 'warehouse_receipts_form') }}
),

form_b as (
    select
        'B'                                                    as template,
        'data'                                                 as row_kind,
        item                                                   as raw_name,
        regexp_extract(quantity, '([^0-9.\s]+)\s*$', 1)        as raw_unit,
        regexp_extract(quantity, '^\s*([0-9.]+)', 1)           as raw_qty,
        unit_price                                             as raw_unit_price,
        cast(null as varchar)                                  as raw_expiry,
        supplier,
        cast(null as varchar)                                  as branch_name_on_doc,
        try_strptime("date", '%Y-%m-%d')                       as receipt_ts,
        regexp_extract(_source_file, '/(CN\d+)/', 1)           as folder,
        _source_file, _row_number, _batch_id
    from {{ source('bronze', 'warehouse_receipts_table') }}
),

unioned as (
    select * from form_a
    union all
    select * from form_b
),

resolved as (
    select
        u.*,
        coalesce(b.branch_id, f.branch_id)                      as branch_id,
        b.branch_id is not null and f.branch_id is not null
            and b.branch_id != f.branch_id                      as branch_conflict,
        cast(u.receipt_ts as date)                              as receipt_date,
        try_cast(u.raw_qty as double)                           as quantity,
        {{ normalize_name('u.raw_unit') }}                      as unit,
        try_cast(u.raw_unit_price as bigint)                    as unit_price,
        cast(try_strptime(u.raw_expiry, '%d/%m/%Y') as date)    as expiry_date
    from unioned u
    left join {{ ref('stg_master__branches') }} b on u.branch_name_on_doc = b.branch_name
    left join {{ ref('branch_code_map') }} f on u.folder = f.warehouse_folder
)

select * from resolved
