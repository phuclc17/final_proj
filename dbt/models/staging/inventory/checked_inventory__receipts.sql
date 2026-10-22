{{ config(schema='silver_work') }}
-- Gan ma nguyen lieu va nhan loi cho tung dong so nhap kho.
-- "Nghi go gam vao cot kg": so luong lon hon 20 lan trung vi cua cung chi nhanh x nguyen lieu.
with base as (
    select r.*, {{ normalize_name('r.raw_name') }} as name_norm
    from {{ ref('base_inventory__receipts') }} r
),

mapped as (
    select b.*, m.ingredient_id, m.match_method, i.unit as master_unit
    from base b
    left join {{ ref('map_ingredient_name') }} m using (name_norm)
    left join {{ ref('stg_master__ingredients') }} i using (ingredient_id)
),

with_median as (
    select
        *,
        median(quantity) over (partition by branch_id, ingredient_id) as median_qty
    from mapped
    where row_kind = 'data'
)

select
    *,
    case
        when branch_id is null                       then 'khong_anh_xa_duoc_chi_nhanh'
        when branch_conflict                         then 'chi_nhanh_tieu_de_khac_thu_muc'
        when receipt_date is null                    then 'ngay_nhap_khong_doc_duoc'
        when ingredient_id is null                   then 'khong_nhan_dien_duoc_nguyen_lieu'
        when quantity is null or quantity <= 0       then 'so_luong_khong_hop_le'
        when unit != master_unit                     then 'don_vi_khong_khop_danh_muc'
        when unit = 'kg' and quantity > 20 * median_qty then 'nghi_go_gam_vao_cot_kg'
    end as dq_issue
from with_median
