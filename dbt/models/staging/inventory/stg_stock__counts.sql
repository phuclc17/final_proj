-- Silver: ton thuc te theo chi nhanh x nguyen lieu x ky kiem ke. O bo trong giu la thieu so lieu (is_not_counted).
select
    branch_id || '-' || ingredient_id || '-' || count_date as count_key,
    branch_id,
    count_date,
    ingredient_id,
    counted_qty,
    is_not_counted,
    counted_by,
    _source_file,
    _row_number,
    _batch_id
from {{ ref('base_stock__counts') }}
where is_data_row and dq_issue is null
