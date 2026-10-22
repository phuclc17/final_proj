-- Doi soat Silver -> Gold: doanh thu thuan trong fact_order phai bang dung tong tinh tu Silver
-- (POS: hoa don khong huy/khong hoan; App: don DELIVERED), theo tung chi nhanh x ngay.
with silver as (
    select branch_id, business_date as date_day, sum(subtotal_amount - discount_amount) as amt
    from {{ ref('stg_pos__receipts') }}
    where not is_void and not is_refund
    group by all
    union all
    select branch_id, business_date, sum(subtotal_amount - promo_value)
    from {{ ref('stg_app__orders') }}
    where order_status = 'DELIVERED'
    group by all
),

s as (select branch_id, date_day, sum(amt) as silver_amt from silver group by all),

g as (select branch_id, date_day, sum(net_sales) as gold_amt from {{ ref('fact_order') }} group by all)

select *
from s
full outer join g using (branch_id, date_day)
where coalesce(silver_amt, 0) <> coalesce(gold_amt, 0)
