-- Gold mart: hanh vi thu ngan theo NHAN VIEN x CHI NHANH x TUAN (cho P5 gian lan tai quay).
-- Chi xet hoa don tai quay (WALKIN) tren POS - noi thu ngan cam tien mat truc tiep.
-- Kem muc trung binh cua CAC THU NGAN KHAC cung chi nhanh cung tuan de so sanh (loai chinh nguoi do).
with r as (
    select
        o.branch_id,
        d.week_start,
        o.cashier_staff_id                                                    as staff_id,
        count(*)                                                              as receipts,
        count(*) filter (where o.order_status = 'VOIDED')                     as voids,
        count(*) filter (where o.order_status = 'VOIDED' and o.minutes_to_void <= 10) as quick_voids,
        coalesce(sum(o.gross_sales) filter (where o.order_status = 'VOIDED'), 0) as void_amount,
        count(*) filter (where o.order_status = 'VOIDED' and o.payment_method = 'CASH') as cash_voids,
        count(*) filter (where o.order_status = 'REFUNDED')                   as refunds,
        coalesce(sum(o.refund_amount), 0)                                     as refund_amount,
        count(*) filter (where o.discount_amount > 0)                         as discounted,
        coalesce(sum(o.discount_amount), 0)                                   as discount_amount,
        sum(o.gross_sales)                                                    as gross_sales
    from {{ ref('fact_order') }} o
    join {{ ref('dim_date') }} d using (date_day)
    where o.source_system = 'POS' and o.channel = 'WALKIN' and o.cashier_staff_id is not null
    group by all
),

branch as (
    select branch_id, week_start,
           sum(receipts) as b_receipts, sum(voids) as b_voids, sum(refunds) as b_refunds,
           sum(discounted) as b_discounted
    from r
    group by all
)

select
    r.*,
    e.staff_code,
    e.role,
    r.voids / r.receipts                                                       as void_rate,
    r.refunds / r.receipts                                                     as refund_rate,
    r.discounted / r.receipts                                                  as discount_rate,
    (b.b_voids - r.voids) / nullif(b.b_receipts - r.receipts, 0)               as others_void_rate,
    (b.b_refunds - r.refunds) / nullif(b.b_receipts - r.receipts, 0)           as others_refund_rate,
    (b.b_discounted - r.discounted) / nullif(b.b_receipts - r.receipts, 0)     as others_discount_rate
from r
join branch b using (branch_id, week_start)
left join {{ ref('dim_employee') }} e
    on e.staff_id = r.staff_id
   and r.week_start between e.valid_from and e.valid_to
