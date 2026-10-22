-- Gold: bang su kien DOI SOAT SAN, 1 dong / san / chi nhanh / tuan.
-- Gom ty le hoa hong hop dong (tai thoi diem) va chenh lech so voi ty le hieu dung tren bao cao.
select
    settlement_key,
    platform                                    as channel,
    branch_id,
    week_start,
    week_end,
    report_generated_date,
    gross_sales,
    orders_completed,
    orders_cancelled,
    commission,
    ads_spend,
    merchant_promo,
    adjustment,
    net_payout,
    avg_prep_min,
    store_rating,
    effective_commission_rate,
    contract_commission_rate,
    commission_rate_gap,
    round(commission_rate_gap * gross_sales)    as commission_overcharge
from {{ ref('stg_marketplace__settlement') }}
