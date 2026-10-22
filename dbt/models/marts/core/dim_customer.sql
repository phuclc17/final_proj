-- Gold: chieu khach hang (chi kenh App moi dinh danh duoc khach).
-- Thuoc tinh co dinh: ngay/chi nhanh/nguon cua don dau tien. Chi so RFM tinh o mart, khong luu o chieu.
select
    customer_id,
    min(business_date)                                                           as first_order_date,
    arg_min(branch_id, created_at_local)                                         as first_branch_id,
    arg_min(utm_source, created_at_local)                                        as acquisition_source,
    arg_min(device_platform, created_at_local)                                   as first_device_platform
from {{ ref('stg_app__orders') }}
where customer_id is not null
group by customer_id
