-- Doi soat so dong giua Bronze va Silver cho tung nguon:
--   so dong Bronze = so dong Silver hop le + so dong bi cach ly + so dong cau truc (dong tong cong, chu ky, tieu de)
-- Cot unexplained_rows phai bang 0; test assert_silver_rows_conserved kiem tra dieu nay.
with counts as (
    select 'pos_receipts' as source_table,
        (select count(*) from {{ source('bronze', 'pos_receipts') }})                                   as bronze_rows,
        (select count(*) from {{ ref('stg_pos__receipts') }})                                           as silver_rows,
        (select count(*) from {{ ref('base_pos__receipts') }} where dq_issue is not null)               as quarantined_rows,
        0                                                                                                as structural_rows
    union all
    select 'app_orders',
        (select count(*) from {{ source('bronze', 'app_orders') }}),
        (select count(*) from {{ ref('stg_app__orders') }}),
        (select count(*) from {{ ref('base_app__orders') }} where dq_issue is not null),
        0
    union all
    select 'shopee_settlement',
        (select count(*) from {{ source('bronze', 'shopee_settlement') }}),
        (select count(*) from {{ ref('stg_shopee__settlement') }}),
        0,
        0
    union all
    select 'warehouse_receipts',
        (select count(*) from {{ source('bronze', 'warehouse_receipts_form') }})
            + (select count(*) from {{ source('bronze', 'warehouse_receipts_table') }}),
        (select count(*) from {{ ref('stg_inventory__receipt_lines') }}),
        (select count(*) from {{ ref('checked_inventory__receipts') }} where dq_issue is not null),
        (select count(*) from {{ ref('base_inventory__receipts') }} where row_kind != 'data')
    union all
    select 'stock_counts',
        (select count(*) from {{ source('bronze', 'stock_counts') }}),
        (select count(*) from {{ ref('stg_stock__counts') }}),
        (select count(*) from {{ ref('base_stock__counts') }} where dq_issue is not null),
        (select count(*) from {{ ref('base_stock__counts') }} where not is_data_row)
    union all
    select 'timekeeping_punches',
        (select count(*) from {{ source('bronze', 'timekeeping_punches') }}),
        (select count(*) from {{ ref('stg_timekeeping__punches') }}),
        (select count(*) from {{ ref('base_timekeeping__punches') }} where dq_issue is not null),
        0
    union all
    select 'weather_daily',
        (select count(*) from {{ source('bronze', 'weather_daily') }}),
        (select count(*) from {{ ref('stg_weather__daily') }}),
        0,
        0
)

select
    *,
    bronze_rows - silver_rows - quarantined_rows - structural_rows as unexplained_rows,
    round(100.0 * quarantined_rows / nullif(bronze_rows - structural_rows, 0), 3) as pct_quarantined
from counts
