-- Silver: bao cao doi soat ShopeeFood (Excel tieng Viet) theo chi nhanh x tuan, cung cau truc voi GrabFood.
-- Ky doi soat nam o dong tieu de phia tren bang: _doc_line_2 = "Kỳ đối soát: 11/03/2024 - 17/03/2024".
-- ShopeeFood khong co ngay tao bao cao -> report_generated_date de trong.
with src as (
    select * from {{ source('bronze', 'shopee_settlement') }}
)

select
    'SHOPEEFOOD'                                                                                   as platform,
    m.branch_id,
    cast(strptime(regexp_extract(src._doc_line_2, '(\d{2}/\d{2}/\d{4})\s*-', 1), '%d/%m/%Y') as date) as week_start,
    cast(strptime(regexp_extract(src._doc_line_2, '-\s*(\d{2}/\d{2}/\d{4})', 1), '%d/%m/%Y') as date) as week_end,
    cast(null as date)                                       as report_generated_date,
    cast(src.doanh_thu_mon_vnd as bigint)                    as gross_sales,
    cast(src.so_don_hoan_thanh as integer)                   as orders_completed,
    cast(src.so_don_huy as integer)                          as orders_cancelled,
    cast(src.phi_dich_vu_vnd as bigint)                      as commission,
    cast(src.phi_quang_cao_vnd as bigint)                    as ads_spend,
    cast(src.khuyen_mai_do_quan_tai_tro_vnd as bigint)       as merchant_promo,
    cast(src.dieu_chinh_vnd as bigint)                       as adjustment,
    cast(src.thuc_nhan_vnd as bigint)                        as net_payout,
    cast(src.thoi_gian_chuan_bi_tb_phut as double)           as avg_prep_min,
    cast(src.danh_gia as double)                             as store_rating,
    cast(src.phi_dich_vu_vnd as double) / nullif(cast(src.doanh_thu_mon_vnd as double), 0) as effective_commission_rate,
    src._source_file,
    src._row_number,
    src._batch_id
from src
left join {{ ref('branch_code_map') }} m on src.ma_cua_hang = m.shopee_store_code
