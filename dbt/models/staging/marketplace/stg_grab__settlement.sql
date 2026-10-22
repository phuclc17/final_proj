-- Silver: bao cao doi soat GrabFood theo chi nhanh x tuan (CSV tieng Anh).
--   Ten cua hang tu do "Fast&Fat - District 3 (#1)" -> branch_id qua seed branch_code_map
--   Cot "week" dang "06/05/2024 - 12/05/2024"; ngay tao bao cao dang "14 May 2024"
--   Bao cao chi co SO TIEN hoa hong -> tu tinh ty le hieu dung de doi chieu hop dong (P1a)
with src as (
    select * from {{ source('bronze', 'grab_settlement') }}
)

select
    'GRABFOOD'                                                                       as platform,
    m.branch_id,
    cast(strptime(split_part(src.week, ' - ', 1), '%d/%m/%Y') as date)               as week_start,
    cast(strptime(split_part(src.week, ' - ', 2), '%d/%m/%Y') as date)               as week_end,
    cast(strptime(src.report_generated_date, '%d %b %Y') as date)                    as report_generated_date,
    cast(src.gross_sales as bigint)                                                  as gross_sales,
    cast(src.total_orders as integer)                                                as orders_completed,
    cast(src.cancelled_orders as integer)                                            as orders_cancelled,
    cast(src.total_commission as bigint)                                             as commission,
    cast(src.ads_spend as bigint)                                                    as ads_spend,
    cast(src.promotion_cost_borne_by_merchant as bigint)                             as merchant_promo,
    cast(src.adjustment_amount as bigint)                                            as adjustment,
    cast(src.net_payout as bigint)                                                   as net_payout,
    cast(src.average_prep_time_min as double)                                        as avg_prep_min,
    cast(src.store_rating as double)                                                 as store_rating,
    cast(src.total_commission as double) / nullif(cast(src.gross_sales as double), 0) as effective_commission_rate,
    src._source_file,
    src._row_number,
    src._batch_id
from src
left join {{ ref('branch_code_map') }} m on src.merchant_store_name = m.grab_store_name
