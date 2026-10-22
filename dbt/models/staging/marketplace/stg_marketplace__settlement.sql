-- Silver: hop nhat doi soat GrabFood + ShopeeFood ve 1 cau truc, kem ty le hoa hong theo hop dong co hieu luc.
-- Day la dau vao cho phat hien P1a (hoa hong sai hop dong) va P1b (don san khong vao POS).
with unioned as (
    select platform, branch_id, week_start, week_end, report_generated_date, gross_sales, orders_completed,
           orders_cancelled, commission, ads_spend, merchant_promo, adjustment, net_payout, avg_prep_min,
           store_rating, effective_commission_rate, _source_file, _row_number
    from {{ ref('stg_grab__settlement') }}
    union all
    select platform, branch_id, week_start, week_end, report_generated_date, gross_sales, orders_completed,
           orders_cancelled, commission, ads_spend, merchant_promo, adjustment, net_payout, avg_prep_min,
           store_rating, effective_commission_rate, _source_file, _row_number
    from {{ ref('stg_shopee__settlement') }}
)

select
    u.platform || '-' || u.branch_id || '-' || u.week_start                 as settlement_key,
    u.*,
    c.contract_commission_rate,
    u.effective_commission_rate - c.contract_commission_rate               as commission_rate_gap
from unioned u
left join {{ ref('stg_master__marketplace_contracts') }} c
    on u.branch_id = c.branch_id and u.platform = c.platform and u.week_start >= c.effective_from
qualify row_number() over (partition by u.platform, u.branch_id, u.week_start order by c.effective_from desc) = 1
