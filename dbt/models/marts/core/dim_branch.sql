-- Gold: chieu chi nhanh (ban moi nhat cua danh muc) + ma chi nhanh o tung he thong nguon.
-- store_class (A/B/C) = hang cua hang, dung lam "nhom chi nhanh cung hang" khi so sanh.
select
    b.branch_id,
    b.branch_name,
    b.district,
    b.store_class,
    b.latitude,
    b.longitude,
    b.open_date,
    m.pos_terminal_prefix,
    m.app_branch_code,
    m.grab_store_name,
    m.shopee_store_code,
    m.timekeeping_branch_code
from {{ ref('stg_master__branches') }} b
left join {{ ref('branch_code_map') }} m using (branch_id)
