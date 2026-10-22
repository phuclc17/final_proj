-- Bang cach ly: moi dong du lieu bi loai o tang Silver, kem nguon, tep, so dong goc va ly do.
select 'pos_receipts' as source_table, _source_file, _row_number, receipt_no as record_key, dq_issue
from {{ ref('base_pos__receipts') }}
where dq_issue is not null

union all
select 'app_orders', _source_file, _row_number, order_id, dq_issue
from {{ ref('base_app__orders') }}
where dq_issue is not null

union all
select 'warehouse_receipts', _source_file, _row_number, raw_name || ' = ' || coalesce(raw_qty, '') || ' ' || coalesce(raw_unit, ''), dq_issue
from {{ ref('checked_inventory__receipts') }}
where dq_issue is not null

union all
select 'stock_counts', _source_file, _row_number, ingredient_code, dq_issue
from {{ ref('base_stock__counts') }}
where dq_issue is not null

union all
select 'timekeeping_punches', _source_file, _row_number, cast(staff_id as varchar) || ' ' || event_type, dq_issue
from {{ ref('base_timekeeping__punches') }}
where dq_issue is not null
