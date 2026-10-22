-- Gold: bang su kien DON HANG, 1 dong / don, gop 2 he thong nguon:
--   POS : tai quay (WALKIN) + don san Grab/Shopee duoc cua hang ghi nhan tren POS
--   App : app rieng (APP)
-- Trang thai chuan hoa: COMPLETED / VOIDED / REFUNDED / CANCELLED_BY_STORE / CANCELLED_BY_CUSTOMER.
-- Doanh thu thuan (net_sales) = tien mon sau giam gia, chi tinh don COMPLETED; khong gom phi giao hang.
-- is_prepared = bep da lam mon (COMPLETED hoac REFUNDED) -> dung tinh tieu hao dinh muc.
with pos as (
    select
        'POS:' || receipt_no                                              as order_key,
        'POS'                                                             as source_system,
        receipt_no                                                        as source_order_id,
        branch_id,
        business_date                                                     as date_day,
        txn_at                                                            as ordered_at_local,
        channel,
        order_type,
        cashier_staff_id,
        cast(null as varchar)                                             as customer_id,
        cast(null as boolean)                                             as is_first_order,
        case when is_void then 'VOIDED'
             when is_refund then 'REFUNDED'
             else 'COMPLETED' end                                         as order_status,
        cast(null as varchar)                                             as cancel_reason,
        payment_method,
        subtotal_amount                                                   as gross_sales,
        discount_amount,
        discount_code                                                     as promo_code,
        coalesce(refund_amount, 0)                                        as refund_amount,
        cast(0 as bigint)                                                 as delivery_fee,
        minutes_to_void,
        cast(null as double)                                              as prep_minutes,
        cast(null as integer)                                             as rating,
        n_lines
    from {{ ref('stg_pos__receipts') }}
),

app as (
    select
        'APP:' || order_id,
        'APP',
        order_id,
        branch_id,
        business_date,
        created_at_local,
        'APP',
        delivery_type,
        cast(null as integer),
        customer_id,
        is_first_order,
        case order_status when 'DELIVERED' then 'COMPLETED' else order_status end,
        cancel_reason,
        payment_method,
        subtotal_amount,
        promo_value,
        promo_code,
        case when order_status = 'REFUNDED' then subtotal_amount - promo_value else 0 end,
        delivery_fee,
        cast(null as double),
        prep_minutes,
        rating,
        n_lines
    from {{ ref('stg_app__orders') }}
),

unioned as (
    select * from pos
    union all
    select * from app
)

select
    u.order_key,
    u.source_system,
    u.source_order_id,
    u.branch_id,
    u.date_day,
    cast(strftime(u.date_day, '%Y%m%d') as integer)                       as date_key,
    u.ordered_at_local,
    hour(u.ordered_at_local)                                              as order_hour,
    case when hour(u.ordered_at_local) < 14 then 'SANG' else 'TOI' end   as shift_name,  -- ca toi vao ~13h40
    u.channel,
    u.order_type,
    u.cashier_staff_id,
    e.employee_sk                                                         as cashier_employee_sk,
    u.customer_id,
    u.is_first_order,
    u.order_status,
    u.cancel_reason,
    u.order_status = 'COMPLETED'                                          as is_completed,
    u.order_status in ('COMPLETED', 'REFUNDED')                           as is_prepared,
    u.payment_method,
    u.gross_sales,
    u.discount_amount,
    u.promo_code,
    case when u.order_status = 'COMPLETED' then u.gross_sales - u.discount_amount else 0 end as net_sales,
    u.refund_amount,
    u.delivery_fee,
    u.minutes_to_void,
    u.prep_minutes,
    u.rating,
    u.n_lines
from unioned u
left join {{ ref('dim_employee') }} e
    on e.staff_id = u.cashier_staff_id
   and u.date_day between e.valid_from and e.valid_to
