-- Gold mart: KPI van hanh theo CHI NHANH x NGAY. Moi chi nhanh co du moi ngay (ngay khong co don = 0).
-- Cay KPI: doanh thu = tong theo kenh; doanh thu kenh = so don x gia tri don binh quan (AOV).
-- Kenh san: so don/doanh thu o day la phan CUA HANG GHI NHAN tren POS; so lieu san bao cao nam o mart tuan.
with grid as (
    select d.date_day, d.week_start, d.is_weekend, d.is_holiday, d.holiday_name, d.is_rain, d.precipitation_mm,
           b.branch_id, b.branch_name, b.store_class
    from {{ ref('dim_date') }} d
    cross join {{ ref('dim_branch') }} b
),

o as (
    select
        branch_id,
        date_day,
        sum(net_sales)                                                                   as net_sales,
        count(*) filter (where is_completed)                                             as orders,
        sum(gross_sales) filter (where is_completed)                                     as gross_sales,
        sum(discount_amount) filter (where is_completed)                                 as discount_amount,
        count(*) filter (where is_completed and discount_amount > 0)                     as discounted_orders,
        {% for ch in ['WALKIN', 'APP', 'GRABFOOD', 'SHOPEEFOOD'] %}
        coalesce(sum(net_sales) filter (where channel = '{{ ch }}'), 0)                  as net_sales_{{ ch | lower }},
        count(*) filter (where is_completed and channel = '{{ ch }}')                    as orders_{{ ch | lower }},
        {% endfor %}
        count(*) filter (where is_completed and shift_name = 'TOI')                      as orders_evening,
        count(*) filter (where is_completed and shift_name = 'SANG')                     as orders_morning,
        count(*) filter (where source_system = 'POS' and channel = 'WALKIN')             as pos_receipts_walkin,
        count(*) filter (where order_status = 'VOIDED')                                  as voids,
        coalesce(sum(gross_sales) filter (where order_status = 'VOIDED'), 0)             as void_amount,
        count(*) filter (where order_status = 'REFUNDED' and channel = 'WALKIN')         as pos_refunds,
        coalesce(sum(refund_amount) filter (where channel = 'WALKIN'), 0)                as pos_refund_amount,
        count(*) filter (where channel = 'APP')                                          as app_orders_placed,
        count(*) filter (where order_status = 'CANCELLED_BY_STORE')                      as app_store_cancels,
        count(*) filter (where order_status = 'CANCELLED_BY_CUSTOMER')                   as app_customer_cancels,
        count(*) filter (where cancel_reason = 'WAITING_TOO_LONG')                       as app_wait_cancels,
        avg(prep_minutes) filter (where channel = 'APP')                                 as app_avg_prep_min,
        sum(prep_minutes) filter (where channel = 'APP')                                 as app_prep_sum,
        count(prep_minutes) filter (where channel = 'APP')                               as app_prep_n,
        sum(rating) filter (where channel = 'APP')                                       as app_rating_sum,
        count(rating) filter (where channel = 'APP')                                     as app_rating_n
    from {{ ref('fact_order') }}
    group by all
),

l as (
    select branch_id, date_day, sum(cogs_standard) as cogs_standard
    from {{ ref('fact_order_line') }}
    group by all
),

s as (
    select
        branch_id,
        date_day,
        count(*)                                                         as shifts,
        count(*) filter (where shift_name = 'SANG')                      as shifts_morning,
        count(*) filter (where shift_name = 'TOI')                       as shifts_evening,
        count(*) filter (where shift_name = 'TOI' and role = 'Kitchen')  as kitchen_evening,
        count(*) filter (where shift_name = 'SANG' and role = 'Kitchen') as kitchen_morning,
        sum(hours_paid)                                                  as labor_hours,
        sum(labor_cost)                                                  as labor_cost,
        count(*) filter (where is_hours_imputed)                         as shifts_hours_imputed
    from {{ ref('fact_labor_shift') }}
    group by all
)

select
    g.*,
    coalesce(o.net_sales, 0)                                  as net_sales,
    coalesce(o.orders, 0)                                     as orders,
    o.net_sales / nullif(o.orders, 0)                         as aov,
    coalesce(o.gross_sales, 0)                                as gross_sales,
    coalesce(o.discount_amount, 0)                            as discount_amount,
    coalesce(o.discounted_orders, 0)                          as discounted_orders,
    {% for ch in ['walkin', 'app', 'grabfood', 'shopeefood'] %}
    coalesce(o.net_sales_{{ ch }}, 0)                         as net_sales_{{ ch }},
    coalesce(o.orders_{{ ch }}, 0)                            as orders_{{ ch }},
    {% endfor %}
    coalesce(o.orders_morning, 0)                             as orders_morning,
    coalesce(o.orders_evening, 0)                             as orders_evening,
    coalesce(o.pos_receipts_walkin, 0)                        as pos_receipts_walkin,
    coalesce(o.voids, 0)                                      as voids,
    coalesce(o.void_amount, 0)                                as void_amount,
    coalesce(o.pos_refunds, 0)                                as pos_refunds,
    coalesce(o.pos_refund_amount, 0)                          as pos_refund_amount,
    coalesce(o.app_orders_placed, 0)                          as app_orders_placed,
    coalesce(o.app_store_cancels, 0)                          as app_store_cancels,
    coalesce(o.app_customer_cancels, 0)                       as app_customer_cancels,
    coalesce(o.app_wait_cancels, 0)                           as app_wait_cancels,
    o.app_avg_prep_min,
    coalesce(o.app_prep_sum, 0)                               as app_prep_sum,
    coalesce(o.app_prep_n, 0)                                 as app_prep_n,
    coalesce(o.app_rating_sum, 0)                             as app_rating_sum,
    coalesce(o.app_rating_n, 0)                               as app_rating_n,
    coalesce(l.cogs_standard, 0)                              as cogs_standard,
    l.cogs_standard / nullif(o.net_sales, 0)                  as cogs_pct,
    coalesce(s.shifts, 0)                                     as shifts,
    coalesce(s.shifts_morning, 0)                             as shifts_morning,
    coalesce(s.shifts_evening, 0)                             as shifts_evening,
    coalesce(s.kitchen_morning, 0)                            as kitchen_morning,
    coalesce(s.kitchen_evening, 0)                            as kitchen_evening,
    coalesce(s.labor_hours, 0)                                as labor_hours,
    coalesce(s.labor_cost, 0)                                 as labor_cost,
    coalesce(s.shifts_hours_imputed, 0)                       as shifts_hours_imputed,
    s.labor_cost / nullif(o.net_sales, 0)                     as labor_pct,
    o.orders / nullif(s.labor_hours, 0)                       as orders_per_labor_hour
from grid g
left join o using (branch_id, date_day)
left join l using (branch_id, date_day)
left join s using (branch_id, date_day)
