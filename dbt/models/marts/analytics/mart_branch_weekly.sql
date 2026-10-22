-- Gold mart: KPI theo CHI NHANH x TUAN (thu Hai -> Chu nhat), cong don tu mart ngay
-- + ghep bao cao doi soat san cung tuan:
--   pos_coverage    = don san cua hang ghi tren POS / don hoan thanh san bao cao  (P1b: don khong vao POS)
--   commission_gap  = ty le hoa hong hieu dung - ty le hop dong                   (P1a: thu sai hop dong)
-- n_days < 7 = tuan dang do dang (dau/cuoi du lieu), lop phan tich tu loai khi so sanh.
with w as (
    select
        branch_id,
        week_start,
        any_value(branch_name)                                       as branch_name,
        any_value(store_class)                                       as store_class,
        count(*)                                                     as n_days,
        count(*) filter (where is_holiday)                           as holiday_days,
        count(*) filter (where is_rain)                              as rain_days,
        sum(net_sales)                                               as net_sales,
        sum(orders)                                                  as orders,
        sum(gross_sales)                                             as gross_sales,
        sum(discount_amount)                                         as discount_amount,
        sum(discounted_orders)                                       as discounted_orders,
        {% for ch in ['walkin', 'app', 'grabfood', 'shopeefood'] %}
        sum(net_sales_{{ ch }})                                      as net_sales_{{ ch }},
        sum(orders_{{ ch }})                                         as orders_{{ ch }},
        {% endfor %}
        sum(orders_morning)                                          as orders_morning,
        sum(orders_evening)                                          as orders_evening,
        sum(pos_receipts_walkin)                                     as pos_receipts_walkin,
        sum(voids)                                                   as voids,
        sum(void_amount)                                             as void_amount,
        sum(pos_refunds)                                             as pos_refunds,
        sum(pos_refund_amount)                                       as pos_refund_amount,
        sum(app_orders_placed)                                       as app_orders_placed,
        sum(app_store_cancels)                                       as app_store_cancels,
        sum(app_customer_cancels)                                    as app_customer_cancels,
        sum(app_wait_cancels)                                        as app_wait_cancels,
        sum(app_prep_sum) / nullif(sum(app_prep_n), 0)               as app_avg_prep_min,
        sum(app_rating_sum) / nullif(sum(app_rating_n), 0)           as app_avg_rating,
        sum(cogs_standard)                                           as cogs_standard,
        sum(shifts)                                                  as shifts,
        sum(shifts_morning)                                          as shifts_morning,
        sum(shifts_evening)                                          as shifts_evening,
        sum(kitchen_morning)                                         as kitchen_morning,
        sum(kitchen_evening)                                         as kitchen_evening,
        sum(labor_hours)                                             as labor_hours,
        sum(labor_cost)                                              as labor_cost,
        sum(shifts_hours_imputed)                                    as shifts_hours_imputed
    from {{ ref('mart_branch_daily') }}
    group by branch_id, week_start
),

ms as (
    select
        branch_id,
        week_start,
        {% for p in ['GRABFOOD', 'SHOPEEFOOD'] %}
        {% set c = p | lower %}
        any_value(orders_completed) filter (where channel = '{{ p }}')           as {{ c }}_settled_orders,
        any_value(orders_cancelled) filter (where channel = '{{ p }}')           as {{ c }}_cancelled_orders,
        any_value(gross_sales) filter (where channel = '{{ p }}')                as {{ c }}_settled_gross,
        any_value(commission) filter (where channel = '{{ p }}')                 as {{ c }}_commission,
        any_value(net_payout) filter (where channel = '{{ p }}')                 as {{ c }}_net_payout,
        any_value(effective_commission_rate) filter (where channel = '{{ p }}')  as {{ c }}_effective_rate,
        any_value(contract_commission_rate) filter (where channel = '{{ p }}')   as {{ c }}_contract_rate,
        any_value(commission_rate_gap) filter (where channel = '{{ p }}')        as {{ c }}_commission_gap,
        any_value(commission_overcharge) filter (where channel = '{{ p }}')      as {{ c }}_commission_overcharge,
        any_value(avg_prep_min) filter (where channel = '{{ p }}')               as {{ c }}_avg_prep_min,
        any_value(store_rating) filter (where channel = '{{ p }}')               as {{ c }}_rating,
        {% endfor %}
    from {{ ref('fact_marketplace_settlement') }}
    group by all
)

select
    w.*,
    w.net_sales / nullif(w.orders, 0)                                       as aov,
    {% for ch in ['walkin', 'app', 'grabfood', 'shopeefood'] %}
    w.net_sales_{{ ch }} / nullif(w.orders_{{ ch }}, 0)                     as aov_{{ ch }},
    {% endfor %}
    w.cogs_standard / nullif(w.net_sales, 0)                                as cogs_pct,
    w.labor_cost / nullif(w.net_sales, 0)                                   as labor_pct,
    w.orders / nullif(w.labor_hours, 0)                                     as orders_per_labor_hour,
    w.orders_evening / nullif(w.shifts_evening, 0)                          as orders_per_evening_shift,
    w.voids / nullif(w.pos_receipts_walkin, 0)                              as void_rate,
    w.pos_refunds / nullif(w.pos_receipts_walkin, 0)                        as refund_rate,
    w.discount_amount / nullif(w.gross_sales, 0)                            as discount_rate,
    w.app_store_cancels / nullif(w.app_orders_placed, 0)                    as app_store_cancel_rate,
    w.app_wait_cancels / nullif(w.app_orders_placed, 0)                     as app_wait_cancel_rate,
    ms.* exclude (branch_id, week_start),
    w.orders_grabfood / nullif(ms.grabfood_settled_orders, 0)               as grabfood_pos_coverage,
    w.orders_shopeefood / nullif(ms.shopeefood_settled_orders, 0)           as shopeefood_pos_coverage
from w
left join ms using (branch_id, week_start)
